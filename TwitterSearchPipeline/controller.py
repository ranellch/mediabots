from TwitterSearch import *
import time
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
        try:
            for tweet in ts.search_tweets_iterable(self.tso):
                buffer.append(tweet)
            meta = ts.get_metadata()
            reset_time = int(meta['x-rate-limit-reset'])
            secs = reset_time-int(time.time())
            print("Queries remaining in current window: ",meta['x-rate-limit-remaining'])
            print("Time remaining: ",int(secs/60),"min ",secs%60,"sec")
        except TwitterSearchException as e:
            if e.code == 429: #if query hit rate limit sleep for remaining time in window
                reset_time = int(ts.get_metadata()['x-rate-limit-reset'])
                secs = reset_time-int(time.time())
                #raise here maybe
                print("Rate limit met - sleeping for ",int(secs/60),"min ",secs%60,"sec") #look into threads later
                time.sleep(secs)
            else:
                print("Exception: %i - %s" % (e.code, e.message))
                   

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

print(ts.get_metadata())
print(rController.getBasicSearchParameters())
print(rController.firstTweet())
        