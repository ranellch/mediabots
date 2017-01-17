#!/home/ubuntu/.virtualenvs/mediabots/bin/python3

# Intended to be run as a cron job. InitializeSearchParameters.py needs to have
#  already populated the database with search parameters.

from TwitterSearchPipeline import RestController
from configparser import ConfigParser
from crontab import CronTab
import os

os.chdir('/home/ubuntu/mediabots/')
config = ConfigParser()
config.read('bot.config')

rController = RestController(config)

collectionNames = ["AustinBeer", "AustinLiveMusic", "AustinHiking", "AustinCoffeeShops"]

def rControllerRunner(collection_names, logPath):
    rController.basicSearch(collection_names)
    rController.writeSearchLog(logPath)
#    cron = CronTab(user=True)
#    iter = cron.find_command('/home/ubuntu/mediabots/controller.py')
#    for job in iter:
#        job.enable(False)
#    cron.write()    

rControllerRunner(collectionNames, './')
