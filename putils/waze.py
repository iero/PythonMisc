# -*- coding: utf-8 -*-
"""Waze route calculator"""

import json
import logging
import requests

class WRCError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class WazeRouteCalculator(object):
    """Calculate actual route time and distance with waze api"""

    WAZE_URL = "https://www.waze.com/"

    def __init__(self, from_lat, from_long, to_lat, to_long, log_lvl=logging.INFO):
        self.log = logging.getLogger(__name__)
        self.log.setLevel(log_lvl)
        self.log.addHandler(logging.StreamHandler())
        #self.log.info("From: %s - to: %s", start_address, end_address)

        #self.start_coords = self.address_to_coords(start_address)
        self.start_coords = {"lon": from_long, "lat": from_lat}
        #self.log.debug('Start coords: (%s, %s)', self.start_coords["lon"], self.start_coords["lat"])
        #self.end_coords = self.address_to_coords(end_address)
        self.end_coords = {"lon": to_long, "lat": to_lat}
        #self.log.debug('End coords: (%s, %s)', self.end_coords["lon"], self.end_coords["lat"])

    def address_to_coords(self, address):
        """Convert address to coordinates"""

        get_cords = "SearchServer/mozi?"
        url_options = {
            "q": address,
            "lang": "eng",
            "origin": "livemap",
            "lon": "19.040",
            "lat": "47.498"
        }
        response = requests.get(self.WAZE_URL + get_cords, params=url_options)
        response_json = response.json()[0]
        lon = response_json['location']['lon']
        lat = response_json['location']['lat']
        return {"lon": lon, "lat": lat}

    def get_route(self):
        """Get route data from waze"""

        routing_req = "row-RoutingManager/routingRequest?"

        url_options = {
            "from": "x:%s y:%s" % (self.start_coords["lon"], self.start_coords["lat"]),
            "to": "x:%s y:%s" % (self.end_coords["lon"], self.end_coords["lat"]),
            "at": 0,
            "returnJSON": "true",
            "returnGeometries": "true",
            "returnInstructions": "true",
            "timeout": 60000,
            "nPaths": 3,
            "options": "AVOID_TRAILS:t",
        }
        response = requests.get(self.WAZE_URL + routing_req, params=url_options)
        response_json = response.json()
        if response_json.get("error"):
            raise WRCError(response_json.get("error"))
        if response_json.get("alternatives"):
            return response_json['alternatives'][0]['response']
        return response_json['response']

    def calc_route_info(self):
        """Calculate best route info."""

        route = self.get_route()
        results = route['results']
        time = 0
        distance = 0
        for segment in results:
            time += segment['crossTime']
            distance += segment['length']
        route_time = time / 60.0
        route_distance = distance / 1000.0
        self.log.info('Time %.2f minutes, distance %.2f km.', route_time, route_distance)
        return route_time, route_distance
