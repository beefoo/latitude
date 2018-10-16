# -*- coding: utf-8 -*-

import argparse
import json
from lib import *
import math
import os
import numpy as np
from pprint import pprint
import sys
import time

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="data/downloads/vivaldi_samples.csv", help="Input csv file that contains samples with features")
parser.add_argument('-dir', dest="DATA_DIR", default="data/%s.json", help="Input data directory")
parser.add_argument('-dur', dest="DURATION", default=3600, type=int, help="Target duration in seconds")
parser.add_argument('-bdur', dest="BEAT_DUR", default=1000, type=int, help="Duration of a beat in milliseconds")
parser.add_argument('-bdiv', dest="BEAT_DIVISIONS", default=8, type=int, help="How much to divide an individual beat, e.g. 2 = half, 4 = quarters, 8 = eights, etc")
parser.add_argument('-out', dest="OUTPUT_FILE", default="output/composition.csv", help="Output .csv file")
args = parser.parse_args()

# Parse arguments
INPUT_FILE = args.INPUT_FILE
DATA_DIR = args.DATA_DIR
OUTPUT_FILE = args.OUTPUT_FILE
DURATION = args.DURATION
BEAT_DUR = args.BEAT_DUR
BEAT_DIVISIONS = args.BEAT_DIVISIONS

DATA_TO_LOAD = ["anomaly", "countries", "emissions", "gdp", "ice", "land", "pop_count", "temperature", "vegetation"]

UNIT = BEAT_DUR / BEAT_DIVISIONS
print("Base unit is %sms" % UNIT)
if BEAT_DUR % BEAT_DIVISIONS > 0:
    print("Warning: %s does not divide into %s units evenly" % (BEAT_DUR, BEAT_DIVISIONS))
print("Target time: %s" % time.strftime('%H:%M:%S', time.gmtime(DURATION)))

def parseData(d, defaultValue=0.0):
    dataCount = len(d)
    values = [dd for dd in d if dd != "-"]
    minValue = min(values)
    maxValue = max(values)
    pd = []
    for i, dd in enumerate(d):
        value = dd if dd != "-" else defaultValue
        nvalue = norm(value, (minValue, maxValue))
        pd.append({
            "value": value,
            "nvalue": nvalue
        })
    return pd

data = {}
for key in DATA_TO_LOAD:
    filename = DATA_DIR % key
    with open(filename) as f:
        contents = json.load(f)
        data[key] = parseData(contents["data"])
print("Retrieved data from %s files" % len(DATA_TO_LOAD))

samples = readCsvDict(INPUT_FILE)
sampleCount = len(samples)
print("Found %s samples" % sampleCount)

# Normalize certain keys
NORMALIZE_KEYS = ["dur", "hz", "power", "octave"]
for key in NORMALIZE_KEYS:
    values = [s[key] for s in samples]
    minValue = min(values)
    maxValue = max(values)
    for i, sample in enumerate(samples):
        samples[i]["n"+key] = norm(sample[key], (minValue, maxValue))
