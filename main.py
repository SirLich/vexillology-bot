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
COUNTRY_MATCH_THRESHOLD = 82
TESTING = True


#Setup
LOGIN = "login.txt"
LOCATIONS = "locations.json"
BLACKLIST = "blacklist.txt"
SUBREDDIT = "vexillology"

if(TESTING):
    SUBREDDIT = "sirlichbottesting"


login_file = open(LOGIN, "r")

CLIENT_ID = login_file.readline().strip()
CLIENT_SECRET = login_file.readline().strip()
USERNAME = login_file.readline().strip()
PASSWORD = login_file.readline().strip()
USER_AGENT = "SirLich"

#This variable holds the instance of PRAW that will talk to the reddit API
reddit = praw.Reddit(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,password=PASSWORD,user_agent=USER_AGENT,username=USERNAME,)

#Setup the subreedit we will use
subreddit = reddit.subreddit(SUBREDDIT)

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

def tprint(m):
    if(TESTING):
        print(m)


def scrub_title(title):
    regex = re.compile('[^a-zA-Z ]')
    title = regex.sub(' ',title)
    title = "                          " + title.lower() + "                             "
    return title


#Handle the post!
def handle_post(post):
    title = post.title
    title = scrub_title(title)
    o = handle_string(title)
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
        comment += "\n\n---\n\nLinks: [GitHub](https://github.com/SirLich/vexillology-bot/blob/master/README.md), [Complain](https://forms.gle/bYck6E7S2FRth2Ao8)"
        tprint(comment)
        tprint("")
        comment = post.reply(comment)
    blacklist(post)
    time.sleep(POST_DELAY)


def collect_locations(title):
    with open(LOCATIONS, "r+") as outfile:
        data = json.load(outfile)
        o = set()
        for object in data:
            for alias in object.get("aliases"):
                threshold = COUNTRY_MATCH_THRESHOLD
                if(len(alias) < 8):
                    threshold = 100

                if(object.get("threshold")):
                    threshold = object.get("threshold")

                alias = " " + alias + " "
                fuzz_ratio = fuzz.partial_ratio(alias, title)
                no_match_fuzz_ration = fuzz.partial_ratio(title,object.get("no-match"))
                if(fuzz_ratio >= threshold and no_match_fuzz_ration < threshold):
                    tprint("Match: " + alias + " " + str(fuzz_ratio) + " " + str(no_match_fuzz_ration))
                    o.add(LinkObject(object.get("display-name"),object.get("direct-link"),object.get("state-code"),object.get("country-code")))
                    break
        return o

def handle_string(title):
    o = collect_locations(title)
    return o

#The main looping part of the program
def start_bot():
    print("VexillologyBot bot " + str(VERSION) + " has loaded! >> " + SUBREDDIT)
    script_start_time = time.time()
    while True:
        try:
            for post in subreddit.stream.submissions():
                if(not blacklisted(post) and post.created_utc > script_start_time and (TESTING or post.link_flair_text is not None and (post.link_flair_text.strip().lower() == "redesigns" or post.link_flair_text.strip().lower() == "oc"))):
                    tprint("link: " + post.permalink)
                    handle_post(post)

        except Exception as e: tprint(e)

def test():
    while(True):
        collect_locations(scrub_title(input(" > ")))


start_bot()
