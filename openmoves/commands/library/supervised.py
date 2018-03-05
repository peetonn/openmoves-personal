import numpy as np
import variables, shorttime, math, csv
from scipy.stats.mstats import zscore

def readin(t):
    if t == "path":
        x_path_file = open('library/data/paths_x.txt', 'r')
        y_path_file = open('library/data/paths_y.txt', 'r')
        z_path_file = open('library/data/paths_z.txt', 'r')
        label_file = open('library/data/paths_l.txt', 'r')
        
        reader = csv.reader(x_path_file)
        variables.x_path = list(reader)
        reader = csv.reader(y_path_file)
        variables.y_path = list(reader)
        reader = csv.reader(z_path_file)
        variables.z_path = list(reader)
        variables.l_path = label_file.read().splitlines()

    if t == "layout":
        x_layout_file = open('library/data/layouts_x.csv', 'r')
        y_layout_file = open('library/data/layouts_y.csv', 'r')
        z_layout_file = open('library/data/layouts_z.csv', 'r')
        label_file = open('library/data/layouts_l.txt', 'r')

        variables.x_layout = []
        variables.y_layout = []
        variables.z_layout = []
        variables.l_layout = []

        # Loop through datasets
        for x in x_layout_file:
            variables.x_layout.append([float(ts) for ts in x.split()])
            
        for y in y_layout_file:
            variables.y_layout.append([float(ts) for ts in y.split()])
            
        for z in z_layout_file:
            variables.z_layout.append([float(ts) for ts in z.split()])
            
        for y in label_file:
            variables.l_layout.append(int(l.rstrip('\n')))

def predict(test):
    predictions = []
    #for i in enumerate(test):
    mindist = float('inf')
    closest = []

    for i, j, l in variables.x_path, variables.y_path, variables.l_path:
        comp = []
        for k in range(len(i)):
            comp.append([i[k], j[k]])

        comp = shorttime.makerotationinvariant(comp)
        comp = shorttime.iterativeNormalization(comp)
        comp = interpolate(comp)

        test = shorttime.makerotationinvariant(test)
        test = shorttime.iterativeNormalization(test)
        test = interpolate(test)
        
        if lbkeogh(test, comp, 5) < mindist:
            dist = fastdtw.fastdtw(test, comp, dist=shorttime.dist)
            if dist < mindist:
                mindist = dist
                closest = l
    predictions.append(closest)
    return predictions

def lbkeogh(p1, p2, r):
    lbsum = 0
    for ind, i in enumerate(p1):       
        lower = min(p2[(ind - r if ind - r > = 0 else 0):(ind + r)])
        upper = max(p2[(ind - r if ind - r > = 0 else 0):(ind + r)])
        
        if i > upper:
            lbsum = lbsum + (i - upper)**2
        elif i < lower:
            lbsum = lbsum + (i - lower)**2
    
    return np.sqrt(lbsum)

"""
def dtw_i(x, y, path, window):
    #set window size
    if (window < abs(len(x) - len(path))):
        window = abs(len(x) - len(path))
    
    xy = []
    for i in range(len(i)):
        xy.append([x[i], y[i]])

    xy = shorttime.settoorigin(xy)
    path = shorttime.settoorigin(path)
    xy = shorttime.rotatetox(xy)
    path = shorttime.rotatetox(path)

    #do the dtw
    px = []
    py = []
    x = []
    y = []

    for i in range(len(path[0])):
        px.append(path[i][0])
        py.append(path[i][1])

    for j in range(len(xy[0])):
        x.append(xy[j][0])
        y.append(xy[j][1])
    
    x = x[~np.isnan(x)].tolist()
    y = y[~np.isnan(y)].tolist()
    px = zscore(px)
    py = zscore(py)
    x = zscore(x)
    y = zscore(y)

    x = dtw_1d(x, px, window)
    y = dtw_1d(y, py, window)
    return x + y

def dtw_1d(p1, p2, window):
    dtwdict = {}

    for i in range(-1, len(p1)):
        for j in range(-1, len(p2)):
            dtwdict[(i, j)] = float("inf")
    dtwdict[(-1, -1)] = 0
  
    for i in range(len(p1)):
        for j in range(max(0, i - window), min(len(p2), i + window)):
            dist = (p1[i] - p2[j])**2
            dtwdict[(i, j)] = dist + min(dtwdict[(i-1, j)], dtwdict[(i, j-1)], dtwdict[(i-1, j-1)])
		
    return math.sqrt(dtwdict[len(p1) - 1, len(p2) - 1])
"""


