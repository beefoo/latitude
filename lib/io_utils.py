# -*- coding: utf-8 -*-

import csv
import gzip
from netCDF4 import Dataset
import numpy as np
import os
import zipfile

def ascDump(filename):
    with open(filename, 'rb') as f:
        lines = list(f)
        lines = lines[:6]
        for line in lines:
            print(line.strip())

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

def readCsv(filename, handler=None):
    if not handler:
        handler = open(filename, 'rb')
    lines = list(handler)
    rows = np.zeros((len(lines), len(lines[0].split(","))))
    for i, line in enumerate(lines):
        row = np.array([float(value) for value in line.split(",")])
        rows[i] = row
    handler.close()
    return rows

def readNetCDF(filename, params):
    ds = Dataset(filename, 'r')
    valueKey = params["valueKey"]
    zKey = None if "zKey" not in params else params["zKey"]
    data = ds.variables[valueKey][:] if zKey is None else ds.variables[valueKey][zKey][:]
    return data

def readAsc(filename, handler=None):
    if not handler:
        handler = open(filename, 'rb')

    handler.close()
    return rows

def readFile(fn, package=None, params={}):
    fileHandler = None
    tempFile = None
    ext = fn.split(".")[-1].lower()
    # check for .zip
    if not os.path.isfile(fn) and package:
        zf = zipfile.ZipFile(package, 'r')
        # special case: NetCDF cannot be read via filehandler; must extract
        if ext == "nc":
            zf.extract(fn)
            tempFile = fn
        else:
            fileHandler = zf.open(fn)
    # check for .gz
    elif os.path.isfile(fn) and ext == "gz":
        fileHandler = gzip.open(fn, 'rb')
        ext = fn.split(".")[-2].lower()
    elif not os.path.isfile(fn):
        print("Cannot find file %s" % fn)
        return False

    results = None
    if ext == "csv":
        results = readCsv(fn, handler=fileHandler)
    elif ext == "nc":
        results = readNetCDF(fn, params=params)
    else:
        results = readTxt(fn, handler=fileHandler)

    if tempFile:
        os.remove(tempFile)
    return results
