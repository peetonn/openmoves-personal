import socket, time, json, time, random
from sklearn.cluster import AffinityPropagation
import shapely.geometry as geometry
from descartes import PolygonPatch
import matplotlib.pyplot as plt
import numpy as np

import variables
import instantaneous

#from template import .template

class readin(): #template):
    """Read in data from OPT, organize it and save to variables"""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs

        self.port = 21234

    def run(self):
        plt.ion()
        plt.interactive(False)
        fig = plt.figure(figsize=(5,5)) 

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("", self.port))
        print "waiting on port:", self.port
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
                    if singleID not in variables.ids:
                        variables.ids.append(singleID)
                        variables.parentList.append([singleID])
                        variables.xdersList.append([singleID])
                        variables.ydersList.append([singleID])
                        variables.xseconddersList.append([singleID])
                        variables.yseconddersList.append([singleID])
                
                #append each track to appropriate list
                for singleID in allids:
                    childList = []
                    for singletrack in trackData:
                        if(singletrack[0] == singleID):
                            del singletrack[0]
                            childList = singletrack
                    idx = variables.ids.index(singleID)
                    variables.parentList[idx].append(childList)

                    instantaneous.ders(idx, childList)
                
                currX = [point[0] for point in trackData]
                currY = [point[1] for point in trackData]

                currXY = []
                for x in range(len(trackData)):
                    currXY.append([currX[x], currY[x]])

                #pairwise distances
                tempPairs = instantaneous.pairwise(currX, currY)

                #take upper triangular only, no redundant distances
                #tempPairsTriu = list(np.asarray(tempPairs)[np.triu_indices(len(currX),1)])
                variables.pairs.append(tempPairs)

                variables.allX.append(currX)
                variables.allY.append(currY)
            
                plt.pause(0.05)
                time.sleep(variables.PERIOD)

        except KeyboardInterrupt:
            pass 

