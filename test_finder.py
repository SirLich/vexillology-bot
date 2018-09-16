#! /usr/bin/python3
import sys
import re
import json
from fuzzywuzzy import fuzz
from google_images_download import google_images_download #Credit: https://github.com/hardikvasa/google-images-download#installation

LOCATION_LOCATION = "/home/liam/application_data/atom/reddit/VexillologyBot/locations.json"
COUNTRY_MATCH_THRESHOLD = 75

class LinkObject:
    def __init__(self, display_name, country_code):
        self.display_name = display_name
        self.code = country_code


def main():
    title = sys.argv[1]
    print("")
    print("Handling: " + title)
    regex = re.compile('[^a-zA-Z ]')
    title = regex.sub('',title)
    title = title.lower()
    print("Normalized title: " + title)
    print("")
    with open(LOCATION_LOCATION, "r+") as outfile:
        data = json.load(outfile)
        o = set()
        for object in data:
            for alias in object.get("aliases"):
                if(fuzz.partial_ratio(alias,title) > COUNTRY_MATCH_THRESHOLD):
                    print(alias)
                    o.add(LinkObject(object.get("display-name"),object.get("country-code")))
        print("")
        comment = "Hello! I did my best to find the following flags:\n"
        for object in o:
            display_name = object.display_name
            code = object.code
            print(display_name + " " + code);

            url = "https://cdn.rawgit.com/hjnilsson/country-flags/master/svg/" + code + ".svg"
            new_link = "[%s](%s)\n"%(display_name,url)
            comment+=new_link
        if(comment != "Hello! I did my best to find the following flags:\n"):
            comment += "^^I ^^am ^^a ^^bot"
            print(comment)
main()
