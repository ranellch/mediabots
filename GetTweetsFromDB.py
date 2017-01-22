from configparser import ConfigParser
from pymongo import *

config = ConfigParser()
config.read('bot.config')

collectionNames = ["AustinBeer", "AustinLiveMusic", "AustinHiking", "AustinCoffeeShops"]

client = MongoClient(config['AWS']['server'],int(config['AWS']['DBport']))
db = client.Searches
db.authenticate(config['MongoDB']['search_user'], config['MongoDB']['search_pwd'])

for collection in collectionNames:
    tweets = db[collection].find({},{'text':1})
    with open(collection+'.tweets', mode='w', encoding='utf-8') as tweetfile:
         tweetfile.write('\n'.join(str(tweet) for tweet in tweets))
