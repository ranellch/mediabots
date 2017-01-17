from .SearchParameters import SearchParameters
from pymongo import *

class SearchDBController:
    def __init__(self, config):
        self.config = config
        client = MongoClient(config['AWS']['server'],int(config['AWS']['DBport']))
        self.db = client.Searches
        self.db.authenticate(config['MongoDB']['search_user'], config['MongoDB']['search_pwd'])
        self.search_lookup_collection = self.db["searchlookup"] # collection that represents a table of all search parameters

    def readSearchParamsFromCollectionName(self, collection_name):
        searchParams = self.search_lookup_collection.find_one({"collection":collection_name})
        return searchParams

    def writeTweets(self, collection_name, tweet_buffer):
        collection = self.db[collection_name]
        collection.insert_many(tweet_buffer)

    def writeSinceId(self, collection_name, since_id):
        self.search_lookup_collection.update({'collection':collection_name},{"$set":{'since_id':since_id}})

    # better policy needed to force unique collection, all keys really
    def addSearchParams(self, searchParams):
        if not (searchParams.searchParametersReady()):
            print("Search parameters not ready")
            return

        params = searchParams.getDict()

        if (params['collection'] in self.db.collection_names() or
                bool(self.search_lookup_collection.find_one({'collection': params['collection']}))):
            print("Collection name not unique")
            return

        self.search_lookup_collection.insert_one(params)

    def getAllCollectionNames(self):
        return self.db.collection_names()

    def getDocumentCountFromCollectionName(self,collection_name):
        return self.db[collection_name].count()

    #debug function
    def readFirstTweet(self,collection_name):
        if (collection_name in self.db.collection_names()):
            collection = self.db[collection_name]
            return collection.find_one()
        else:
            return None

    #WARNING -- clears all tweets in collection!!!!
    def clearCollection(self,collection_name):
        print (collection_name)
        ans = input("Clear collection? Y/N \n").strip().lower()
        if (ans=='y'):
            self.db[collection_name].delete_many({})

    def dropCollection(self, collection_name):
        print (collection_name)
        ans = input("Drop collection? Y/N \n").strip().lower()
        if (ans=='y'):
            self.db[collection_name].drop()
