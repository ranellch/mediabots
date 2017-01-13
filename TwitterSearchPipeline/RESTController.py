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
        self.databaseParametersSoftCopy = []
        self.tsqList = []
        self.DBController = SearchDBController(config)
       
      
        
    def addNewSearchParams(self, searchParams):
        # if search parameters are unique and complete, add them to the database search controller
        self.DBController.addSearchParams(searchParams)
        
    def _readParamsFromDatabase(self, collection_names):   
        # add the unique twitter search from database
        self._clearTsqList()
        for name in collection_names:
            params = self.DBController.readSearchParamsFromCollectionName(name)
            self.databaseParametersSoftCopy.append(params)
            self.tsqList.append(TwitterSearchQuery(self.ts, params))
    
    # debug function            
    def getTweetsFromCollection(self, collection_name):
        tsq = self._findTsqFromCollectionName(collection_name)
        return tsq.buffer
        
    def _moveResultsToDatabase(self, tsq):
        if (tsq.buffer):
            self.DBController.writeTweets(tsq.collection_name, tsq.buffer)
            self.DBController.writeSinceId(tsq.collection_name, tsq.getSinceId())
    
    def _clearTsqList(self):
        self.tsqList = []
        
    # main function
    def basicSearch(self,collection_names):
        self._readParamsFromDatabase(collection_names)
        self._updateQueriesAllowed()
        for tsq in self.tsqList:
            if tsq.queriesAllowed == 0:
                print("Not enough queries remaining")
                break
            tsq.performSearch()
            self._moveResultsToDatabase(tsq)
            
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
    
    # debug function
    def clearDBCollections(self):
        for col in self.DBController.getAllCollectionNames():
            if(col == "searchlookup"):
                self.DBController.clearCollection(col)
            else:
                self.DBController.dropCollection(col)
            
            