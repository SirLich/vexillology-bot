import praw
import time
import sched

#Globals
VERSION = 1.0
POST_DELAY = 10 #seconds

#Setup
LOGIN_LOCATION = "/home/liam/application_data/atom/reddit/login.txt"
login_file = open(LOGIN_LOCATION, "r")

CLIENT_ID = login_file.readline().strip()
CLIENT_SECRET = login_file.readline().strip()
USERNAME = login_file.readline().strip()
PASSWORD = login_file.readline().strip()
USER_AGENT = login_file.readline().strip()

#This variable holds the instance of PRAW that will talk to the reddit API
reddit = praw.Reddit(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,username=USERNAME,password=PASSWORD,user_agent=USER_AGENT)

#Setup some subreddits
vexillology = reddit.subreddit("vexillology")


#This function determines whether a comment should be left on a post
def blacklisted(post):
    f = open(BLACKLIST_LOCATION,"r")
    for line in f:
        if post.id in line:
            f.close()
            return True
    f.close()
    return False

#Blacklist a post to stop further comments being made on it
def blacklist(post):
    f = open(BLACKLIST_LOCATION,"a")
    f.write(post.id + " " + post.title)
    f.write("\n")
    f.close()

#The main looping part of the program
def main():
    print("vexillology bot" + VERSION + "has loaded!")
    while True:
        for comment in vexillology.stream.comments():
            print(comment.created_utc)
            return
#Begin!
main()
