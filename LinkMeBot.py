"""
/u/PebbleAppStoreBot

A bot made by /u/spangborn, forked from /u/PlayStoreLinks__Bot by /u/cris9696

General workflow:

*login
*get comments
*reply
*shutdown
"""

#general
import praw
import logging
import os
import sys
import re
import cPickle as pickle

#web
import urllib
import HTMLParser
import json
import requests

#mine
import Config
import App
from pprint import pprint

try:
    alreadyDone = pickle.load( open( "done.p", "rb" ) )
except IOError:
    alreadyDone = []

#setting up the logger

logging.basicConfig(filename=Config.logFile,level=Config.loggingLevel,format='%(levelname)-8s %(message)s')

console = logging.StreamHandler()
console.setLevel(Config.loggingLevel)
console.setFormatter(logging.Formatter('%(asctime)s %(levelname)-8s %(message)s'))
logging.getLogger('').addHandler(console)


def stopBot(removeFile = False):
    """if removeFile:
        os.remove(Config.botRunningFile)"""
    pickle.dump( alreadyDone, open( "done.p", "wb" ) )
    sys.exit(0)


def removeRedditFormatting(text):
    return text.replace("*", "").replace("~", "").replace("^", "").replace(">","")

def isDone(comment):
    #TODO check if in the database
    if comment.id in alreadyDone:
        logging.debug("Already replied to \"" + comment.id + "\"")
        return True

    alreadyDone.append(comment.id)
    return False


def generateComment(linkRequests):
    reply = ""
    nOfRequestedApps = 0
    nOfFoundApps = 0
    for linkRequest in linkRequests:    #for each linkme command
        appsToLink = linkRequest.split(",") #split the apps
        for app in appsToLink:
            app = app.strip()
            if len(app)>0:
                app = HTMLParser.HTMLParser().unescape(app)  #html encoding to normal encoding
                nOfRequestedApps+=1
                if nOfRequestedApps<=Config.maxAppsPerComment:
                    foundApp = findApp(app)
                    if foundApp:
                        nOfFoundApps+=1
                        reply += "[**" + foundApp.fullName + "**](" + foundApp.link + ") - by: " + foundApp.developer + " - " + str(foundApp.hearts) + " Hearts\n\n"
                        logging.info("App found. Full Name: " + foundApp.fullName + " - Link: " + foundApp.link)
                    else:
                        reply +="I am sorry, I can't find any app named \"" + app + "\".\n\n"
                        logging.info("Can't find any app named \"" + app + "\"")
    if nOfRequestedApps>Config.maxAppsPerComment:
        reply = "You requested more than " + str(Config.maxAppsPerComment) + " apps. I will only link to the first " + str(Config.maxAppsPerComment) + " apps.\n\n" + reply

    if nOfFoundApps == 0:
        reply = None

    return reply


def findApp(appName):
    logging.debug("Searching for \"" + appName + "\"")
    app = App.App()
    if len(appName)>0:
        app = searchInDatabase(appName)
        if app:
            return app
        else:
            return searchOnPebbleStore(appName)
    else:
        return None

def searchInDatabase(appName):
    logging.debug("TODO: Searching in database for " + appName)
    return None

def searchOnPebbleStore(appName):
    appNameNoUnicode = appName.encode('utf-8')
    appNameforSearchUrl = urllib.quote_plus(appNameNoUnicode)

    pblAppId = 'BUJATNZD81'
    pblApiKey = '8dbb11cdde0f4f9d7bf787e83ac955ed'
    #pblHost = 'http://httpbin.org/post'
    pblHost = 'http://bujatnzd81-1.algolia.io/1/indexes/pebble-appstore-production/query'

    # POST Payload
    payload = '{ \"params\": \"query=' + appName + '\" }'


    # Headers (w/ API )

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding' : 'gzip, deflate',
        'Accept-Language' : 'en-US,en;q=0.5',
        'Content-Type'    : 'application/json; charset=UTF-8',
        'Origin' : 'http://pas.cpfx.ca',
        'Pragma' : 'no-cache',
        'Referer' : 'http://pas.cpfx.ca/store_boot.html?access_token=0',
        'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:30.0) Gecko/20100101 Firefox/30.0',
        'X-Algolia-API-Key': pblApiKey,
        'X-Algolia-Application-Id' : pblAppId
    }

    try:
        response = requests.post(url=pblHost, data=payload, headers=headers)
        apps = response.json()["hits"]


        if len(apps) > 0:
            app = getAppFromJson(apps[0])
            return app
        else:
            return None

    except Exception as e:
        logging.error("Exception \"" + str(e) + "\" occured while searching on the Pebble Store! Shutting down!")
        stopBot(True)

def getAppFromJson(data):

    app = App.App()

    app.fullName = data["title"]
    app.developer = data["author"]
    app.link = 'https://apps.getpebble.com/applications/' + data["id"]
    app.version = data["version"]
    app.hearts = data["hearts"]
    app.appType = data["type"]

    return app


def reply(comment,myReply):
    logging.debug("Replying to \"" + comment.id + "\"")
    myReply += Config.closingFormula
    tryAgain = True
    while tryAgain:
        tryAgain = False
        try:
            comment.reply(myReply)
            logging.info("Successfully replied to comment \"" + comment.id + "\"\n")
            break
        except praw.errors.RateLimitExceeded as timeError:
            logging.warning("Doing too much, sleeping for " + str(timeError.sleep_time))
            time.sleep(timeError.sleep_time)
            tryAgain = True
        except Exception as e:
            logging.error("Exception \"" + str(e) + "\" occured while replying to \"" + comment.id + "\"! Shutting down!")
            stopBot(True)

def addToDB(app):
    pass
####### main method #######
if __name__ == "__main__":

    """if os.path.isfile(Config.botRunningFile):
            logging.warning("The bot is already running! Shutting down!")
            stopBot()

    open(Config.botRunningFile, "w").close()"""


    logging.debug("Logging in")
    try:
        r = praw.Reddit("/u/PebbleAppStoreBot by /u/spangborn")
        r.login(Config.username, Config.password)
        logging.debug("Successfully logged in")

    except praw.errors.RateLimitExceeded as error:
        logging.error("The bot is doing too much! Sleeping for " + str(error.sleep_time) + " and then shutting down!")
        time.sleep(error.sleep_time)
        stopBot(True)

    except Exception as e:
        logging.error("Exception \"" + str(e) + "\" occured on login! Shutting down!")
        stopBot(True)



    subreddits = r.get_subreddit("+".join(Config.subreddits))


    linkRequestRegex = re.compile("\\bpebble[\s]*me[\s]*:[\s]*(.*?)(?:\.|$)", re.M | re.I)

    try:
        logging.debug("Getting the comments")
        comments = subreddits.get_comments()
        logging.debug("Comments successfully loaded")
    except Exception as e:
        if (str(e) != "TOO_OLD")
            logging.error("Exception \"" + str(e) + "\" occured while getting comments! Shutting down!")
            stopBot(True)


    for comment in comments:
        myReply = ""
        comment.body = removeRedditFormatting(comment.body)

        linkRequests = linkRequestRegex.findall(comment.body)

        if len(linkRequests) > 0:
            if not isDone(comment):
                logging.info("Generating reply to \"" + comment.id + "\"")
                myReply = generateComment(linkRequests)

                if myReply is not None:
                    reply(comment,myReply)
                else:
                    logging.info("No apps found for comment \"" + comment.id + "\"\n\n")

    logging.debug("Shutting down")




    stopBot(True)
