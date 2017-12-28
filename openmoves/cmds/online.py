import socket, time, json, time, random
from sklearn.cluster import AffinityPropagation
import shapely.geometry as geometry
from descartes import PolygonPatch
import matplotlib.pyplot as plt
import numpy as np

from template import .template

class online(template):
    """Run while reading in from OPT."""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

        self.port = 21234

        self.parentList = []
        self.pairs = []
        self.ids = []
        self.dersList = []
        self.seconddersList = []

        self.allX = []
        self.allY = []

        self.dxt = []
        self.dyt = []
        self.ddxt = []
        self.ddyt = []

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

    def pca():
        pass

    def run(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("", port))
        print "waiting on port:", port
        try:
            while True:
                data, addr = s.recvfrom(8192)
                data = data.rstrip("\0")  
                payload = json.dumps(json.loads(data), sort_keys=True, indent=4, separators=(',', ': ') ) 

                plt.ion()
                plt.interactive(False)
                fig = plt.figure(figsize=(5,5))

                #parse as generated
                msg = str(payload)
                end = msg.find("]}") + 2
                start = msg.find('{"header')

                trackingData = json.loads(msg[start:end])
                tracks = trackingData['tracks']
                trackData = []
                for singletrack in tracks:
                    trackData.append([singletrack['id'], singletrack['x'], singletrack['y'], singletrack['height']])

                #create/update list of IDs
                allids = [singletrack[0] for singletrack in trackData]
                for singleID in allids:
                    if singleID not in ids:
                        ids.append(singleID)
                        parentList.append([singleID])
                        dersList.append([singleID])
                
                #append each track to appropriate list
                for singleID in allids:
                    childList = []
                    for singletrack in trackData:
                        if(singletrack[0] == singleID):
                            del singletrack[0]
                            childList = singletrack
                    idx = ids.index(singleID)
                    parentList[idx].append(childList)

                    #take derivatives as generated
                    if len(parentList[idx]) > 2:
                        x = childList[0]
                        y = childList[1]
                        prevpoint = parentList[idx][len(parentList[idx])-2]
                        dersList[idx].append((y - prevpoint[1])/(x-prevpoint[0]))
                        #ders.append((mx[i]-mx[i-1])/dt)
                
                currX = [point[0] for point in trackData]
                currY = [point[1] for point in trackData]

                currXY = []
                for x in range(10):
                    currXY.append([currX[x], currY[x]])

                allX.append(currX)
                allY.append(currY)

                #get clusters
                af = AffinityPropagation().fit(currXY)
                clusterCenters = af.cluster_centers_indices_
                labs = af.labels_
                nClusts = len(clusterCenters)
                
                plt.clf()

                #plot paths & points
                for i in range(10):
                    plt.plot([item[i] for item in allX], [item[i] for item in allY], zorder=-1)
  
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
                    centers = currXY[clusterCenters[k]]
                    
                    """#image generation
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
                    plt.imsave('filename.png', img)"""

                    #combine points
                    x, y = currXY[classMems, 0], currXY[classMems, 1]
                    combo = []
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
            
                time.sleep(PERIOD)

        except KeyboardInterrupt:
            pass 

