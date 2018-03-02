import variables
import numpy as np
import math
import shapely.geometry as geometry

"""Instantaneous features module functionality"""
def pointdists(point):
    distances = []
    for i in range(len(variables.pois)):
        currpt = variables.pois[i]
        distances.append(np.sqrt((currpt[0]-point[0])**2 + (currpt[1]-point[1])**2))
    return distances

def linedists(point):
    distances = []
    pt = geometry.Point(point[0], point[1])
    for i in range(len(variables.stagepts)):
        a = variables.stagepts[i]
        if i == 3:
            b = variables.stagepts[0]
        else:
            b = variables.stagepts[i+1]
        topLeft = geometry.Point(min(a[0], b[0]), min(a[1], b[1]))
        bottomRight = geometry.Point(max(a[0], b[0]), max(a[1], b[1]))
        box = geometry.box(min(topLeft.x - buffer, bottomRight.x + buffer), min(topLeft.y - buffer, bottomRight.y + buffer), 
            max(topLeft.x - buffer, bottomRight.x + buffer), max(topLeft.y - buffer, bottomRight.y + buffer))
        if box.contains(pt):
            #d = |v-dot-r| = |(x2 - x1)(y1 - y0) - (x1 - x0)(y2 - y1)| / sqrt((x2 - x1)^2 + (y2 - y1)^2)
            #where *2 and *1 are endpts of line, *0 is point being checked
            up = abs(((a[0] - b[0]) * (b[1] - point[1])) - ((b[0] - point[0]) * (a[1] - b[1])))
            distances.append(up / math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2))
    return distances

def orientation(idx):
    if len(variables.xdersList[idx] > 0):
        variables.orientations[idx].append(np.linalg.norm(variables.xdersList[idx][-1], variables.ydersList[idx][-1]))

def pairwise(X, Y):
    tempPairs = []
    if(len(X) > len(Y)):
        rng = len(Y)
    else:
        rng = len(X)

    for i in range(rng):
        jArr = []
        for j in range(rng):
            jArr.append(np.sqrt((X[j]-X[i])**2 + (Y[j]-Y[i])**2))
        tempPairs.append(jArr)
    
    return tempPairs

def ders(idx, childList):
    if len(variables.parentList[idx]) > 2:
        x = childList[0]
        y = childList[1]
        prevpoint = variables.parentList[idx][len(variables.parentList[idx])-2]
        variables.xdersList[idx].append((x-prevpoint[0])/variables.PERIOD)
        variables.ydersList[idx].append((y-prevpoint[1])/variables.PERIOD)
        if len(variables.parentList[idx]) > 3 and variables.xdersList[idx][-2] != float('nan'):
            variables.xseconddersList[idx].append(((variables.xdersList[idx][-1] - \
                variables.xdersList[idx][-2])/variables.PERIOD))
            variables.yseconddersList[idx].append(((variables.ydersList[idx][-1] - \
                variables.ydersList[idx][-2])/variables.PERIOD))