import json

from requests_oauthlib import requests

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}


def getDarkWeather(darksky_url,darksky_token,msg_lat, msg_long) :
    meteoUrl = "{}{}/{},{}?lang=fr".format(darksky_url,darksky_token,msg_lat, msg_long)

    client = requests.session()
    dark = client.get(meteoUrl, headers=headers)
    return json.loads(dark.content.decode("utf-8"))


# def getRandomDay(state) :
#     answer = []
#     if state == "clear-day" :
#
#     elif state == "clear-night" :
#     elif state == "rain" :
#     elif state == "snow" :
#     elif state == "sleet" :
#     elif state == "wind" :
#     elif state == "fog" :
#     elif state == "cloudy" :
#     elif state == "partly-cloudy-day" :
#     elif state == "partly-cloudy-night" :
