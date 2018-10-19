
def filterWhere(arr, filters):
    if isinstance(filters, tuple):
        filters = [filters]

    if len(arr) <= 0:
        return arr

    # Filter array
    for f in filters:
        key, value, mode = f
        if mode == "<=":
            arr = [a for a in arr if a[key] <= value]
        elif mode == ">=":
            arr = [a for a in arr if a[key] >= value]
        elif mode == "<":
            arr = [a for a in arr if a[key] < value]
        elif mode == ">":
            arr = [a for a in arr if a[key] > value]
        elif mode == "~=":
            arr = [a for a in arr if value in a[key]]
        else:
            arr = [a for a in arr if a[key] == value]

    return arr

def lerpFetch(arr, amount):
    arrLen = len(arr)
    index = int(round(1.0 * amount * (arrLen-1)))
    return arr[index]

def reduceBy(arr, amount, reduceTo):
    arrLen = len(arr)
    reduceTo = int(round(arrLen * reduceTo))
    reduceLeft = reduceTo/2
    reduceRight = reduceTo - reduceLeft
    index = int(round(1.0 * amount * (arrLen-1)))
    i0 = index - reduceLeft
    i1 = index + reduceRight
    subLeft = i1 - arrLen + 1 if i1 >= arrLen else 0
    addRight = -i0 if i0 < 0 else 0
    i0 = max(0, i0-subLeft)
    i1 = min(arrLen-1, i1+addRight)
    return arr[i0:i1]

def sortBy(arr, sorters):
    if len(arr) <= 0:
        return arr

    # Sort array
    for key, direction in sorters:
        reversed = (direction == "desc")
        arr = sorted(arr, key=lambda k: k[key], reverse=reversed)

    return arr

def updateArr(arr, values):
    for i, entry in enumerate(arr):
        arr[i].update(values)
    return arr
