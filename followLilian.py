import os
import json
import random
import socket
import time

from requests_oauthlib import requests
import xml.etree.ElementTree as ET

from TwitterAPI import TwitterAPI

# pip install pygeocoder
from pygeocoder import Geocoder
import pandas as pd
import numpy as np

import putils.darksky as darksky

#pip install wikipedia
import putils.uwikipedia as wikipedia

import putils.waze as waze

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

spotUrl="https://api.findmespot.com/spot-main-web/consumer/rest-api/2.0/public/feed/"

spotId = "0kGtoQJ7kRRE4Wz5lKhofJjsXf95t27LK"

removeId = [741276466,741263971,741254154,741245153,741245060]
hashtags=['oya','ironman','triathlon','expedition',"run","marathon"]

# debug on local
print("Running on "+socket.gethostname())
if "digital-gf.local" in socket.gethostname() :
	print("Local testing...")
	local = True
else :
    local = False

def loadxml(params_file) :
    tree = ET.parse(params_file)
    return tree.getroot()

def loadjson(json_file) :
    if os.path.exists(json_file) :
        with open(json_file) as f:
            return json.load(f)
    else :
        return {}

def createFirstSentence(ville, meteo, disday) :
    locationSentence=[
        "C'est reparti pour une nouvelle journée ! Passage par VILLE",
        "Première ville traversée aujourd'hui : VILLE",
        "Pour bien commencer votre journée, passez par VILLE",
        "Dommage que je vienne juste de commencer la journée, j'aurais bien pris un café à VILLE",
        "Je suis passé admirer le lever de soleil à VILLE"
    ]

def createSentence(ville,meteo,disday) :
    locationSentence=[
        "Je suis vers VILLE",
        "Je pédale à VILLE",
        "J'ai visité VILLE",
        "Je suis à VILLE",
        "Je visite VILLE",
        "Rejoignez moi, je suis à VILLE",
        "Passage par VILLE",
        "Connaissez vous VILLE ? J'y suis en ce moment !",
        "Si vous me rattrapez à VILLE, je vous offre une bière",
        "De Porspoder à VILLE, la digue la digue..",
        "Si vous passez par VILLE et que vous voyez un cycliste..",
        "Sur les routes de VILLE",
        "Je viens de croiser un panneau qui souhaite la bienvenue à VILLE",
        "VILLE, son troquet, sa poste et sa mairie",
        "Le village de VILLE souhaite la bienvenue aux cyclistes",
        "VILLE : le bitume de ses routes, et ses paysages",
        "Si j'avais un peu plus de temps je visiterais bien VILLE",
        "Je pédale donc je suis.. à VILLE"
    ]

    if disday < 20 :
        locationSentence.append("Je visiterais bien VILLE, mais je n'ai fait que {} km ce matin".format(disday))

    if disday > 50 :
        locationSentence.append("Déja {} km aujourd'hui et je suis enfin à VILLE".format(disday))
        locationSentence.append("{} km depuis mon réveil, et me voici à VILLE".format(disday))

    weet_text = random.choice(locationSentence).replace('VILLE',results.city)

    return weet_text

def computeDistance(lilianjson) :
    distToday = 0
    distTotal = 0
    for id in lilianjson :
        d=0
        today=False
        for s in lilianjson[id] :
            if 'distance' in s :
                d = s['distance']
                distTotal = distTotal + d

            if 'time' in s and s['time'].startswith(time.strftime("%Y-%m-%d")) :
                today=True

            if today and d > 0 :
                distToday = distToday + d
                d=0
    return distToday,distTotal

if __name__ == "__main__":

    auth_settings = loadxml("auth.xml")

    for service in auth_settings.findall('service') :
    	if service.get("name") == "twitter" :
    		consumer_key=service.find("consumer_key").text
    		consumer_secret=service.find("consumer_secret").text
    		access_token_key=service.find("access_token_key").text
    		access_token_secret=service.find("access_token_secret").text
    	elif service.get("name") == "darksky" :
            darksky_token=service.find("token").text
            darksky_url=service.find("url").text

    # Local record
    lilianjsonfile="lilian.json"
    lilianjson = loadjson(lilianjsonfile)
    print("+-[Loaded json] : {}".format(lilianjsonfile))

    lastPointId = max(lilianjson)
    lastPoint= lilianjson[lastPointId]
    for s in lastPoint :
        if 'latitude' in s : lastLat = s['latitude']
        if 'longitude' in s : lastLong = s['longitude']

    # Get Spot data
    client = requests.session()
    url = spotUrl+spotId+"/message.json"
    print("+-[Load spot url] : {} ".format(url))
    r = client.get(url, headers=headers)
    response = r.content.decode("utf-8")
    json_decode=json.loads(response)
    messages = json_decode["response"]["feedMessageResponse"]["messages"]["message"]
    print("+-[Load spot data] with {} entries ".format(len(messages)))

    for message in messages :
        msg_id=message["id"]
        msg_time=message["dateTime"]
        msg_lat=message["latitude"]
        msg_long=message["longitude"]
        # if "messageContent" in message :
        #     print(message["messageContent"])

        # New entry
        if (str(msg_id) not in lilianjson) :
            print("+-[{}] : {} ({},{})".format(msg_id,msg_time,msg_lat, msg_long))
            results = Geocoder.reverse_geocode(msg_lat,msg_long)

            link = "https://www.google.com/maps/@{},{},12z".format(msg_lat, msg_long)

            #link = "http://maps.google.com/?q={},France/@{},{},12z".format(results.city,msg_lat, msg_long)

            dark_decode=darksky.getDarkWeather(darksky_url,darksky_token,msg_lat, msg_long)
            dark_icon = dark_decode["currently"]["icon"]
            dark_weather = dark_decode["currently"]
            print(dark_icon)

            # Distance
            route_distance=0
            if lastLat and lastLong :
                route = waze.WazeRouteCalculator(lastLat, lastLong, msg_lat, msg_long)
                route_time, route_distance = route.calc_route_info()
                print("+-[{} km] depuis le dernier point" .format(route_distance))

            tweet_text = createSentence(results.city, "none",route_distance)

            tweet_text += " "+ link
            tweet_text += " #oya"

            lilianjson[msg_id] = []
            lilianjson[msg_id].append({
                'id': msg_id,
                'time': msg_time,
                'city': results.city,
                'latitude' : msg_lat,
                'longitude' : msg_long,
                'weather' : dark_weather,
                'distance' : route_distance
            })

            if not local and route_distance >= 1 :
                twitterapi = TwitterAPI(consumer_key=consumer_key, consumer_secret=consumer_secret, access_token_key=access_token_key, access_token_secret=access_token_secret)

                twitterapi.request('statuses/update', {'status':tweet_text, 'lat':msg_lat,'long':msg_long})

            print("+-[Tweet] {}".format(tweet_text))

            #img = wikipedia.getImage(results.city)
            #if (img) :
            #    print("Pic : "+img)
            #     response = requests.get(img, headers=headers, allow_redirects=True)
            #     data = response.content
            #     twitterapi.request('statuses/update_with_media', {'status':tweet_text}, {'media[]':data})
            # else :

    distToday,distTotal = computeDistance(lilianjson)

    print("+-[Distance] Today : {} km, Total : {} km".format(int(distToday),int(distTotal)))

    with open(lilianjsonfile, 'w') as jsonfile:
        json.dump(lilianjson, jsonfile)
