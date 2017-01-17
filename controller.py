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

def killController():
    cron = CronTab(user=True)
    iter = cron.find_command('/home/ubuntu/mediabots/controller.py')
    for job in iter:
       job.enable(False)
    cron.write()

def rControllerRunner(collection_names, logPath, limit):
    names_to_run = []
    for name in collection_names:
        if (rController.DBController.getDocumentCountFromCollectionName(name) < limit):
            names_to_run.append(name)
    if not names_to_run:
        killController()
        return
    rController.basicSearch(names_to_run)
    rController.writeSearchLog(logPath)

rControllerRunner(collectionNames, './', 100000)
