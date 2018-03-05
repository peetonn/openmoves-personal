# -*- coding: utf-8 -*-
import socket, time, json, random, fastdtw
import shapely.geometry as geometry
from descartes import PolygonPatch
import matplotlib.pyplot as plt
import numpy as np

import library.variables as variables
import library.instantaneous as instantaneous
import library.publishing as publishing
import library.unsupervised as unsupervised
import library.visualization as visualize
import library.shorttime as shorttime

from .base import Base

class Readin(Base):
    """Read in data from OPT, organize it and save to variables"""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs
        publishing.parse()

    def run(self):
        plt.ion()
        plt.interactive(False)
        fig = plt.figure(figsize=(5,5)) 

        s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s_in.bind(("", variables.UDP_PORT_IN))
        print("waiting on port:", variables.UDP_PORT_IN)

        aliveids = 0
        
        try:
            while True:
                if variables.visualize == 1:
                    plt.clf()
                data, addr = s_in.recvfrom(8192)
                data = data.rstrip("\0")  
                payload = json.dumps(json.loads(data), sort_keys=True, indent=4, separators=(',', ': ') ) 

                #parse as generated
                msg = str(payload)

                trackingData = json.loads(msg)
                variables.SEQ = trackingData['header']['seq']
                if trackingData['header']['frame_id'] == 'heartbeat':
                    aliveids = len(trackingData['alive_IDs'])
                    variables.aliveIDs = trackingData['alive_IDs']
                    continue
                
                tracks = trackingData['people_tracks']
                if tracks == []:
                    continue

                trackData = []
                for singletrack in tracks:
                    trackData.append([singletrack['id'], singletrack['x'], singletrack['y'], singletrack['height']])

                #create/update list of IDs
                allids = [singletrack[0] for singletrack in trackData]
                for singleID in allids:
                    if singleID not in variables.ids:
                        variables.ids.append(singleID)
                        variables.parentList.append([[float('nan'), float('nan')]] * variables.epoch)
                        variables.xdersList.append([float('nan')] * variables.epoch)
                        variables.ydersList.append([float('nan')] * variables.epoch)
                        variables.xseconddersList.append([float('nan')] * variables.epoch)
                        variables.yseconddersList.append([float('nan')] * variables.epoch)
                        variables.orientations.append([float('nan')] * variables.epoch)
                        variables.dtwdistances.append([])
                
                    #append each track to appropriate list
                    childList = []
                    for singletrack in trackData:
                        if(singletrack[0] == singleID):
                            del singletrack[0]
                            del singletrack[2]
                            childList = singletrack
                    idx = variables.ids.index(singleID)
                    variables.parentList[idx].append(childList)

                    instantaneous.ders(idx, childList)
               
                for singleID in variables.ids:
                    if singleID not in allids:
                        idx = variables.ids.index(singleID)
                        variables.parentList[idx].append([float('nan'), float('nan')])
                        variables.xdersList[idx].append(float('nan'))
                        variables.ydersList[idx].append(float('nan'))
                        variables.xseconddersList[idx].append(float('nan'))
                        variables.yseconddersList[idx].append(float('nan'))
                        variables.orientations[idx].append(float('nan'))
                
                currX = [point[0] for point in trackData]
                currY = [point[1] for point in trackData]

                currXY = []
                for x in range(len(trackData)):
                    currXY.append([currX[x], currY[x]])

                unsupervised.clusts(currXY)
                unsupervised.hotClusts()

                #pairwise distances
                tempPairs = instantaneous.pairwise(currX, currY)

                #take upper triangular only, no redundant distances
                #tempPairsTriu = list(np.asarray(tempPairs)[np.triu_indices(len(currX),1)])
                variables.pairs.append(tempPairs)
                """
                if variables.epoch % 50 == 0:
                    #doneids = []
                    for singleID in allids:
                        idx = variables.ids.index(singleID)
                        path = variables.parentList[idx]
                        #variables.dtwdistances[idx] = []
                        for singleID in allids:
                            #if singleID in doneids:
                            #    continue
                            idx2 = variables.ids.index(singleID)
                            otherpath = variables.parentList[idx2]
                            if path == otherpath:
                                continue
                            else:
                                #distance = shorttime.doFastDTW(path, otherpath)
                                variables.dtwdistances[idx].append(shorttime.slidingdtw(path, otherpath, 20))
                                #variables.dtwdistances[idx].append(distance)
                        #doneids.append(singleID)
                """
                
                if variables.visualize == 1:
                    variables.allX.append(currX)
                    variables.allY.append(currY)
                
                variables.epoch += 1

                """if variables.epoch % variables.pcarefresh == 0 and aliveids > 1:
                    #results ordered as: x1, y1, x2, y1,..., xn, yn
                    variables.e1 = []
                    variables.e2 = []
                    e1, e2 = unsupervised.pca()
                    e1 = list(e1)
                    e2 = list(e2)
                    e1[1] = e1[1].tolist()
                    e2[1] = e2[1].tolist()
                    variables.e1.append(e1)
                    variables.e1.append(e2)"""

                MESSAGE = json.dumps(publishing.packet())
                payload = bytes(MESSAGE.encode('utf-8')) + bytes(bytearray(100))
                s_out.sendto(payload, (variables.UDP_IP, variables.UDP_PORT_OUT))

                MESSAGE = json.dumps(publishing.secondPacket())
                payload = bytes(MESSAGE.encode('utf-8')) + bytes(bytearray(100))
                s_out.sendto(payload, (variables.UDP_IP, variables.UDP_PORT_OUT))

                if variables.visualize == 1:
                    visualize.pltPaths()
                    visualize.pltClustering()
                    visualize.pltShapes(fig)
                    plt.pause(0.000000000001)

        except KeyboardInterrupt:
            pass 

