#! /usr/bin/python3

import sys
import json

def main():
    OUTPUT_LOCATION = "/home/liam/application_data/atom/reddit/VexillologyBot/locations.json"
    INPUT_LOCATION = sys.argv[1]

    with open(INPUT_LOCATION) as f:
        for line in f:
            location_name = line.split("-")[0].strip()
            location_code = line.split("-")[1].strip().lower()
            print(location_name + location_code)
            location_dict = create_dict(location_name, location_code)
            with open(OUTPUT_LOCATION, "r+") as outfile:
                data = json.load(outfile)
                print(data)
                data.append(location_dict)
                print(data)
            with open(OUTPUT_LOCATION, "wt") as outfile:
                json.dump(data,outfile, indent=3)

def create_dict(location, location_code):
        d = {}
        d["display-name"] = location
        d["state-code"] = location_code;
        aliases = [location.lower()]
        d["aliases"] = aliases
        return d

main()
