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
parser.add_argument('-config', dest="CONFIG", default="config.json", help="Input config file")
parser.add_argument('-in', dest="INPUT_DIR", default="data/downloads/", help="Input directory")
parser.add_argument('-res', dest="RESOLUTION", default=1.0, type=float, help="Resolution in degrees latitude")
parser.add_argument('-points', dest="POINTS", default=800, type=int, help="Target data points")
parser.add_argument('-out', dest="OUTPUT_DIR", default="data/", help="Output directory")
parser.add_argument('-overwrite', dest="OVERWRITE", default=0, type=int, help="Overwrite existing data?")
parser.add_argument('-draw', dest="DRAW", default=0, type=int, help="Draw data files?")
parser.add_argument('-plot', dest="PLOT", default=0, type=int, help="Plot data?")
parser.add_argument('-plotdir', dest="PLOT_DIR", default="ui/img/plot/", help="Plot directory")
parser.add_argument('-imgdir', dest="IMAGE_DIR", default="output/", help="Image directory")
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
PLOT_DIR = args.PLOT_DIR
IMAGE_DIR = args.IMAGE_DIR

# ncDump("data/downloads/GDP_per_capita_PPP_1990_2015_v2.nc")
# ncDump("data/downloads/gpw_v4_une_atotpopbt_dens_2pt5_min.nc")
# ascDump("data/downloads/gpw_v4_national_identifier_grid_rev10_2pt5_min.asc")
# sys.exit()

# Make sure output dir exist
outDirs = [os.path.dirname(OUTPUT_DIR), os.path.dirname(PLOT_DIR), os.path.dirname(IMAGE_DIR)]
for outDir in outDirs:
    if not os.path.exists(outDir):
        os.makedirs(outDir)

files = []
with open(CONFIG) as f:
    configData = json.load(f)
    files = configData["files"]

def getLatitudeData(data, resolution, points, mode="mean", precision=0, bounds=(90, -90), fillValue="-", fillValues=[]):
    lat0, lat1 = bounds
    height = 1.0 * resolution / (lat0 - lat1)
    results = []
    h, w = data.shape
    for i in range(points):
        progress = 1.0 * i / (points-1)
        lat = -(progress * 180 - 90)
        filled = False
        for fv in fillValues:
            if fv["bounds"][1] <= lat <= fv["bounds"][0]:
                filled = True
                results.append(fv["value"])
                break
        if filled:
            continue
        if not (lat1 <= lat <= lat0):
            results.append(fillValue)
            continue
        dataProgress = norm(lat, (lat0, lat1))
        start = dataProgress * (1.0-height)
        end = start + height
        start = int(round(start * h))
        end = int(round(end * h))
        if start==end:
            continue
        subset = data[start:end]
        subset = subset.reshape(-1)
        count = len(subset)
        subset = subset[~np.isnan(subset)]
        result = None
        if mode == "count":
            set = list(np.unique(subset.astype(int)))
            result = len(set)
        elif mode == "percent":
            result = 1.0 * len(subset) / count
        elif mode == "sum":
            result = float(np.sum(subset))
        elif len(subset) <= 0:
            result = fillValue
        else:
            result = float(np.mean(subset))
        if isinstance(result, float):
            if precision > 0:
                result = round(result, precision)
            else:
                result = int(round(result))
        results.append(result)
    return results

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

def drawPlot(xy, filename, title, label):
    if os.path.isfile(filename):
        return False
    plt.style.use('fivethirtyeight')
    plt.figure(figsize=(10,10))
    x = [lerp((90, -90), v[0]) for v in xy]
    y = [v[1] for v in xy]
    plt.plot(y, x)
    plt.title(title)
    plt.xlabel(label)
    plt.ylabel("Degrees Latitude")
    plt.yticks(np.arange(-90, 91, step=30))
    plt.savefig(filename)
    plt.close()
    print("Saved %s" % filename)

# files = [files[4]]

for f in files:
    outFile = OUTPUT_DIR + f["id"] + ".json"
    filenames = f["filename"]
    if not isinstance(filenames, list):
        filenames = [filenames]
    datas = []

    # Check if file exists already, just overwrite metadata
    if os.path.isfile(outFile) and not OVERWRITE:
        print("%s already exists." % outFile)
        existingData = {}
        with open(outFile) as fin:
            existingData = json.load(fin)

        existingData.update(f)

        with open(outFile, 'w') as fout:
            json.dump(existingData, fout)
            print("Wrote metadata to %s" % outFile)
        continue

    else:
        for filename in filenames:
            pathname = INPUT_DIR + filename
            package = None if "package" not in f else INPUT_DIR + f["package"]
            params = {} if "params" not in f else f["params"]
            if "*" in filename:
                fns = glob.glob(pathname)
                ds = []
                for fn in fns:
                    ds.append(readFile(fn, package=package, params=params))
                # get mean of all datas, ignoring NaN
                data = np.nanmean(np.array(ds), axis=0)
            elif package is None:
                data = readFile(pathname, params=params)
            else:
                data = readFile(filename, package=package, params=params)
            datas.append(data)

    data = None
    if len(datas) == 1:
        data = datas[0]
    elif len(datas) > 1:
        print("Combining data...")
        data = combineData(datas)

    if data is not None:
        if DRAW:
            drawData(data, IMAGE_DIR + "map_" + f["id"] + ".png")

        # Write to file
        bounds = (90, -90) if "bounds" not in f else tuple(f["bounds"])
        reduceMode = "mean" if "reduceMode" not in f else f["reduceMode"]
        precision = 0 if "precision" not in f else f["precision"]
        fillValue = "-" if "fillValue" not in f else f["fillValue"]
        fillValues = [] if "fillValues" not in f else f["fillValues"]
        latitudeData = getLatitudeData(data, RESOLUTION, POINTS, mode=reduceMode, precision=precision, bounds=bounds, fillValue=fillValue, fillValues=fillValues)
        if PLOT:
            count = len(latitudeData)
            title = f["title"] + " by Latitude ("+str(f["year"])+")"
            label = f["title"]
            if "unit" in f:
                label += " ("+f["unit"]+")"
            drawPlot([(1.0*i/(count-1), d) for i, d in enumerate(latitudeData) if d != fillValue], PLOT_DIR + "plot_" + f["id"] + ".png", title, label)

        with open(outFile, 'w') as fout:
            f["data"] = latitudeData
            json.dump(f, fout)
            print("Wrote data to %s" % outFile)
