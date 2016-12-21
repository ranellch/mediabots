from TwitterSearch import *
import time
from configparser import ConfigParser
from pymongo import *
import sys

config = ConfigParser()
config.read('../bot.config')

# it's about time to create a TwitterSearch object with our secret tokens
# information from C.Ranella botnet1 app on twitter (he has actual access but these codes will work)



class TwitterSearchQuery:
    def __init__(self, ts, dict):
        self.ts = ts
        self.tso = TwitterSearchOrder()
        self.last_max_id = 0
        self.collection_name = dict['collection']
        self.tso.remove_all_filters()
        self.tso.set_language('en')
        self.tso.set_include_entities(False)
        self.tso.set_count(100)
        self.buffer = ['default']
        self.queriesAllowed = 10
        
        for key in dict.keys():
            if (key == "keywords"):
                self.tso.set_keywords(dict["keywords"])
            # add more parameters here...create a global resource for all possible parameters

    def setSinceId(self, last_max_id):
        self.last_max_id = last_max_id
        self.tso.set_since_id(last_max_id)
        
    def getCurrentSearchURL(self):
        return self.tso.create_search_url()  
        
    def performSearch(self):
        self.buffer.clear()
        try:
            start = True
            count = 0
            for tweet in self.ts.search_tweets_iterable(self.tso):
                self.buffer.append(tweet)
                current_amount_of_queries = self.ts.get_statistics()[0] #get current number of queries
                if start:
                    self.setSinceId(tweet['id']) #get max tweet id for next searches
                    start = False
                if current_amount_of_queries == self.queriesAllowed:
                    count += 1
                    tweets_available = self.ts.get_amount_of_tweets()
                    if count == tweets_available:
                        break
            meta = self.ts.get_metadata()
            reset_time = int(meta['x-rate-limit-reset'])
            secs = reset_time-int(time.time())
            print("Tsq",self.collection_name,"complete")
            print("Queries remaining in current window: ",meta['x-rate-limit-remaining'])
            print("Time remaining: ",int(secs/60),"min ",secs%60,"sec")
        except TwitterSearchException as e:
            if e.code == 429: #if query hit rate limit print remaining time in window
                reset_time = int(ts.get_metadata()['x-rate-limit-reset'])
                secs = reset_time-int(time.time())
                #raise here maybe
                print("Rate limit met by tsq",self.collection_name, "- must wait for ",int(secs/60),"min ",secs%60,"sec")
                raise e
            else:
                raise e

#Start of controller
#-----
class RestController:
    def __init__(self, config):
        self.config = config
        self.ts = TwitterSearch(
            consumer_key = config['TwitterAuth']['consumer_key'],
            consumer_secret = config['TwitterAuth']['consumer_secret'],
            access_token = config['TwitterAuth']['access_token'],
            access_token_secret = config['TwitterAuth']['access_token_secret'])
        self.writerList = []
        self.tsqList = []
        
    def addNewTsqFromDatabaseDictionary(self, dictInput):
        self.tsqList.append(TwitterSearchQuery(self.ts, dictInput))
        
    def getTweetsFromCollection(self, collection_name):
        tsq = self._findTsqFromCollectionName(collection_name)
        return tsq.buffer
    
    # debug function
    def basicSearchAll(self):
        self._updateQueriesAllowed()
        for tsq in self.tsqList:
            if tsq.queriesAllowed == 0:
                print("Not enough queries remaining")
                break
            tsq.performSearch()
            
    # debug function
    def basicSearch(self, collection_name):
        tsq = self._findTsqFromCollectionName(collection_name)
        if (tsq):
            tsq.performSearch()
            
    def firstTweetFromCollectionName(self, collection_name):
        tsq = self._findTsqFromCollectionName(collection_name)
        if (tsq):
            return tsq.buffer[0]
        
    def _findTsqFromCollectionName(self, collection_name):
        for tsq in self.tsqList:
            if (tsq.collection_name == collection_name):
                return tsq
        return None
    
    def _updateQueriesAllowed(self):
        for tsq in self.tsqList:
            try:
                tsq.queriesAllowed = int(self.ts.get_metadata()['x-rate-limit-remaining']) / len(self.tsqList)
            except TwitterSearchException as e:
                if (e.code == 1012):
                    tsq.queriesAllowed = 180 / len(self.tsqList)
                else:
                    raise e
                    
            # remove this when we are done experimenting
            tsq.queriesAllowed /= 10

