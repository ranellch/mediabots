from TwitterSearchPipeline import RestController
from TwitterSearchPipeline import SearchParameters
from configparser import ConfigParser
import os

config = ConfigParser()
config.read('bot.config')

# it's about time to create a TwitterSearch object with our secret tokens
# information from C.Ranella botnet1 app on twitter (he has actual access but these codes will work)


#Start of controller
#-----





rController = RestController(config)

rController.clearDBCollections()

print(rController.DBController.getAllCollectionNames())

# Construct a search params
# TODO: make locations work
collectionName = "AustinBeer"
params = SearchParameters()
params.addKeywords(['beer'])
params.addLocation('Austin Texas', 50)
params.addCollectionName(collectionName)
rController.addNewSearchParams(params)

collectionName2 = "AustinLiveMusic"
params = SearchParameters()
params.addKeywords(['Live', 'Music'])
params.addLocation('Austin Texas',50)
params.addCollectionName(collectionName2)
rController.addNewSearchParams(params)

collectionNames = [collectionName, collectionName2]


rController.basicSearch(collectionNames)

# Test that our Database and our Tsq Buffers are the same
tweetFromController = rController.firstTweetFromCollectionName(collectionName)
tweetFromDB = rController.DBController.readFirstTweet(collectionName)
print (tweetFromController == tweetFromDB)

tweetFromController = rController.firstTweetFromCollectionName(collectionName2)
tweetFromDB = rController.DBController.readFirstTweet(collectionName2)
print (tweetFromController == tweetFromDB)

os.remove("searches.log")
rController.basicSearch([collectionName])
rController.writeSearchLog('./')

print(rController.DBController.readFirstTweet("AustinLiveMusic"))
