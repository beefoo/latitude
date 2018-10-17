
def filterWhere(arr, filters):
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


def sortBy(arr, sorters):
    if len(arr) <= 0:
        return arr

    # Sort array
    for key, direction in sorters:
        reversed = (direction == "desc")
        arr = sorted(arr, key=lambda k: k[key], reverse=reversed)

    return arr
