import math
import variables
import numpy as np
import threading, fastdtw, cython
from itertools import islice
from scipy.stats.mstats import zscore

def split_processing(p1, p2):
    threads = []
    for i in range(len(variables.dtwwindows)):
        threads.append(
            threading.Thread(target=slidingdtw, args=(p1, p2, variables.dtwwindows[i])))
        threads[-1].start()

    for t in threads:
        t.join()

def slide(p, w=3):
    it = iter(p)
    result = tuple(islice(it, w))
    if len(result) == w:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result

def makerotationinvariant(path):
    #define the movement vector
    vt = []
    vt.append([0,0])
    for i in range(1, len(path)):
        vt.append([path[i][0] - path[i-1][0], path[i][1] - path[i-1][1]])
    
    #transform into angle/arc-length space
    ref = [1,0]
    at = []
    sum = 0
    for t in vt:
        cur = []
        a = np.dot(t, ref)
        b = np.cross(t, ref)
        if b < 0:
            cur.append(-a)
        else: 
            cur.append(a)
        l = math.sqrt((t[0] - t[1])**2)
        sum = sum + l
        cur.append(l)
        at.append(cur)
    
    if sum > 0:
        for i in range(len(at)):
            at[i][1] = float(at[i][1]) / sum

    return at

def iterativeNormalization(rotInvPath):
    seqNorm = []
    for i in range(len(rotInvPath)):
        seqNorm.append(rotInvPath[i][0])
    for j in range(5):
        avgValue = float(sum(seqNorm))/len(seqNorm)
        for i in range(len(seqNorm)):
            seqNorm[i] = seqNorm[i] - avgValue
            if seqNorm[i] < -math.pi:
                seqNorm[i] = 2*math.pi + seqNorm[i]
            elif seqNorm[i] > math.pi:
                seqNorm[i] = -2*math.pi + seqNorm[i]
    
    for i in range(len(rotInvPath)):
        rotInvPath[i][0] = seqNorm[i]

    return rotInvPath

def interpolate(path):
    curinds = []
    curvals = []
    sum = 0
    for i in range(len(path)):
        curvals.append(path[i][0])
        sum = sum + path[i][1]
        curinds.append(sum)
    
    path = np.interp(np.linspace(0,1,len(path)), curinds, curvals)
    return path

def dist(a, b):
    return min(abs(a-b), (2*math.pi - abs(a-b)))

def doFastDTW(p1, p2):
    p1 = makerotationinvariant(p1)
    p1 = iterativeNormalization(p1)
    p1 = interpolate(p1)
    p2 = makerotationinvariant(p2)
    p2 = iterativeNormalization(p2)
    p2 = interpolate(p2)
    distance, ind = fastdtw.fastdtw(p1, p2, dist=dist)
    return distance

def slidingdtw(p1, p2, slidesize):
    alldists = []
    alldists.append(slidesize)
    for outer in slide(p1, slidesize):
        distances = []
        for inner in slide(p2, slidesize):
            distances.append(doFastDTW(outer, inner))
        alldists.append(distances)
    return alldists

"""
def settoorigin(path):
    x0, y0 = path[0]
    return [(x - x0, y - y0) for x, y in path]

def rotatetox(path):
    xn, yn = path[-1]
    theta = math.atan2(-yn, xn)
    return [(x*math.cos(theta) - y*math.sin(theta), x*math.sin(theta) + y*math.cos(theta)) for x, y in path]

#returns dtw distance between paths
#add support for z coordinate
def dtw_d(p1, p2, window):
    dtwdict = {}

    #set window size
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
    
    return math.sqrt(dtwdict[len(p1)-1, len(p2)-1]) #, indices.reverse()

def dtw_i(p1, p2, window):
    #set window size
    if (window < abs(len(p1) - len(p2))):
        window = abs(len(p1) - len(p2))

    p1 = settoorigin(p1)
    p2 = settoorigin(p2)
    p1 = rotatetox(p1)
    p2 = rotatetox(p2)

    #do the dtw
    x1 = []
    x2 = []
    y1 = []
    y2 = []
    for i in range(len(p1)):
        x1.append(p1[i][0])
        x2.append(p2[i][0])
        y1.append(p1[i][1])
        y2.append(p2[i][1])

    x1 = zscore(x1)
    x2 = zscore(x2)
    y1 = zscore(y1)
    y2 = zscore(y2)

    xval, idx = fastdtw.dtw(x1, x2)
    yval, idx = fastdtw.dtw(y1, y2)

    x = dtw_1d(x1, x2, window)
    y = dtw_1d(y1, y2, window)
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
