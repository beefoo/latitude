# -*- coding: utf-8 -*-

import argparse
import glob
import json
from lib import *
import math
from matplotlib import pyplot as plt
import os
import numpy as np
from PIL import Image
from pprint import pprint
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="data/downloads/worldcities.csv", help="Input csv file")
parser.add_argument('-points', dest="POINTS", default=800, type=int, help="Target data points")
parser.add_argument('-max', dest="MAX_CITIES_PER_POINT", default=10, type=int, help="Max cities to display per point")
parser.add_argument('-radius', dest="RADIUS", default=0.5, type=float, help="Radius in degrees for matching cities")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/cities.json", help="Output file")
args = parser.parse_args()

# Parse arguments
INPUT_FILE = args.INPUT_FILE
POINTS = args.POINTS
MAX_CITIES_PER_POINT = args.MAX_CITIES_PER_POINT
RADIUS = args.RADIUS
OUTPUT_FILE = args.OUTPUT_FILE

data = readCsvDict(INPUT_FILE)
print("Founds %s rows from %s" % (len(data), INPUT_FILE))
# pprint(data[100])
# sys.exit(1)

cities = []
dataPoints = []
noMatch = []
for i in range(POINTS):
    p = 1.0 * i / (POINTS-1)
    lat = lerp((90.0, -90.0), p)
    lat0 = lat - RADIUS
    lat1 = lat + RADIUS
    matches = [d for d in data if lat0 <= d["lat"] <= lat1 and not isinstance(d["population"], basestring)]
    matches = sorted(matches, key=lambda d: -d["population"])
    matches = matches[:MAX_CITIES_PER_POINT]
    indices = []
    for match in matches:
        # city_ascii
        city = "%s, %s" % (match["city"], match["country"])
        if city in cities:
            index = cities.index(city)
            indices.append(index)
        else:
            indices.append(len(cities))
            cities.append([city, match["lng"], match["lat"]])
    dataPoints.append(indices)
    if len(indices) <= 0:
        if int(lat) not in noMatch:
            noMatch.append(int(lat))
            print("No matches for %s" % int(lat))

dataOut = {
    "id": "cities",
    "title": "Cities",
    "filename": "worldcities.csv",
    "year": 2018,
    "ref": cities,
    "data": dataPoints,
    "source": "SimpleMaps",
    "sourceURL": "https://simplemaps.com/data/world-cities"
}

with open(OUTPUT_FILE, 'w') as f:
    json.dump(dataOut, f)
    print("Wrote %s cities to %s" % (len(cities), OUTPUT_FILE))
