# -*- coding: utf-8 -*-

import argparse
import glob
import json
from lib import ascDump, ncDump, norm, readFile
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
args = parser.parse_args()

# Parse arguments
CONFIG = args.CONFIG
INPUT_DIR = args.INPUT_DIR
RESOLUTION = args.RESOLUTION
POINTS = args.POINTS
OUTPUT_DIR = args.OUTPUT_DIR
OVERWRITE = args.OVERWRITE > 0
DRAW = args.DRAW > 0

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

def valueToColor(value, minValue, maxValue):
    if np.isnan(value):
        return (255, 0, 0)
    else:
        c = int(round(norm(value, (minValue, maxValue)) * 255))
        return (c, c, c)

def drawData(d, filename):
    if os.path.isfile(filename):
        return False
    print("Processing %s..." % filename)

    # from matplotlib import pyplot as plt
    # plt.figure(figsize = (20,10))
    # x = d.reshape(-1)
    # x = x[~np.isnan(x)]
    # x = x[x > 1000]
    # # example data
    # mu = 100  # mean of distribution
    # sigma = 15  # standard deviation of distribution
    # num_bins = 100
    # fig, ax = plt.subplots()
    # # the histogram of the data
    # n, bins, patches = ax.hist(x, num_bins)
    # plt.show()
    # return False

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
        drawData(data, "output/" + f["id"] + ".png")
    # if data is not None:
        # # Write to file
        # with open(outFile, 'w') as fout:
        #     f["data"] = data
        #     json.dump(f, fout)
        #     print("Wrote data to %s" % outFile)
