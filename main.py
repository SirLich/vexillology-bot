#! /usr/bin/python3

import praw #https://praw.readthedocs.io/en/latest/
import time
import sched
from fuzzywuzzy import fuzz #https://github.com/seatgeek/fuzzywuzzy
#from googlesearch import search #https://pypi.org/project/google/#description
import json
import re
import asyncio

#Flags Credit:
#Country flag: http://hjnilsson.github.io/country-flags/
#State flag:
#City and world flag: https://www.crwflags.com/fotw/flags/

#Toolset Credit:
#Atom: https://atom.io/
#Python tools for atom: https://atom.io/packages/python-tools

#Globals
VERSION = 1.4
POST_DELAY = 10 #seconds
TIME_FREEZE = time.time()
COUNTRY_MATCH_THRESHOLD = 80


#Setup
LOGIN = "login.txt"
LOCATIONS = "locations.json"
BLACKLIST = "blacklist.txt"
SUBREDDIT = "vexillology"


login_file = open(LOGIN, "r")

CLIENT_ID = login_file.readline().strip()
CLIENT_SECRET = login_file.readline().strip()
USERNAME = login_file.readline().strip()
PASSWORD = login_file.readline().strip()
USER_AGENT = "SirLich"

#This variable holds the instance of PRAW that will talk to the reddit API
reddit = praw.Reddit(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,password=PASSWORD,user_agent=USER_AGENT,username=USERNAME,)

#Setup the subreedit we will use
vexillology = reddit.subreddit(SUBREDDIT)

#Temp class used for things
class LinkObject:
    def __init__(self, display_name, direct_link, state_code, country_code):
        self.display_name = display_name
        self.direct_link = direct_link
        self.state_code = state_code
        self.country_code = country_code


#This function determines whether a comment should be left on a post
def blacklisted(post):
    f = open(BLACKLIST,"r")
    for line in f:
        if post.id in line:
            f.close()
            return True
    f.close()
    return False

#Blacklist a post to stop further comments being made on it
def blacklist(post):
    f = open(BLACKLIST,"a")
    f.write(post.id + " " + post.title)
    f.write("\n")
    f.close()

#Handle the post!
def handle_post(post):
    title = post.title
    print("")
    print("Handling: " + title)
    regex = re.compile('[^a-zA-Z ,]')
    title = regex.sub('',title)
    title = title.lower()
    with open(LOCATIONS, "r+") as outfile:
        data = json.load(outfile)
        o = set()
        for object in data:
            for alias in object.get("aliases"):
                alias = " " + alias + " "
                if(fuzz.partial_ratio(alias,title) > COUNTRY_MATCH_THRESHOLD):
                    print("I found a country!: " + alias)
                    o.add(LinkObject(object.get("display-name"),object.get("direct-link"),object.get("state-code"),object.get("country-code")))
                    break


        comment = "I did my best to find the following flags: \n\n"
        for object in o:
            display_name = object.display_name
            direct_link = object.direct_link
            country_code = object.country_code
            state_code = object.state_code
            photo_url = "https://us.v-cdn.net/5018160/uploads/FileUpload/45/7c5d94954064b9f1953165ffe15f06.jpg"
            if(direct_link):
                photo_url = direct_link
            elif(state_code):
                photo_url = "http://usa.fmcdn.net/data/flags/w580/" + state_code + ".png"
            elif(country_code):
                photo_url = "https://cdn.rawgit.com/hjnilsson/country-flags/master/png1000px/" + country_code + ".png"

            new_link = "[%s](%s)\n\n"%(display_name,photo_url)
            comment+=new_link
        if(len(o) > 0):
            comment += "Learn more: [GitHub](https://github.com/SirLich/vexillology-bot)"
            print(comment)
            print("")
            comment = post.reply(comment)
    blacklist(post)
    time.sleep(POST_DELAY)

#The main looping part of the program
def main():
    print("VexillologyBot bot " + str(VERSION) + " has loaded!")
    script_start = time.time()
    while True:
        try:
            for post in vexillology.stream.submissions():
                if(not blacklisted(post) and post.created_utc > TIME_FREEZE and (post.link_flair_text is not None and post.link_flair_text.strip().lower() == "redesigns")):
                    print("link: " + post.permalink)
                    handle_post(post)

        except Exception as e: print(e)
main()
