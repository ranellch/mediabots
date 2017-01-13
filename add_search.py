#script to add new search to searchlookup collection in mongodb
from pymongo import *
from configparser import ConfigParser

config = ConfigParser()
config.read('./bot.config')


client = MongoClient('ec2-35-164-223-57.us-west-2.compute.amazonaws.com',27017)
db = client.Searches
db.authenticate(config['MongoDB']['search_user'], config['MongoDB']['search_pwd'])
# 
collection = db.searchlookup 
# search = {"_id":1,             
#           "since_id":0,
#           "keywords":["beer"],
#           "location":"austin"
#           "collection":"AustinBeer"}
# collection.insert_one(search)
# for doc in collection.find():
#    print(doc)
# 
# #collection.remove({"_id":1})
# for doc in collection.find():
#     print(doc)
#     print(type(doc))
    

collection.find_one_and_update(
    {'_id': 0}, {'$set': {'collection': 'AustinBeer'}})
for doc in collection.find():
    print(doc)

