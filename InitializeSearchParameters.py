#!/home/ubuntu/.virtualenvs/mediabots/bin/python3
from TwitterSearchPipeline import RestController
from TwitterSearchPipeline import SearchParameters
from configparser import ConfigParser

config = ConfigParser()
config.read('bot.config')

rController = RestController(config)
rController.clearDBCollections()

def addParams(collectionName, keywords, location, radius):
    params = SearchParameters()
    params.addKeywords(keywords)
    params.addLocation(location, radius)
    params.addCollectionName(collectionName)
    rController.addNewSearchParams(params)

addParams("AustinBeer", ['beer', 'draught', 'on draft', 'on tap'], 'Austin Texas', 50)
addParams("AustinLiveMusic", ['Live Music', 'live shows', 'concert'], 'Austin Texas', 50)
addParams("AustinHiking", ['hiking'], 'Austin Texas', 50)
addParams("AustinCoffeeShops", ['coffee', 'coffee shop', 'cafe'], 'Austin Texas', 50)