class SearchDBController:
    def __init__(self,config):
        self.config = config    
        client = MongoClient(config['AWS']['server'],int(config['AWS']['DBport']))
        self.db = client.Searches
        self.db.authenticate(config['MongoDB']['search_user'], config['MongoDB']['search_pwd']) 
        
    def readSearchParamsFromCollectionName(self, collection_name):
        collection = self.db.searchlookup
        searchParams = collection.find_one({"collection":collection_name})
        return searchParams
        
    def writeTweets(self,collection_name,tweet_buffer):
        collection = self.db[collection_name]
        collection.insert_many(tweet_buffer)
    
    # better policy needed to force unique collection, all keys really
    def addSearchParams(self, searchParams):
        if not (searchParams.searchParametersReady()):
            print("Search parameters not ready")
            return None
        
        params = searchParams.getDict()
        
        if (params['collection'] in self.db.collection_names()):
            print("Collection name not unique")
            return None
            
        collection = self.db.searchlookup
        collection.insert_one(params)
    
    def getAllCollectionNames(self):
        return self.db.collection_names()
         
    
    #debug function
    def readFirstTweet(self,collection_name):
        if (collection_name in self.db.collection_names()):
            collection = self.db[collection_name]
            return collection.find_one()
        else:
            return None
    
    #WARNING -- deletes all tweets in collection!!!!        
    def clearCollection(self,collection_name):
        ans = input("Delete all? Y/N \n").strip().lower()
        if (ans=='y'):
            self.db[collection_name].delete_many({})
            
class SearchParameters:
    def __init__(self):
        self.dict = {}
        self.requiredAttributes = ['collection', 'since_id', 'keywords']
        for attr in self.requiredAttributes:
            self.dict[attr] = None
    
    def addKeywords(self, keywordList):
        self.dict['keywords'] = keywordList
        
    def addLocation(self, location):
        self.dict['location'] = location
    
    def addCollectionName(self, collection_name):
        self.dict['collection'] = collection_name
    
    def addSinceId(self, since_id):
        self.dict['since_id'] = since_id
    
    def searchParametersReady(self):
        ready = True
        for attr in self.requiredAttributes:
            if not (attr):
                ready = False
                break         
        return ready
    
    def getDict(self):
        return self.dict
    
    def getCollectionName(self):
        return self.dict['collection']
        
        
sController = SearchDBController(config)

# TODO: remove collections, not just clear
for col in sController.getAllCollectionNames():
    sController.clearCollection(col)
            
rController = RestController(config)

#Construct a search params
collectionName = "AustinBeer5"
params = SearchParameters()
params.addKeywords(['beer'])
params.addLocation('austin')
params.addCollectionName(collectionName)
params.addSinceId(0)

sController.addSearchParams(params)
print(sController.readSearchParamsFromCollectionName(collectionName))

# add a new search query to the controller
rController.addNewTsqFromDatabaseDictionary(sController.readSearchParamsFromCollectionName(collectionName));
print("added tsq")

rController.basicSearchAll()

# put in database
sController.writeTweets(collectionName, rController.getTweetsFromCollection(collectionName))
print("wrote tweets")

tweetFromController = rController.firstTweetFromCollectionName(collectionName)
tweetFromDB = sController.readFirstTweet(collectionName)
print("comparing first tweets")

print (tweetFromController == tweetFromDB)

        