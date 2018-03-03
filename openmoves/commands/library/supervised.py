import numpy as np
import variables, shorttime

def readin(t):
    if t == "path":
        x_path_file = open('library/data/paths_x.txt', 'r')
        y_path_file = open('library/data/paths_y.txt', 'r')
        z_path_file = open('library/data/paths_z.txt', 'r')
        label_file = open('library/data/paths_l.txt', 'r')

        # Create empty lists
        x_path = []
        y_path = []
        z_path = []
        l_path = []

        # Loop through datasets
        for x in x_path_file:
            x_path.append([float(ts) for ts in x.split()])
            
        for y in y_path_file:
            y_path.append([float(ts) for ts in y.split()])
            
        for z in z_path_file:
            z_path.append([float(ts) for ts in z.split()])
            
        for y in y_test_file:
            y_test.append(int(y.rstrip('\n')))
    if t == "layout"

def predict(train, test, w):
    predictions = []
    for ind, i in enumerate(test):
        mindist = float('inf')
        closest = []

        for j in train:
            if lbkeogh(i, j[:-1], 5) < mindist:
                dist = shorttime.dtw(i, j[:-1], w)
                if dist < mindist:
                    mindist = dist
                    closest = j
        predictions.append(closest[-1])
    return predictions

def lbkeogh(p1, p2, r):
    lbsum = 0
    for ind, i in enumerate(p1):       
        lower = min(p2[(ind-r if ind-r >=0 else 0):(ind+r)])
        upper = max(p2[(ind-r if ind-r >=0 else 0):(ind+r)])
        
        if i > upper:
            lbsum = lbsum + (i-upper)**2
        elif i < lower:
            lbsum = lbsum + (i-lower)**2
    
    return np.sqrt(lbsum)

#dtw-based classification
#iterate through template paths, find corresponding live paths
#use dtw distance as metric for closest corresponding template path
def classify(live, template, window):
    pass