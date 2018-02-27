from __future__ import print_function #can be ignored removed, used to supress an error in my particular editor

import socket, time, json, time, random
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
                #end = msg.find("]}") + 2
                #start = msg.find('{"header')

                trackingData = json.loads(msg)#[start:end])
                variables.SEQ = trackingData['header']['seq']
                if trackingData['header']['frame_id'] == 'heartbeat':
                    aliveids = len(trackingData['alive_IDs'])
                    print(aliveids)
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
                        variables.parentList.append([[float('inf'), float('inf')]] * variables.epoch)
                        variables.xdersList.append([float('inf')] * variables.epoch)
                        variables.ydersList.append([float('inf')] * variables.epoch)
                        variables.xseconddersList.append([float('inf')] * variables.epoch)
                        variables.yseconddersList.append([float('inf')] * variables.epoch)
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
                        variables.parentList[idx].append([float('inf'), float('inf')])
                        variables.xdersList[idx].append(float('inf'))
                        variables.ydersList[idx].append(float('inf'))
                        variables.xseconddersList[idx].append(float('inf'))
                        variables.yseconddersList[idx].append(float('inf'))
                
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

                if variables.epoch % 50 == 0:
                    for singleID in allids:
                        idx = variables.ids.index(singleID)
                        path = variables.parentList[idx]
                        variables.dtwdistances[idx] = []
                        for singleID in allids:
                            idx2 = variables.ids.index(singleID)
                            otherpath = variables.parentList[idx2]
                            if path == otherpath:
                                continue
                            else:
                                distance = shorttime.dtw(path, otherpath, variables.shortwindow)
                                variables.dtwdistances[idx].append(distance)

                variables.allXY.append(currXY)
                variables.allX.append(currX)
                variables.allY.append(currY)
                variables.epoch += 1

                if variables.epoch % variables.pcarefresh == 0 and aliveids > 1:
                    variables.expair = []
                    variables.eypair = []
                    expair, eypair = unsupervised.pca()
                    expair = list(expair)
                    eypair = list(eypair)
                    expair[1] = expair[1].tolist()
                    eypair[1] = eypair[1].tolist()
                    variables.expair.append(expair)
                    variables.eypair.append(eypair)

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

