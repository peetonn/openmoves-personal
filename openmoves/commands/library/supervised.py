import numpy as np
import variables, shorttime

#alexminnaar.com/time-series-classification-and-clustering-with-python.html
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