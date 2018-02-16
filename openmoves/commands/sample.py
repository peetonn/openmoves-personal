import socket, time, json, time, random, Math
from sklearn.cluster import AffinityPropagation
from scipy import linalg
import shapely.geometry as geometry
from descartes import PolygonPatch
import matplotlib.pyplot as plt
import numpy as np
import numpy.random as rnd

from .base import Base

"""
Next steps:
SPARSITY SUPPORT / further general clean-up & style adjustments 
                        ex: cleaning up places where I extracted list elements to work with them, 
                            cleaning stored vars which aren't used, cleaning up redundant vars...


Calculate number of acute angles along convex hull to determine group shape

Adjust to number of LIVE IDs/perform live ID filtering

As discussed with Marco, implemeting the edge-of-stage functionality using
roslaunch opt_calibration network_assessment.launch which depends on having the OPT network calibrated.
How it works:  
    -> we have the calibration parameters of each sensor that defines the FOV cone of each camera
    -> given the extrinsic calibration of the network, can intersect the cones and get the area
"""

class Sample(Base):
    def __init__(self, ops, *args, **kwargs):
        self.ops = ops
        self.args = args
        self.kwargs = kwargs
        self.UDP_IP = "127.0.0.1"
        self.UDP_PORT = 21234
        self.PERIOD = .100    

        self.MAXSTEP_X = 10         
        self.MAXSTEP_Y = 10
        self.WOBBLE_Z = 1
        self.Z_NOMINAL = 40
        self._SEQ = 0 

        self.parentList = []
        self.pairs = []
        self.ids = []
        self.xdersList = []
        self.ydersList = []
        self.xseconddersList = []
        self.yseconddersList = []

        self.allX = []
        self.allY = []

    def track(self, id, x, y, height, age, confidence) :
        return {"id":id, "x":x, "y":y, "height":height, "age": age, "confidence":confidence}

    def packet(self, tracks) : 
        self._SEQ+=1
        now = float(time.time())
        sec = int(now)
        nsec = int((now-sec) * 1e9)
        header = { "seq":self._SEQ, "stamp": {"sec":sec, "nsec":nsec}, "frame_id":"world" }
        return { "header":header, "tracks":tracks } 

    '''
    #progress towards below todo, written for 1 variable at a time
    #used during debugging, will integrate later
    def dowalk(x, v):
        dt = .01
        a = rnd.randn()
        x = x + v * dt + 0.5 * a * dt * dt
        v = v + a * dt
        return x, v

    def indwalk(x0, v0, n):
        x = x0
        v = v0
        xes = np.zeros(n)
        i = 0
        while i < n:
            xes[i] = x
            x, v = dowalk(x, v)
            i = i+1
        return xes 
    '''

    def walk(self, W):
        #todo: adjust this to generate paths which are differentiable
        #where acceleration is what is random & velocity then position are calculated from it
        #a_n is random, v_(n+1)=v_n+a_n dt and x_(n+1)=x_n+v_ndt+1/2 a_n dt^2
        for w in W: 
            w[0] += self.MAXSTEP_X * 2*(random.random() - 0.5)
            w[1] += self.MAXSTEP_Y * 2*(random.random() - 0.5)
            w[2] = self.Z_NOMINAL + self.WOBBLE_Z*2*(random.random()-0.5) 
    
    def pairwise(self, X, Y):
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

    def covariance(self): #ignore entries of resulting matrix with indicies not both odd or even
        #todo: keep track of longest length for zero padding / otherwise account for different n in each timestep  
        #create a matrix such that each column is the x or y of a particular actor
        allXY = []
        for i in range(len(self.allX)):
            currentX = self.allX[i]
            currentY = self.allY[i]
            recentXY = []
            for j in range(len(currentX)):
                recentXY.append(currentX[j])
                recentXY.append(currentY[j])
            allXY.append(recentXY)
        cov = np.cov(allXY)

        #now filter out x-to-y and y-to-x covariances
        m, n = cov.shape
        truecov = []
        for i in range(m): #rows
            currrow = []
            for j in range(n): #columns
                if i%2==0 and j%2==0:
                    currrow.append(cov[i, j])
                elif i%2!=0 and j%2!=0:
                    currrow.append(cov[i, j])
            truecov.append(currrow)
        return truecov

    def covarianceind(self):
        covX = np.cov(np.asarray(self.allX).T)
        covY = np.cov(np.asarray(self.allY).T)

        return covX, covY

    #returns dtw distance between two paths as well as their warp path indices
    #can specify window size to go through time
    #use also with velocity vectors from kalman filter to find similar velocity periods, etc
    """todo: 
            -next steps with dtw-- currently just used for path comparisons but
    can be applied to activity categorisation when using a reference dataset...
    for example: can be customised per performance to search for a particular movement
    sequence among all actors
            -add support for z coordinate"""
    def dtw(self, p1, p2, window):
        dtwdict = {}

        #set window size... todo: generation of window size via cross-validation
        if (window > abs(len(p1) - len(p2))):
            window = abs(len(p1) - len(p2))

        #generate empty dictionary
        for i in range(-1, len(p1)):
            for j in range(-1, len(p2)):
                dtwdict[(i, j)] = (0, 0, 0)
        dtwdict[(-1, -1)] = (0, 0, 0)

        #do the dtw
        for i in range(len(p1)):
            for j in range(max(0, i - window), min(len(p2), i + window)):
                dist = ((p1[i][0] - p2[j][0]) ** 2) + ((p1[i][1] - p2[j][1]) ** 2)
                dtwdict[(i, j)] = min((dtwdict[(i-1, j)], i-1, j), (dtwdict[(i, j-1)], i, j-1), (dtwdict[(i-1, j-1)], i-1, j-1), 
                    key = lambda x: x[0]) #get the min distance with indices appended
                dtwdict[(i, j)][0] += dist

        #get list indices for warp path
        indices = []
        i, j = len(p1), len(p2)
        while not (i == j == 0):
            indices.append((i-1, j-1))
            i, j = dtwdict[(i, j)][1], dtwdict[(i, j)][2]

        return Math.sqrt(dtwdict[len(p1)-1, len(p2)-1]), indices.reverse()

    #dtw-based classification, as per above todo
    #iterate through template paths, find corresponding live paths
    #use dtw distance as metric for closest corresponding template path
    def classify(self, live, template, window):
        pass

    """
    #fastdtw library, want to reduce dependence on tones of libs so not using
    def usefastdtw(x1, x2):
        import fastdtw

        distance, path = fastdtw(x1, x2)
        return disance, path
    """

    #kalman filter, commented heavily for personal reference
    #todo: factor in estimation of acceleration 
    def kalmanfilter(self, x, y):
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
        F = np.array([[1.0, 0.0, self.PERIOD, 0.0, self.PERIOD*self.PERIOD / 2.0, 0.0], [0.0, 1.0, 0.0, self.PERIOD, 0.0, self.PERIOD*self.PERIOD / 2.0],
            [0.0, 0.0, 1.0, 0.0, self.PERIOD, 0.0], [0.0, 0.0, 0.0, 1.0, 0.0, self.PERIOD], [0.0, 0.0, 0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 0.0, 0.0, 1.0]])
        
        #measurement matrix, 
        #denoting that we're only taking measurements on position data
        H = np.array([[1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0, 0.0, 0.0]])

        #covariance of observation noise...based off of OPT's current implementation
        R = np.array([[0.5, 0.0], [0.0, 0.5]])
        
        #covariance of process noise 
        G = np.array([[self.PERIOD * self.PERIOD / 2.0], [self.PERIOD * self.PERIOD / 2.0], [self.PERIOD], [self.PERIOD], [1.0], [1.0]])
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

    #Take covariance-method PCA, get sort of 
    #most likely arrangement of people
    def pca(self):
        #take cov matrices & evals/evects
        xcov, ycov = self.covarianceind()
        ex, vx = np.linalg.eig(xcov)
        ey, vy = np.linalg.eig(ycov)

        #pair and sort the eigenvectors with respective eigenvalues
        expairs = [(np.abs(ex[i]), vx[:,i]) for i in range(len(ex))]
        eypairs = [(np.abs(ey[i]), vy[:,i]) for i in range(len(ex))]
        expairs.sort(key=lambda x: x[0], reverse=True)
        eypairs.sort(key=lambda x: x[0], reverse=True)

        #return greatest of each
        return expairs[0], eypairs[0]

    def run(self):
        plt.ion()
        plt.interactive(False)
        fig = plt.figure(figsize=(5,5))

        walkers = [ [random.randrange(200)-100, random.randrange(200)-100, self.Z_NOMINAL], 
            [random.randrange(200)-100, random.randrange(200)-100, self.Z_NOMINAL],
            [random.randrange(200)-100, random.randrange(200)-100, self.Z_NOMINAL],
            [random.randrange(200)-100, random.randrange(200)-100, self.Z_NOMINAL],
            [random.randrange(200)-100, random.randrange(200)-100, self.Z_NOMINAL],
            [random.randrange(200)-100, random.randrange(200)-100, self.Z_NOMINAL],
            [random.randrange(200)-100, random.randrange(200)-100, self.Z_NOMINAL],
            [random.randrange(200)-100, random.randrange(200)-100, self.Z_NOMINAL],
            [random.randrange(200)-100, random.randrange(200)-100, self.Z_NOMINAL],
            [random.randrange(200)-100, random.randrange(200)-100, self.Z_NOMINAL] ] 

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            while True:
                self.walk(walkers)
                MESSAGE = json.dumps( self.packet( [ self.track(42, walkers[0][0], walkers[0][1], walkers[0][2], self._SEQ+100+random.random(), random.random()),
                                                self.track(43, walkers[1][0], walkers[1][1], walkers[1][2], self._SEQ+100+random.random(), random.random()),
                                                self.track(44, walkers[2][0], walkers[2][1], walkers[2][2], self._SEQ+100+random.random(), random.random()),
                                                self.track(45, walkers[3][0], walkers[3][1], walkers[3][2], self._SEQ+100+random.random(), random.random()),
                                                self.track(46, walkers[4][0], walkers[4][1], walkers[4][2], self._SEQ+100+random.random(), random.random()),
                                                self.track(47, walkers[5][0], walkers[5][1], walkers[5][2], self._SEQ+100+random.random(), random.random()),
                                                self.track(48, walkers[6][0], walkers[6][1], walkers[6][2], self._SEQ+100+random.random(), random.random()),
                                                self.track(49, walkers[7][0], walkers[7][1], walkers[7][2], self._SEQ+100+random.random(), random.random()),
                                                self.track(50, walkers[8][0], walkers[8][1], walkers[8][2], self._SEQ+100+random.random(), random.random()),
                                                self.track(51, walkers[9][0], walkers[9][1], walkers[9][2], self._SEQ+100+random.random(), random.random())] )  )
            
                payload = bytes(MESSAGE.encode('utf-8')) + bytes(bytearray(100))
                sock.sendto(payload, (self.UDP_IP, self.UDP_PORT))
                
                #parse as generated
                msg = str(payload)
                end = msg.find("]}") + 2
                start = msg.find('{"header')

                trackingData = json.loads(msg[start:end])
                tracks = trackingData['tracks']
                trackData = []
                for singletrack in tracks:
                    trackData.append([singletrack['id'], singletrack['x'], singletrack['y'], singletrack['height']])

                #create/update list of ids
                allids = [singletrack[0] for singletrack in trackData]
                for singleID in allids:
                    if singleID not in self.ids:
                        self.ids.append(singleID)
                        self.parentList.append([singleID])
                        self.xdersList.append([singleID])
                        self.ydersList.append([singleID])
                        self.xseconddersList.append([singleID])
                        self.yseconddersList.append([singleID])
                
                #append each track to appropriate list
                for singleID in allids:
                    childList = []
                    for singletrack in trackData:
                        if(singletrack[0] == singleID):
                            del singletrack[0]
                            childList = singletrack
                    idx = self.ids.index(singleID)
                    self.parentList[idx].append(childList)

                    #take derivatives as generated
                    if len(self.parentList[idx]) > 2:
                        x = childList[0]
                        y = childList[1]
                        prevpoint = self.parentList[idx][len(self.parentList[idx])-2]
                        self.xdersList[idx].append((x-prevpoint[0])/self.PERIOD)
                        self.ydersList[idx].append((y-prevpoint[1])/self.PERIOD)
                        self.xseconddersList[idx].append(((self.xdersList[idx][0] - 
                            self.xdersList[idx-1][0])/self.PERIOD))
                        self.yseconddersList[idx].append(((self.ydersList[idx][1] - 
                            self.ydersList[idx-1][1])/self.PERIOD))
                        #ders.append((mx[i]-mx[i-1])/dt)
                
                currX = [point[0] for point in trackData]
                currY = [point[1] for point in trackData]

                currXY = []
                for x in range(10):
                    currXY.append([currX[x], currY[x]])

                #pairwise distances
                tempPairs = self.pairwise(currX, currY)

                #take upper triangular only, no redundant distances
                #tempPairsTriu = list(np.asarray(tempPairs)[np.triu_indices(len(currX),1)])
                self.pairs.append(tempPairs)

                self.allX.append(currX)
                self.allY.append(currY)

                #hot locations analysis on recent time window (can adjust)
                if(len(self.allX) > 100):
                    recentXY = []
                    for i in range(1, 100):
                        currentX = self.allX[len(self.allX)-i]
                        currentY = self.allY[len(self.allX)-i]
                        for j in range(len(currentX)):
                            recentXY.append([currentX[j], currentY[j]])

                af = AffinityPropagation().fit(recentXY)
                clusterCenters = af.cluster_centers_indices_
                labs = af.labels_
                nClusts = len(clusterCenters)
                hotSpots = []
                for i in range(nClusts):
                    hotSpots.append(recentXY[clusterCenters[i]])

                #get clusters
                af = AffinityPropagation().fit(currXY)
                clusterCenters = af.cluster_centers_indices_
                labs = af.labels_
                nClusts = len(clusterCenters) #push to save at each time step
                
                #cluster distances
                centers = []
                for i in range(nClusts):
                    centers.append(currXY[clusterCenters[i]])

                plt.clf()

                #plot paths & points
                for i in range(len(currX)):
                    plt.plot([item[i] for item in self.allX], [item[i] for item in self.allY], zorder=-1)
  
                plt.scatter(currX, currY, zorder=3)
                
                #plot clustering
                for k in range(nClusts):
                    classMems = labs == k
                    classMem = []
                    for t in classMems:
                        if isinstance(t, tuple):
                            for x in t:
                                classMem.append(x)
                        else:
                            classMem.append(t)
                    classMems = np.asarray(classMem)
                    currXY = np.asarray(currXY)
                    center = centers[k]
                    
                    """#image generation for shape recognition
                    x, y = currXY[classMems, 0], currXY[classMems, 1]
                    minx, miny = min(x), min(y)
                    if minx < 0 or miny < 0:
                        if minx <= miny:
                            for point in range(len(x)):
                                x[point] = x[point] + abs(minx)
                            for point in range(len(y)):
                                y[point] = y[point] + abs(minx)
                        if miny < minx:
                            for point in range(len(x)):
                                x[point] = x[point] + abs(miny)
                            for point in range(len(y)):
                                y[point] = y[point] + abs(miny)
                    maxx, maxy = max(x), max(y)
                    img = np.zeros((int(maxy)+1, int(maxx)+1))
                    for i in range(len(x)):
                        img[int(maxy)-int(y[i]), int(x[i])] = 1
                    plt.imsave('filename.png', img)
                    
                    Better method: calculate number of acute angles along convex hull 
                    """

                    #combine points
                    x, y = currXY[classMems, 0], currXY[classMems, 1]
                    combo = [] #push combo to save each cluster at each time step
                    for i in range(len(x)):
                        combo.append((x[i],y[i]))

                    #get shapes
                    pointColl = geometry.MultiPoint(combo)
                    convHull = pointColl.convex_hull
                    minx, miny, maxx, maxy = convHull.bounds
                    if len(x) > 2:
                        patch = PolygonPatch(convHull, fc='#999999', ec='#000000', fill=True, zorder=1)
                    ax = fig.add_subplot(111)
                    if len(x) > 2:
                        ax.add_patch(patch)

                    #label shapes
                    if len(x) > 2:
                        x, y = convHull.exterior.coords.xy
                        if len(x) == 4:
                            plt.text(centers[0] + 5, centers[1] + 5, r'triangle', fontdict={'size': 8})
                        if len(x) == 5:
                            plt.text(centers[0] + 5, centers[1] + 5, r'quad', fontdict={'size': 8})
                        if len(x) == 6:
                            plt.text(centers[0] + 5, centers[1] + 5, r'pentagon', fontdict={'size': 8})
                        if len(x) > 6:
                            plt.text(centers[0] + 5, centers[1] + 5, r'poly', fontdict={'size': 8})
                    plt.plot(centers[0], centers[1], 'y' + '*', zorder=4)
                    for x in currXY[classMems]:
                        plt.plot([centers[0], x[0]], [centers[1], x[1]], 'r' + '--', zorder=2)
                
                plt.axis([-250,250,-250,250])
                plt.pause(0.05)
            
                time.sleep(self.PERIOD)

        except KeyboardInterrupt:
            pass 
