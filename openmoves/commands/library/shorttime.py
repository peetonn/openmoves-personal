import math
import variables
import numpy as np
import threading
from itertools import islice

def split_processing(p1, p2):
    threads = []
    for i in range(len(variables.dtwwindows)):
        threads.append(
            threading.Thread(target=slidingdtw, args=(p1, p2, variables.dtwwindows[i])))
        threads[-1].start()

    for t in threads:
        t.join()

def settoorigin(path):
    x0, y0 = path[0]
    return [(x - x0, y - y0) for x, y in path]

def rotatetox(path):
    xn, yn = path[-1]
    theta = math.atan2(-yn, xn)
    return [(x*math.cos(theta) - y*math.sin(theta), x*math.sin(theta) + y*math.cos(theta)) for x, y in path]

def slide(p, w=3):
    it = iter(p)
    result = tuple(islice(it, w))
    if len(result) == w:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result

#returns dtw distance between paths
#add support for z coordinate
def dtw(p1, p2, window):
    dtwdict = {}

    #set window size... todo: generation of window size via cross-validation
    if (window < abs(len(p1) - len(p2))):
        window = abs(len(p1) - len(p2))

    #generate empty dictionary
    for i in range(-1, len(p1)):
        for j in range(-1, len(p2)):
            dtwdict[(i, j)] = float("inf")#(0, 0, 0)
    dtwdict[(-1, -1)] = 0#(0, 0, 0)

    p1 = settoorigin(p1)
    p2 = settoorigin(p2)
    p1 = rotatetox(p1)
    p2 = rotatetox(p2)

    #do the dtw
    for i in range(len(p1)):
        for j in range(max(0, i - window), min(len(p2), i + window)):
            dist = ((p1[i][0] - p2[j][0]) ** 2) + ((p1[i][1] - p2[j][1]) ** 2)
            dtwdict[(i, j)] = dist + min(dtwdict[(i - 1, j)], dtwdict[(i, j-1)], dtwdict[(i-1, j-1)])#min((dtwdict[(i-1, j)], i-1, j), (dtwdict[(i, j-1)], i, j-1), (dtwdict[(i-1, j-1)], i-1, j-1), 
    """ 
                #key = lambda x: x[0]) #get the min distance with indices appended
            #dtwdict[(i, j)][0] += dist

    #get list indices for warp path
    indices = []
    i, j = len(p1)-1, len(p2)-1
    while not (i == j == 0):
        indices.append((i-1, j-1))
        print(dtwdict[(i, j)])
        print(dtwdict[(i, j)][2])
        i, j = dtwdict[(i, j)][1], dtwdict[(i, j)][2]
    """
    return math.sqrt(dtwdict[len(p1)-1, len(p2)-1]) #, indices.reverse()

def slidingdtw(p1, p2, slidesize):
    alldists = []
    alldists.append(slidesize)
    for outer in slide(p1, slidesize):
        distances = []
        for inner in slide(p2, slidesize):
            distances.append(dtw(outer, inner, 0))
        alldists.append(distances)
    return alldists

#kalman filter, commented heavily for personal reference
#todo: factor in estimation of acceleration 
def kalmanfilter(x, y):
    velocx = []
    velocy = []
    accelx = []
    accely = []

    #specifically for estimating the acceleration & velocity 
    #initial state, with the observed position values
    state = np.array([[float(x[0]), float(y[0]), 0.0, 0.0, 0.0, 0.0]]).T
    n = state.size

    #set up initial covariance matrix
    P = np.diag(np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0]))

    #state transition model
    F = np.array([[1.0, 0.0, variables.PERIOD, 0.0, variables.PERIOD*variables.PERIOD / 2.0, 0.0], [0.0, 1.0, 0.0, variables.PERIOD, 0.0, variables.PERIOD*variables.PERIOD / 2.0],
        [0.0, 0.0, 1.0, 0.0, variables.PERIOD, 0.0], [0.0, 0.0, 0.0, 1.0, 0.0, variables.PERIOD], [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 1.0]])
    
    #measurement matrix, 
    #denoting that we're only taking measurements on position data
    H = np.array([[1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0, 0.0, 0.0]])

    #covariance of observation noise...based off of OPT's current implementation
    R = np.array([[0.5, 0.0], [0.0, 0.5]])
    
    #covariance of process noise 
    G = np.array([[variables.PERIOD * variables.PERIOD / 2.0], [variables.PERIOD * variables.PERIOD / 2.0], [variables.PERIOD], [variables.PERIOD], [1.0], [1.0]])
    Q = np.dot(G, G.T)  

    xy = np.vstack((x, y))

    for i in range(len(x)):
        #prediction step
        #state projection
        state = np.dot(F, state)

        #error projection
        P = np.dot(np.dot(F, P), F.T) + Q

        #update step
        #compute kalman gain
        S = np.dot(np.dot(H, P), H.T) + R
        K = np.dot(np.dot(P, H.T), np.linalg.pinv(S))

        #update estimate
        v = xy[:,i].reshape(2, 1) 
        temp = v - np.dot(H, state)
        state = state + np.dot(K, temp)

        #update error covariance
        I = np.eye(n)
        P = np.dot((I - np.dot(K, H)), P)

        velocx.append(float(state[2]))
        velocy.append(float(state[3]))
        accelx.append(float(state[4]))
        accely.append(float(state[5]))

    return velocx, velocy, accelx, accely
