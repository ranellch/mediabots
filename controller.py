#!/home/ubuntu/.virtualenvs/mediabots/bin/python3
from TwitterSearchPipeline import RestController
from configparser import ConfigParser
import os

config = ConfigParser()
config.read('bot.config')

try:
    os.remove("searches.log")
except OSError:
    pass

scheduler = PeriodicScheduler()
rController = RestController(config)

collectionNames = ["AustinBeer", "AustinLiveMusic", "AustinHiking", "AustinCoffeeShops"]

def rControllerRunner(collection_names, logPath):
    rController.basicSearch(collection_names)
    rController.writeSearchLog(logPath)

rControllerRunner(collectionNames, './')
# args = (collectionNames, './')
# scheduler.scheduleTaskInSeconds(60, rControllerRunner, *args)
# scheduler.executeTaskLoop()

# rController.basicSearch(collectionNames)
#
# # Test that our Database and our Tsq Buffers are the same
# tweetFromController = rController.firstTweetFromCollectionName(collectionName)
# tweetFromDB = rController.DBController.readFirstTweet(collectionName)
# print (tweetFromController == tweetFromDB)
#
# tweetFromController = rController.firstTweetFromCollectionName(collectionName2)
# tweetFromDB = rController.DBController.readFirstTweet(collectionName2)
# print (tweetFromController == tweetFromDB)


# rController.basicSearch([collectionName])
# rController.writeSearchLog('./')

# print(rController.DBController.readFirstTweet("AustinLiveMusic"))
