# -*- coding: utf-8 -*-

import csv
import gdal
import gzip
from netCDF4 import Dataset
import numpy as np
import numpy.ma as ma
import os
import zipfile

def parseNumber(string):
    try:
        num = float(string)
        if "." not in string:
            num = int(string)
        return num
    except ValueError:
        return string

def parseNumbers(arr):
    for i, item in enumerate(arr):
        for key in item:
            arr[i][key] = parseNumber(item[key])
    return arr

def ascDump(filename):
    with open(filename, 'rb') as f:
        lines = list(f)
        rows = len(lines)-6
        firstLine = [l.strip() for l in lines[6].strip().split(" ")]
        print("rows: %s" % rows)
        print("cols: %s" % len(firstLine))

        lines = lines[:6]
        for line in lines:
            print(line.strip())

def tifDump(filename):
    ds = gdal.Open(filename)
    print(ds.GetMetadata())
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    rows, cols = arr.shape
    arr_min = arr.min()
    arr_max = arr.max()
    print("Shape: %s x %s" % (cols, rows))
    print("Range: %s - %s" % (arr_min, arr_max))
    ds = None

def ncDump(filename, verb=True):
    nc_fid = Dataset(filename, 'r')
    def print_ncattr(key):
        try:
            print "\t\ttype:", repr(nc_fid.variables[key].dtype)
            for ncattr in nc_fid.variables[key].ncattrs():
                print '\t\t%s:' % ncattr,\
                      repr(nc_fid.variables[key].getncattr(ncattr))
        except KeyError:
            print "\t\tWARNING: %s does not contain variable attributes" % key

    # NetCDF global attributes
    nc_attrs = nc_fid.ncattrs()
    if verb:
        print "NetCDF Global Attributes:"
        for nc_attr in nc_attrs:
            print '\t%s:' % nc_attr, repr(nc_fid.getncattr(nc_attr))
    nc_dims = [dim for dim in nc_fid.dimensions]  # list of nc dimensions
    # Dimension shape information.
    if verb:
        print "NetCDF dimension information:"
        for dim in nc_dims:
            print "\tName:", dim
            print "\t\tsize:", len(nc_fid.dimensions[dim])
            print_ncattr(dim)
    # Variable information.
    nc_vars = [var for var in nc_fid.variables]  # list of nc variables
    if verb:
        print "NetCDF variable information:"
        for var in nc_vars:
            if var not in nc_dims:
                print '\tName:', var
                print "\t\tdimensions:", nc_fid.variables[var].dimensions
                print "\t\tsize:", nc_fid.variables[var].size
                print_ncattr(var)
    return nc_attrs, nc_dims, nc_vars

def parseFloat(string, multiplier=None):
    try:
        num = float(string.strip())
        if multiplier is not None:
            num *= multiplier
        return num
    except ValueError:
        return np.nan

def readCsv(filename, delimeter=",", handler=None, params={}):
    if not handler:
        handler = open(filename, 'rb')
    skipRows = 0 if "skipRows" not in params else params["skipRows"]
    multiplier = None if "multiplier" not in params else params["multiplier"]
    shape = None if "shape" not in params else tuple(params["shape"])
    lines = list(handler)
    if skipRows > 0:
        lines = lines[skipRows:]
    firstLine = [l.strip() for l in lines[0].strip().split(delimeter)]
    rows = np.zeros((len(lines), len(firstLine)))
    for i, line in enumerate(lines):
        row = np.array([parseFloat(value, multiplier=multiplier) for value in line.strip().split(delimeter)])
        rows[i] = row
    if shape is not None:
        rows = rows.reshape(shape)
    handler.close()
    return rows

def readCsvDict(filename):
    rows = []
    if os.path.isfile(filename):
        with open(filename, 'rb') as f:
            lines = [line for line in f if not line.startswith("#")]
            reader = csv.DictReader(lines, skipinitialspace=True)
            rows = list(reader)
            rows = parseNumbers(rows)
    return rows

def readGeoTIFF(filename, params={}):
    ds = gdal.Open(filename)
    band = ds.GetRasterBand(1)
    data = band.ReadAsArray()
    ds = None
    return data

def readNetCDF(filename, params={}):
    ds = Dataset(filename, 'r')
    valueKey = params["valueKey"]
    zKey = None if "zKey" not in params else params["zKey"]
    data = ds.variables[valueKey][:] if zKey is None else ds.variables[valueKey][zKey][:]
    ds.close()
    return data

def readText(filename, handler=None, params={}):
    return readCsv(filename, delimeter=" ", handler=handler, params=params)

def readFile(fn, package=None, params={}):
    print("Reading file %s..." % fn)
    fileHandler = None
    tempFile = None
    ext = fn.split(".")[-1].lower()
    # check for .zip
    if not os.path.isfile(fn) and package:
        zf = zipfile.ZipFile(package, 'r')
        # special case: NetCDF and GeoTiff cannot be read via filehandler; must extract
        if ext in ["nc", "tif"]:
            zf.extract(str(fn))
            tempFile = fn
        else:
            fileHandler = zf.open(str(fn))
    # check for .gz
    elif os.path.isfile(fn) and ext == "gz":
        fileHandler = gzip.open(fn, 'rb')
        ext = fn.split(".")[-2].lower()
    elif not os.path.isfile(fn):
        print("Cannot find file %s" % fn)
        return False

    results = None
    if ext == "csv":
        results = readCsv(fn, handler=fileHandler, params=params)
    elif ext == "nc":
        results = readNetCDF(fn, params=params)
    elif ext == "tif":
        results = readGeoTIFF(fn, params=params)
    else:
        results = readText(fn, handler=fileHandler, params=params)

    if "reverse" in params:
        results = np.flip(results, axis=0)

    emptyValue = None if "emptyValue" not in params else params["emptyValue"]
    if emptyValue is not None:
        results = replaceEmpty(results, emptyValue)

    if tempFile:
        os.remove(tempFile)

    print("%s parsed with shape %s" % (fn, results.shape))
    return results

def replaceEmpty(arr, emptyValue):
    shape = arr.shape
    arr = arr.reshape(-1)
    ev = float(emptyValue)
    arr[arr==ev] = np.nan
    arr = ma.filled(arr, np.nan)
    arr = arr.reshape(shape)
    return arr

def writeCsv(filename, arr, headings):
    with open(filename, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(headings)
        for i, d in enumerate(arr):
            row = []
            for h in headings:
                row.append(d[h])
            writer.writerow(row)
    print("Wrote %s rows to %s" % (len(arr), filename))
