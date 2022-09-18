#! /usr/bin/python3

import praw #https://praw.readthedocs.io/en/latest/
from fuzzywuzzy import fuzz #https://github.com/seatgeek/fuzzywuzzy

import time
import sched
import json
import re
import asyncio
import threading
import queue
from random import random


#Flags Credit:
# http://hjnilsson.github.io/country-flags/
# http://usa.fmcdn.net
# https://www.crwflags.com/fotw/flags/
# https://flagpedia.net

#Toolset Credit:
# Atom: https://atom.io/
# VSCode: https://code.visualstudio.com/

#Globals
VERSION = 2.1
POST_DELAY = 10 #seconds
FUZZY_MATCH_THRESHOLD = 82
RESPONSE_DELAY = 30 #This gives the person some time to add a flair
RESPONSE_RETRIES = 30
NUM_WORKER_THREADS = 5
COUNTRY_URL = "https://flagpedia.net/data/flags/w580/COUNTRY_CODE.png"
STATE_URL = "https://usa.flagpedia.net/data/flags/w580/STATE_CODE.png"

# Old:
# STATE_URL = http://usa.fmcdn.net/data/flags/w580/STATE_CODE.png
# COUNTRY_URL = https://cdn.rawgit.com/hjnilsson/country-flags/master/png1000px/COUNTRY_CODE.png


#Setup
LOGIN = "login.txt"
LOCATIONS = "locations.json"

#SUBREDDIT = "vexillology"
SUBREDDIT = "sirlichbottesting"

login_file = open(LOGIN, "r")

CLIENT_ID = login_file.readline().strip()
CLIENT_SECRET = login_file.readline().strip()
USERNAME = login_file.readline().strip()
PASSWORD = login_file.readline().strip()
USER_AGENT = "SirLich"

#This variable holds the instance of PRAW that will talk to the reddit API
reddit = praw.Reddit(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,password=PASSWORD,user_agent=USER_AGENT,username=USERNAME,)

#Setup the subreddit we will use
subreddit = reddit.subreddit(SUBREDDIT)

#Temp class used for things
class LinkObject:
    def __init__(self, display_name, direct_link, state_code, country_code):
        self.display_name = display_name
        self.direct_link = direct_link
        self.state_code = state_code
        self.country_code = country_code

#Cleans post title for processing
def scrub_title(title):
    regex = re.compile('[^a-zA-Z ]')
    title = regex.sub(' ',title)
    title = "                          " + title.lower() + "                             "
    return title


#Handles an individual post
def handle_post(post):
    title = scrub_title(post.title)
    link_objects = collect_locations(title)

    #If no flags are found, return
    if(len(link_objects) == 0):
        return

    #Just a little old-school easter-egg
    if(random() < 0.001):
        comment = "I did my best to find the following flags : \n\n"
    else:
        comment = "For your reference: \n\n"

    for object in link_objects:
        display_name = object.display_name
        direct_link = object.direct_link
        country_code = object.country_code
        state_code = object.state_code
        photo_url = ""
        if(direct_link):
            photo_url = direct_link
        elif(state_code):
            photo_url = STATE_URL.replace("STATE_CODE", state_code)
        elif(country_code):
            photo_url = COUNTRY_URL.replace("COUNTRY_CODE", country_code)
        
        #Append the new correctly formatted link
        comment += "[%s](%s)\n\n"%(display_name,photo_url)
    
    #Append the final comment message
    comment += "\n\n---\n\nLinks: [Learn more](https://github.com/SirLich/vexillology-bot/blob/master/README.md), Contact the [maintainer](https://www.reddit.com/user/SirLich)."
    print(comment)
    print("")
    comment = post.reply(comment)

#Takes a string, and returns a list of link-objects, based on the found-flags
def collect_locations(title):
    with open(LOCATIONS, "r+") as outfile:
        data = json.load(outfile)
        link_objects = set()
        for object in data:
            for alias in object.get("aliases"):
                threshold = FUZZY_MATCH_THRESHOLD

                #Small flag titles should be forced into an absolute match
                if(len(alias) < 8):
                    threshold = 100

                #Flags can also provide their own threshold
                if(object.get("threshold")):
                    threshold = object.get("threshold")
                
                #Flag titles get padded with extra space to avoid inconsistancies at the edges
                alias = " " + alias + " "
                fuzz_ratio = fuzz.partial_ratio(alias, title)
                no_match_fuzz_ratio = get_no_match_fuzz_ratio(title, object)
                if(fuzz_ratio >= threshold and no_match_fuzz_ratio < threshold):
                    print("Match: " + alias + " " + str(fuzz_ratio) + " " + str(no_match_fuzz_ratio))
                    link_objects.add(LinkObject(object.get("display-name"),object.get("direct-link"),object.get("state-code"),object.get("country-code")))
                    break
        return link_objects

#Helper method to determine the fuzzing of the no-match list
def get_no_match_fuzz_ratio(title, object):
    match = 0
    if "no-match" not in object:
        return match
    for alias in object.get("no-match"):
        temp_match = fuzz.partial_ratio(title,alias)
        if(temp_match > match):
            match = temp_match
    return match


#Worker will take posts from post_queue and asynchroniously handle them 
def worker():
    while True:
        post = post_queue.get()
        id = post.id
        if post is None:
            break

        for i in range(RESPONSE_RETRIES):

            #Retrieve post to refresh flair
            post = reddit.submission(id)
            if(is_flair_valid(post)):
                handle_post(post)
                post_queue.task_done()
                break
            time.sleep(RESPONSE_DELAY)

#Create queue of posts
post_queue = queue.Queue()

#Start worker threads
for i in range(NUM_WORKER_THREADS):
    t = threading.Thread(target=worker)
    t.start()

#Helper function for determining flair validity
def is_flair_valid(post):
    return (post.link_flair_text is not None and (post.link_flair_text.lower() == "redesigns" or post.link_flair_text.strip().lower() == "oc"))

#The main looping part of the program
def start_bot():
    print("VexillologyBot bot " + str(VERSION) + " has loaded! >> " + SUBREDDIT)
    SCRIPT_START_TIME = time.time()
    while True:
        try:
            #Loops through all subreddit posts, including historic ones:
            for post in subreddit.stream.submissions():

                #Only seriously handle new posts
                if(post.created_utc > SCRIPT_START_TIME):
                    print("Handling: " + post.title)

                    #Queue up post for handling
                    post_queue.put(post)

        except Exception as e: print(e)

def test():
    while(True):
        collect_locations(scrub_title(input(" > ")))

# test()
start_bot()
