from TwitterSearch import *
from .TwitterSearchQuery import TwitterSearchQuery
from .SearchParameters import SearchParameters
from .SearchDBController import SearchDBController

class RestController:
    def __init__(self, config):
        self.config = config
        self.ts = TwitterSearch(
            consumer_key = config['TwitterAuth']['consumer_key'],
            consumer_secret = config['TwitterAuth']['consumer_secret'],
            access_token = config['TwitterAuth']['access_token'],
            access_token_secret = config['TwitterAuth']['access_token_secret'])
        self.searchParametersLog = []
        self.tsqList = []
        self.DBController = SearchDBController(config)
       
      
    #---Main public methods----    
    def addNewSearchParams(self, searchParams):
        # if search parameters are unique and complete, add them to the database search controller
        self.DBController.addSearchParams(searchParams)
        
    def basicSearch(self,collection_names):
        self._clearTsqList()
        self._readParamsFromDatabase(collection_names)
        self._updateQueriesAllowed()
        for tsq in self.tsqList:
            if tsq.queriesAllowed == 0:
                self.searchParametersLog.append("Failure") 
                print("Not enough queries remaining")
                break
            try:
                tsq.performSearch()
                self._moveResultsToDatabase(tsq)
            except TwitterSearchException as e:
                self.searchParametersLog.append("TwitterSearch Failure")
                self.writeSearchLog('./')
                raise e
            except:
                self.searchParametersLog.append("Write Failure")
                self.writeSearchLog('./')
                raise
            self.searchParametersLog.append("Success: %d Tweets Written" % len(tsq.buffer)) 
                   
    #---Debug methods----         
    def getTweetsFromCollection(self, collection_name):
        tsq = self._findTsqFromCollectionName(collection_name)
        return tsq.buffer
                     
    def firstTweetFromCollectionName(self, collection_name):
        tsq = self._findTsqFromCollectionName(collection_name)
        if (tsq):
            return tsq.buffer[0]
            
    def clearDBCollections(self):
        for col in self.DBController.getAllCollectionNames():
            if(col == "searchlookup"):
                self.DBController.clearCollection(col)
            else:
                self.DBController.dropCollection(col)
                
    def writeSearchLog(self,path):
        with open(path+'searches.log', mode='wt', encoding='utf-8') as logfile:
             logfile.write('\n'.join(str(entry) for entry in self.searchParametersLog))         
     
    #---Private methods----                        
    def _readParamsFromDatabase(self, collection_names):   
        # add the unique twitter search from database
        for name in collection_names:
            params = self.DBController.readSearchParamsFromCollectionName(name)
            self.searchParametersLog.append(params)
            self.tsqList.append(TwitterSearchQuery(self.ts, params))
       
    def _moveResultsToDatabase(self, tsq):
        if (tsq.buffer):
            self.DBController.writeTweets(tsq.collection_name, tsq.buffer)
            self.DBController.writeSinceId(tsq.collection_name, tsq.getSinceId())
    
    def _clearTsqList(self):
        self.tsqList = []

        
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
            
            