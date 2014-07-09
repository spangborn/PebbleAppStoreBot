##[PebbleAppStoreBot](http://www.reddit.com/u/PebbleAppStoreBot)


A Reddit bot that links to Pebble Apps from the Pebble App Store when a user asks to do it.

Heavily based on /u/PlayStoreLinks__Bot by /u/cris9696. It was forked from his code.


####What's included

* LinkMeBot.py, the main program
* App.py, a class that the bot uses to save data
* Config.py, a simple and easy to understand configuration file
* LICENSE, the license that this project is released under (MIT)
* README, this file


####What you need to know before editing this bot / running it on your local machine

The bot was written on a OS X machine with Python 2.7.5

The bot uses the following extra libraries avaible to install via pip:

* praw, to interface with reddit
* requests, to get web pages

You need to set a valid username and password in the config file
Also in the config file you need to set the subreddits where the bot searches for comments

####How to use it

On the server I use the bot is set to run every two minutes using a cronjob
If you want to test the code I suggest you to post a comment in a subreddit and then run the bot


####Info / Reddit-related questions / See the bot in action

http://www.reddit.com/u/PebbleAppStoreBot

Feel free to make any post you want to test it.


####TODO

A database where I save the apps already searched to avoid as many web requests to the Pebble App store as possible


####Want to help or want help?

* If you want to help please feel free to do it.

* If you need help please fell free to ask me.

* If you find any bug or exploit please tell me: I will try to fix them or if you want you can fix them and I will include your changes in the project
Subimited linkme request with 10 apps and bot thinks that i requested more than 10 apps
* If you find a way to improve the bot please share it with everybody.

####LICENSE

MIT License
