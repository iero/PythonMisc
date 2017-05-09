import os
import json
import random

from requests_oauthlib import requests
import xml.etree.ElementTree as ET

from TwitterAPI import TwitterAPI

# pip install pygeocoder
from pygeocoder import Geocoder
import pandas as pd
import numpy as np

import putils.darksky as darksky

#pip install wikipedia
import putils.wikipedia as wikipedia

import putils.waze as waze

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

spotUrl="https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/"

spotId = "0kGtoQJ7kRRE4Wz5lKhofJjsXf95t27LK"

def loadxml(params_file) :
    tree = ET.parse(params_file)
    return tree.getroot()

def loadjson(json_file) :
    if os.path.exists(json_file) :
        with open(json_file) as f:
            return json.load(f)
    else :
        return {}


if __name__ == "__main__":

    auth_settings = loadxml("auth.xml")

    for service in auth_settings.findall('service') :
    	if service.get("name") == "darksky" :
            darksky_token=service.find("token").text
            darksky_url=service.find("url").text

    # Local record
    lilianjsonfile="lilian.json"
    lilianjson = loadjson(lilianjsonfile)

    # Get Spot data
    client = requests.session()
    url = spotUrl+spotId+"/message.json"
    r = client.get(url, headers=headers)
    response = r.content.decode("utf-8")
    json_decode=json.loads(response)

    for message in json_decode["response"]["feedMessageResponse"]["messages"]["message"] :
        msg_id=message["id"]
        msg_time=message["dateTime"]
        msg_lat=message["latitude"]
        msg_long=message["longitude"]

        for s in lilianjson[msg_id] :
            if 'weather' in s :
            dark_weather=s['weather']
        
        # if "messageContent" in message :
        #     print(message["messageContent"])

        # New entry
        results = Geocoder.reverse_geocode(msg_lat,msg_long)
        link = "https://www.google.com/maps/@{},{},12z".format(msg_lat, msg_long)

        # dark_decode=darksky.getDarkWeather(darksky_url,darksky_token,msg_lat, msg_long)
        # dark_icon = dark_decode["currently"]["icon"]
        # dark_weather = dark_decode["currently"]
        # print(dark_icon)

        # Distance
        if old_msg_lat and old_msg_long :
            route = waze.WazeRouteCalculator(lastPoint["latitude"], lastPoint["longitude"], old_msg_lat, old_msg_long)
            route_time, route_distance = route.calc_route_info()
            print("+-[{} km] depuis le dernier point" .format(route_distance))

        img = wikipedia.getImage(results.city)

        lilianjson[msg_id] = []
        lilianjson[msg_id].append({
            'id': msg_id,
            'time': msg_time,
            'city': results.city,
            'latitude' : msg_lat,
            'longitude' : msg_long,
            'image' : img,
                #'weather' : dark_weather
            'distance' : route_distance
        })

        print("+-[{}] : {} ({},{})".format(msg_id,msg_time,msg_lat, msg_long))


#with open(lilianjsonfile, 'w') as jsonfile:
#    json.dump(lilianjson, jsonfile)
