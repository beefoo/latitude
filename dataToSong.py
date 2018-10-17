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

dataMappings = {
    "distortion": { "data": "emissions", "range": (0, 20) }, # more emissions = more distortion
    "dur": { "data": "temperature", "range": (0.0, 1.0) }, # higher temperature = shorter notes (more staccato)
    "highfreq": { "data": "pop_count", "range": (2, 11) }, # more population = more high-frequency instruments
    "lowfreq": { "data": "vegetation", "range": (2, 11) }, # more vegetation = more low-frequency instruments
    "reverb": { "data": "ice", "range": (75.0, 25.0) }, # more ice = less reverb
    "stretch": { "data": "land", "range": (4.0, 1.0) }, # more land = less stretch
    "tempo": { "data": "anomaly", "range": (1.0, 2.0) }, # more anomaly = faster tempo
    "velocity": { "data": "gdp", "range": (0.0, 1.0) } # more gdp = more high-velocity sounds
}

phrases = [
    {"count": BEAT_DIVISIONS},
    {"count": BEAT_DIVISIONS, "offset": 0.5},
    {"count": BEAT_DIVISIONS, "offset": 0.25},
    {"count": BEAT_DIVISIONS, "offset": 0.75},
    {"count": BEAT_DIVISIONS, "offset": 0.125},
    {"count": BEAT_DIVISIONS, "offset": 0.625},
    {"count": BEAT_DIVISIONS, "offset": 0.375},
    {"count": BEAT_DIVISIONS, "offset": 0.875},
    {"count": BEAT_DIVISIONS/2, "gainPhase": (0, 1.0), "phase": 12},
    {"count": BEAT_DIVISIONS/2, "offset": 0.25, "gainPhase": (0, 1.0), "phase": 12},
    {"count": BEAT_DIVISIONS/2, "offset": 0.125, "gainPhase": (0, 1.0), "phase": 12}
]

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

for key in dataMappings:
    dataKey = dataMappings[key]["data"]
    filename = DATA_DIR % dataKey
    with open(filename) as f:
        contents = json.load(f)
        dataMappings[key]["data"] = parseData(contents["data"])

samples = readCsvDict(INPUT_FILE)
sampleCount = len(samples)
print("Found %s samples" % sampleCount)

INDEX_KEYS = ["filename"]
for key in INDEX_KEYS:
    values = list(set([s[key] for s in samples]))
    for i, sample in enumerate(samples):
        samples[i]["i"+key] = values.index(sample[key])

# Normalize certain keys
NORMALIZE_KEYS = ["ifilename", "dur", "hz", "power", "octave"]
for key in NORMALIZE_KEYS:
    values = [s[key] for s in samples]
    minValue = min(values)
    maxValue = max(values)
    for i, sample in enumerate(samples):
        samples[i]["n"+key] = norm(sample[key], (minValue, maxValue))
