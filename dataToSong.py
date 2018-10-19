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
parser.add_argument('-bps', dest="BEATS_PER_SECTION", default=12, type=int, help="How many beats per section")
parser.add_argument('-out', dest="OUTPUT_FILE", default="output/mix.csv", help="Output .csv file")
args = parser.parse_args()

# Parse arguments
INPUT_FILE = args.INPUT_FILE
DATA_DIR = args.DATA_DIR
OUTPUT_FILE = args.OUTPUT_FILE
DURATION = args.DURATION
BEAT_DUR = args.BEAT_DUR
BEAT_DIVISIONS = args.BEAT_DIVISIONS
BEATS_PER_SECTION = args.BEATS_PER_SECTION

dataMappings = {
    "distortion": { "data": "emissions", "range": (0, 20) }, # more emissions = more distortion
    "dur": { "data": "temperature", "range": (0.0, 1.0), "reduce": 0.5 }, # higher temperature = shorter notes (more staccato)
    "highfreq": { "data": "pop_count", "range": (0, 11) }, # more population = more high-frequency instruments
    "lowfreq": { "data": "vegetation", "range": (2, 11) }, # more vegetation = more low-frequency instruments
    "reverb": { "data": "ice", "range": (75.0, 25.0) }, # more ice = less reverb
    "stretch": { "data": "land", "range": (4.0, 1.0) }, # more land = less stretch
    "tempo": { "data": "anomaly", "range": (1.0, 2.0) }, # more anomaly = faster tempo
    "velocity": { "data": "gdp", "range": (0.0, 1.0), "reduce": 0.5 } # more gdp = more high-velocity sounds
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
phraseCount = len(phrases)

UNIT = BEAT_DUR / BEAT_DIVISIONS
print("Base unit is %sms" % UNIT)
if BEAT_DUR % BEAT_DIVISIONS > 0:
    print("Warning: %s does not divide into %s units evenly" % (BEAT_DUR, BEAT_DIVISIONS))
SECTION_DURATION = BEATS_PER_SECTION * BEAT_DUR
SECTIONS = DURATION * 1000.0 / SECTION_DURATION
print("Section count: %s" % SECTIONS)
print("Section duration: %s" % formatSeconds(SECTION_DURATION/1000))
print("Target time: %s" % formatSeconds(DURATION))

if SECTIONS % 1.0 > 0:
    print("Sections do not divide evenly, rounding...")
    SECTIONS = int(round(SECTIONS))
    DURATION = int(round(SECTIONS * SECTION_DURATION / 1000.0))
    print("New target time: %s" % formatSeconds(DURATION))
else:
    SECTIONS = int(SECTIONS)

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

INDEX_KEYS = {"filename": []}
for key in INDEX_KEYS:
    values = list(set([s[key] for s in samples]))
    INDEX_KEYS[key] = values
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

def fetch(mapping, amount, rangeKey="range"):
    value = lerpFetch(mapping["data"], progress)
    return lerp(mapping[rangeKey], value["nvalue"])

def getSequenceSteps(sample, phrase, startms, beatMs, beatDivisions, durationMs):
    steps = []
    unitMs = int(round(1.0 * beatMs / beatDivisions))
    offset = int(round(phrase["offset"]*beatMs)) if "offset" in phrase else 0
    stepMs = phrase["count"] * unitMs
    ms = offset
    while ms < durationMs:
        step = { "ms": startms + ms }
        step.update(sample)
        steps.append(step)
        ms += stepMs
    return steps

ms = 0
sequence = []
for section in range(SECTIONS):
    progress = 1.0 * section / (SECTIONS-1)

    # determine this section's tempo
    tempo = fetch(dataMappings["tempo"], progress)
    sectionBeatMs = int(round(BEAT_DUR/tempo))
    sectionDuration = sectionBeatMs * BEATS_PER_SECTION

    # retrieve other features
    distortion = fetch(dataMappings["distortion"], progress)
    dur = fetch(dataMappings["dur"], progress)
    highfreqCount = int(round(fetch(dataMappings["highfreq"], progress)))
    lowfreqCount = int(round(fetch(dataMappings["lowfreq"], progress)))
    reverb = fetch(dataMappings["reverb"], progress)
    stretch = fetch(dataMappings["stretch"], progress)
    velocity = fetch(dataMappings["velocity"], progress)

    # filter by filename
    filename = lerpFetch(INDEX_KEYS["filename"], progress)
    ssamples = filterWhere(samples, ("filename", filename, "="))
    # print(len(ssamples))

    # filter by
    ssamples = reduceBy(ssamples, dur, dataMappings["dur"]["reduce"])
    # print(len(ssamples))

    ssamples = reduceBy(ssamples, velocity, dataMappings["velocity"]["reduce"])
    # print(len(ssamples))

    if len(ssamples) < (highfreqCount + lowfreqCount):
        print("Warning: not enough samples after filtering for %s at %s. %s needed, %s found" % (filename, formatSeconds(ms/1000), (highfreqCount + lowfreqCount), len(ssamples)))

    # sort by frequency, then select
    ssamples = sorted(ssamples, key=lambda k: k["nhz"])
    lfSamples = ssamples[:lowfreqCount] if lowfreqCount > 0 else []
    hfSamples = ssamples[-highfreqCount:] if highfreqCount > 0 else []

    # add features to samples
    lfSamples = updateArr(lfSamples, {"distortion": 0, "stretch": stretch, "reverb": reverb, "volume": 1.0, "pan": 0})
    hfSamples = updateArr(hfSamples, {"distortion": distortion, "stretch": 1.0, "reverb": reverb, "volume": 1.0, "pan": 0})
    ssamples = lfSamples + hfSamples

    # add to sequence
    for i, sample in enumerate(ssamples):
        phrase = phrases[i % phraseCount]
        sequence += getSequenceSteps(sample, phrase, ms, sectionBeatMs, BEAT_DIVISIONS, sectionDuration)

    ms += sectionDuration

print("Actual time: %s" % time.strftime('%H:%M:%S', time.gmtime(ms/1000)))
writeCsv(OUTPUT_FILE, sequence, ["ms", "ifilename", "start", "dur", "distortion", "pan", "reverb", "stretch", "volume"])
writeCsv(OUTPUT_FILE.replace(".csv", "_audio.csv"), [{"filename": f} for f in INDEX_KEYS["filename"]], ["filename"])
