from TwitterSearch import *
import time

class TwitterSearchQuery:
    def __init__(self, ts, paramsDict):
        self.ts = ts
        self.tso = TwitterSearchOrder()
        self.last_max_id = 0
        self.collection_name = paramsDict['collection']
        self.tso.remove_all_filters()
        self.tso.set_language('en')
        self.tso.set_include_entities(False)
        self.tso.set_count(100)
        self.buffer = ['default']
        self.queriesAllowed = 10

        for key in paramsDict.keys():
            if (key == "keywords"):
                self.tso.set_keywords(paramsDict[key], or_operator = True)
            if (key == "since_id"):
                self.setSinceId(paramsDict[key])
            if (key == "geocode"):
                self.tso.set_geocode(paramsDict[key]['lat'],paramsDict[key]['lon'],
                                        paramsDict[key]['rad'],imperial_metric=False)
            # add more parameters here...create a global resource for all possible parameters

    def setSinceId(self, last_max_id):
        self.last_max_id = last_max_id
        self.tso.set_since_id(last_max_id)

    def getSinceId(self):
        return self.last_max_id

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
                raise
