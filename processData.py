# -*- coding: utf-8 -*-

import argparse
import glob
import json
from lib import ascDump, ncDump, norm, readFile
import math
from matplotlib import pyplot as plt
import os
import numpy as np
from PIL import Image
from pprint import pprint
import sys

# input
parser = argparse.ArgumentParser()
parser.add_argument('-config', dest="CONFIG", default="config.json", help="Input config file")
parser.add_argument('-in', dest="INPUT_DIR", default="data/downloads/", help="Input directory")
parser.add_argument('-res', dest="RESOLUTION", default=1.0, type=float, help="Resolution in degrees latitude")
parser.add_argument('-points', dest="POINTS", default=800, type=int, help="Target data points")
parser.add_argument('-out', dest="OUTPUT_DIR", default="data/", help="Output directory")
parser.add_argument('-overwrite', dest="OVERWRITE", default=0, type=int, help="Overwrite existing data?")
parser.add_argument('-draw', dest="DRAW", default=0, type=int, help="Draw data files?")
parser.add_argument('-plot', dest="PLOT", default=0, type=int, help="Plot data?")
args = parser.parse_args()

# Parse arguments
CONFIG = args.CONFIG
INPUT_DIR = args.INPUT_DIR
RESOLUTION = args.RESOLUTION
POINTS = args.POINTS
OUTPUT_DIR = args.OUTPUT_DIR
OVERWRITE = args.OVERWRITE > 0
DRAW = args.DRAW > 0
PLOT = args.PLOT > 0

# ncDump("data/downloads/gpw_v4_une_atotpopbt_dens_2pt5_min.nc")
# ascDump("data/downloads/gpw_v4_national_identifier_grid_rev10_2pt5_min.asc")
# sys.exit()

# Make sure output dir exist
outDirs = [os.path.dirname(OUTPUT_DIR), os.path.dirname("output/")]
for outDir in outDirs:
    if not os.path.exists(outDir):
        os.makedirs(outDir)

files = []
with open(CONFIG) as f:
    configData = json.load(f)
    files = configData["files"]

def getLatitudeData(data, resolution, points, mode="mean"):
    height = resolution / 180.0
    results = []
    h, w = data.shape
    for i in range(points):
        progress = 1.0 * i / (points-1)
        start = progress * (1.0-height)
        end = start + height
        start = int(round(start * h))
        end = int(round(end * h))
        subset = data[start:end]
        subset = subset.reshape(-1)
        count = len(subset)
        subset = subset[~np.isnan(subset)]
        result = None
        if mode == "sum":
            result = int(np.sum(subset))
        elif mode == "set":
            result = list(np.unique(subset.astype(int)))
        elif mode == "percent":
            result = 1.0 * len(subset) / count
        else:
            result = np.mean(subset)
            if np.isnan(result):
                result = 0
            result = int(result)
        results.append(result)
    return results

def valueToColor(value, minValue, maxValue):
    if np.isnan(value):
        return (255, 0, 0)
    else:
        if (maxValue - minValue) > 9999.0 and minValue > 0.0 and value > 0.0:
            maxValue = maxValue**0.25
            minValue = minValue**0.25
            value = value**0.25
        c = int(round(norm(value, (minValue, maxValue)) * 255))
        return (c, c, c)

def drawData(d, filename):
    if os.path.isfile(filename):
        return False
    print("Processing %s..." % filename)
    minValue = np.nanmin(d)
    maxValue = np.nanmax(d)
    print("Value range: %s - %s" % (minValue, maxValue))
    shape = d.shape
    pixels = d.reshape(-1)
    pixels = np.array([valueToColor(value, minValue, maxValue) for value in pixels])
    h, w = shape
    pixels = pixels.reshape((h, w, 3))
    im = Image.fromarray(pixels.astype('uint8'), 'RGB')
    print("Saving %s..." % filename)
    im.save(filename)
    print("Saved %s" % filename)

def drawPlot(y, filename):
    if os.path.isfile(filename):
        return False
    plt.figure(figsize=(20,10))
    x = np.linspace(90, -90, len(y))
    plt.plot(x, y)
    plt.savefig(filename)
    plt.close()
    print("Saved %s" % filename)

# files = [files[4]]

for f in files:
    outFile = OUTPUT_DIR + f["id"] + ".json"
    data = None
    filename = f["filename"]
    pathname = INPUT_DIR + filename
    # Check if file exists already
    if os.path.isfile(outFile) and not OVERWRITE:
        print("%s already exists. Skipping." % outFile)
    else:
        package = None if "package" not in f else INPUT_DIR + f["package"]
        params = {} if "params" not in f else f["params"]
        if "*" in filename:
            filenames = glob.glob(pathname)
            datas = []
            for fn in filenames:
                datas.append(readFile(fn, package=package, params=params))
            # get mean of all datas, ignoring NaN
            data = np.nanmean(np.array(datas), axis=0)
        elif package is None:
            data = readFile(pathname, params=params)
        else:
            data = readFile(filename, package=package, params=params)

    if DRAW:
        drawData(data, "output/map_" + f["id"] + ".png")

    if data is not None:
        # Write to file
        latitudeData = getLatitudeData(data, RESOLUTION, POINTS, mode=f["reduceMode"])
        if PLOT and f["reduceMode"] != "set":
            drawPlot(latitudeData, "output/plot_" + f["id"] + ".png")

        with open(outFile, 'w') as fout:
            f["data"] = latitudeData
            json.dump(f, fout)
            print("Wrote data to %s" % outFile)
