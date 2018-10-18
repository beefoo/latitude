# -*- coding: utf-8 -*-

import math
import numpy as np

def combineData(data):
    if len(data) <= 0:
        return []
    elif len(data) <= 1:
        return data[0]
    combined = data.pop(0)
    shape = combined.shape
    for d in data:
        dshape = d.shape
        if dshape != shape:
            print("Error: shape %s !=  %s" % (shape, dshape))
            continue
        for index, value in np.ndenumerate(d):
            if np.isnan(combined[index]):
                combined[index] = value
    return combined

def lerp(ab, amount):
    a, b = ab
    return (b-a) * amount + a

def lerpFetch(arr, amount):
    arrLen = len(arr)
    index = int(round(1.0 * amount * (arrLen-1)))
    return arr[index]

def norm(value, ab):
    a, b = ab
    return 1.0 * (value - a) / (b - a)

def roundToNearest(n, nearest):
    return 1.0 * round(1.0*n/nearest) * nearest

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

def weighted_mean(values):
    count = len(values)
    if count <= 0:
        return 0
    weights = [w**2 for w in range(count, 0, -1)]
    return np.average(values, weights=weights)
