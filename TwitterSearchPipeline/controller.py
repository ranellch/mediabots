from TwitterSearch import *
import time
from configparser import ConfigParser

config = ConfigParser()
config.read('../bot.config')

# it's about time to create a TwitterSearch object with our secret tokens
# information from C.Ranella botnet1 app on twitter (he has actual access but these codes will work)



class TwitterSearchQuery:
    def __init__(self, ts, dict, dbKey):
        self.ts = ts
        self.tso = TwitterSearchOrder()
        self.last_max_id = 0
        self.dbKey = dbKey
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
            print("Tsq",self.dbKey,"complete")
            print("Queries remaining in current window: ",meta['x-rate-limit-remaining'])
            print("Time remaining: ",int(secs/60),"min ",secs%60,"sec")
        except TwitterSearchException as e:
            if e.code == 429: #if query hit rate limit print remaining time in window
                reset_time = int(ts.get_metadata()['x-rate-limit-reset'])
                secs = reset_time-int(time.time())
                #raise here maybe
                print("Rate limit met by tsq",self.dbKey, "- must wait for ",int(secs/60),"min ",secs%60,"sec")
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
        self.tsqList.append(TwitterSearchQuery(self.ts, dictInput, 0))
    
    # debug function
    def basicSearchAll(self):
        self._updateQueriesAllowed()
        for tsq in self.tsqList:
            if tsq.queriesAllowed == 0:
                print("Not enough queries remaining")
                break
            tsq.performSearch()
            
    # debug function
    def basicSearch(self, dbKey):
        tsq = self._findTsqFromDbKey(dbKey)
        if (tsq):
            tsq.performSearch()
        
    # debug function
    def getBasicSearchParameters(self, dbKey):
        tsq = self._findTsqFromDbKey(dbKey)
        if (tsq):
            return tsq.getCurrentSearchURL()
        else:
            None
    
    # debug function
    def firstTweet(self, dbKey):
        tsq = self._findTsqFromDbKey(dbKey)
        if (tsq):
            return tsq.buffer[0]
            
    def _findTsqFromDbKey(self, dbKey):
        for tsq in self.tsqList:
            if (tsq.dbKey == dbKey):
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
            

        
rController = RestController(config)

# Replace temp Dict with read from database
tempDict = {'keywords' : ['beer'], 'location' : ['austin']}

# add a new search query to the controller
rController.addNewTsqFromDatabaseDictionary(tempDict);

rController.basicSearchAll()

#print(ts.get_metadata())
print(rController.getBasicSearchParameters(0))
print(rController.firstTweet(0))
        