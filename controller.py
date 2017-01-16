#!/home/ubuntu/.virtualenvs/mediabots/bin/python3
from TwitterSearchPipeline import RestController
from configparser import ConfigParser
import os

os.chdir('/home/ubuntu/mediabots/')
config = ConfigParser()
config.read('bot.config')

rController = RestController(config)

collectionNames = ["AustinBeer", "AustinLiveMusic", "AustinHiking", "AustinCoffeeShops"]

def rControllerRunner(collection_names, logPath):
    rController.basicSearch(collection_names)
    rController.writeSearchLog(logPath)

rControllerRunner(collectionNames, './')
