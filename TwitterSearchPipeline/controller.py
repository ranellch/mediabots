from TwitterSearch import *
from time import sleep
from configparser import ConfigParser

config = ConfigParser()
config.read('../bot.config')

# it's about time to create a TwitterSearch object with our secret tokens
# information from C.Ranella botnet1 app on twitter (he has actual access but these codes will work)
ts = TwitterSearch(
    consumer_key = config['TwitterAuth']['consumer_key'],
    consumer_secret = config['TwitterAuth']['consumer_secret'],
    access_token = config['TwitterAuth']['access_token'],
    access_token_secret = config['TwitterAuth']['access_token_secret']
)

tso = TwitterSearchOrder()

class TwitterSearchQuery:
    def __init__(self, ts, tso):
        self.ts = ts
        self.tso = tso
    
    def setBasicSearchParameters(self, keywordList):
        self.tso.remove_all_filters()
        self.tso.set_keywords(keywordList) # let's define all words we would like to have a look for
        self.tso.set_language('en') # we want to see English tweets only
        self.tso.set_include_entities(False) # and don't give us all those entity information
        self.tso.set_count(100)
        
    def getCurrentSearchURL(self):
        return self.tso.create_search_url()
        
    def performSearch(self, buffer):
        buffer.clear()
        count = 0
        for tweet in ts.search_tweets_iterable(self.tso):
            buffer.append(tweet)
            print (count)
            count += 1
        
        # Make this better. For now sleep every 60 seconds
        #sleep(60)            
        
        

tsq = TwitterSearchQuery(ts, tso)
        
    
#Start of controller
#-----
class RestController:
    def __init__(self, tsq):
        self.buffer = ['default']
        self.tsq = tsq
        self.writer = []
        
    def basicSearch(self, keywordList):
        self.tsq.setBasicSearchParameters(keywordList)
        self.tsq.performSearch(self.buffer)
        
    def getBasicSearchParameters(self):
        return self.tsq.getCurrentSearchURL()
    
    def firstTweet(self):
        if (self.buffer):
            return self.buffer[0]
        
        

        
rController = RestController(tsq)

keywords = ['beer']
rController.basicSearch(keywords)

print(rController.getBasicSearchParameters())
print(rController.firstTweet().encode('utf-8'))
        