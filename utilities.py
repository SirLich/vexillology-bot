#! /usr/bin/python3

import sys
import json

def main():
    OUTPUT_LOCATION = "/home/liam/application_data/atom/reddit/VexillologyBot/locations.json"
    location_name = sys.argv[1]
    location_dict = create_dict(location_name)

    with open(OUTPUT_LOCATION, "r+") as outfile:
        data = json.load(outfile)
        print(data)
        data.append(location_dict)
        print(data)
    with open(OUTPUT_LOCATION, "wt") as outfile:
        json.dump(data,outfile, indent=3)

def create_dict(location):
        d = {}
        d["display-name"] = location
        d["svg-link"] = "null"
        aliases = [location.lower()]
        d["aliases"] = aliases
        return d

main()
