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
import library.supervised as supervised

from .base import Base

class Readin(Base):
    """Read in data from OPT, organize it and save to variables"""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs
        publishing.parse()
        supervised.readin("path")
        
        """
        plt.ion()
        plt.interactive(False)
        for i in range(len(variables.x_path)):
            plt.subplot(7, 7, i+1)
            plt.plot(variables.x_path[i], variables.y_path[i], zorder=3)

        plt.show()
        """

    def run(self):
        plt.ion()
        plt.interactive(False)
        fig = plt.figure(figsize=(5,5)) 

        s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        s_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_out.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8192)
        s_out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)

        s_in.bind(("", variables.UDP_PORT_IN))
        print("waiting on port:", variables.UDP_PORT_IN)

        heartbeat = 0
        
        try:
            while True:
                try:
                    variables.outofbounds = []
                    
                    if variables.visualize == 1:
                        plt.clf()
                        axes = plt.gca()
                        axes.set_xlim([variables.extents[0][0],variables.extents[1][0]])
                        axes.set_ylim([variables.extents[0][1],variables.extents[1][1]])
                    
                    data, addr = s_in.recvfrom(8192)
                    data = data.rstrip("\0")  
                    payload = json.dumps(json.loads(data), sort_keys=True, indent=4, separators=(',', ': ') ) 

                    #parse as generated
                    msg = str(payload)
                    trackingData = json.loads(msg)
                    variables.SEQ = trackingData['header']['seq']
                    if trackingData['header']['frame_id'] == 'heartbeat':
                        heartbeat = heartbeat + 1
                        variables.aliveIDs = trackingData['alive_IDs']
                        if heartbeat % 5 == 0:
                            for singleID in variables.ids:
                                if singleID not in variables.aliveIDs:
                                    idx = variables.ids.index(singleID)
                                    del variables.ids[idx]
                                    del variables.parentList[idx]
                                    del variables.xdersList[idx]
                                    del variables.ydersList[idx]
                                    del variables.xseconddersList[idx]
                                    del variables.yseconddersList[idx]
                                    del variables.orientations[idx]
                                    del variables.dtwdistances[idx]
                                    del variables.speeds[idx]
                                    del variables.accel[idx]
                                    del variables.predictions[idx]
                                    del variables.stagedists[idx]
                                    variables.currIDs.remove(singleID)
                        continue
                    
                    tracks = trackingData['people_tracks']
                    #print(tracks)

                    trackData = []
                    for singletrack in tracks:
                        if singletrack['x'] < variables.extents[0][0] or singletrack['x'] > variables.extents[1][0] or singletrack['y'] < variables.extents[0][1] or singletrack['y'] > variables.extents[1][1]: 
                            variables.outofbounds.append(singletrack['id'])
                        trackData.append([singletrack['id'], singletrack['x'], singletrack['y'], singletrack['height']])

                    #create/update list of IDs
                    variables.currIDs = variables.aliveIDs
                    allids = [singletrack[0] for singletrack in trackData]
                    for singleID in allids:
                        if singleID not in variables.ids:
                            variables.ids.append(singleID)
                            variables.parentList.append([])
                            variables.xdersList.append([])
                            variables.ydersList.append([])
                            variables.xseconddersList.append([])
                            variables.yseconddersList.append([])
                            variables.orientations.append([])
                            variables.dtwdistances.append([])
                            variables.stagedists.append([])
                            variables.speeds.append([])
                            variables.accel.append([])
                            variables.predictions.append([])
                    
                        #append each track to appropriate list
                        childList = []
                        for singletrack in trackData:
                            if(singletrack[0] == singleID):
                                del singletrack[0]
                                del singletrack[2]
                                childList = singletrack
                        idx = variables.ids.index(singleID)

                        if variables.parentList[idx] != [] and childList[0] == variables.parentList[idx][-1][0] and childList[1] == variables.parentList[idx][-1][1]:
                            elsum = [0, 0]
                            n = 15
                            if len(variables.parentList[idx]) < 15:
                                n = len(variables.parentList[idx])
                            for i, x in enumerate(variables.parentList[idx][-n:]):
                                elsum[0] = elsum[0] + x[0]
                                elsum[1] = elsum[1] + x[1]
                            elsum[0] = elsum[0] / n
                            elsum[1] = elsum[1] / n
                            variables.parentList[idx].append(elsum)
                        
                        else:
                            variables.parentList[idx].append(childList)

                        instantaneous.ders(idx)   
                        instantaneous.orientation(idx)  

                        if singleID not in variables.currIDs:
                            variables.currIDs.append(singleID)
                    
                    for singleID in variables.aliveIDs:
                        if singleID not in allids:
                            #if singleID not in variables.ids:
                            #    variables.currIDs.remove(singleID)
                            #    continue
                            idx = variables.ids.index(singleID)
                            elsum = [0, 0]
                            n = 15
                            if len(variables.parentList[idx]) < 15:
                                n = len(variables.parentList[idx])
                            for i, x in enumerate(variables.parentList[idx][-n:]):
                                elsum[0] = elsum[0] + x[0]
                                elsum[1] = elsum[1] + x[1]
                            elsum[0] = elsum[0] / n
                            elsum[1] = elsum[1] / n
                            variables.parentList[idx].append(elsum)
                            instantaneous.ders(idx)
                            instantaneous.orientation(idx)
                    
                    currX = []
                    currY = []
                    currXY = []
                    for singleID in variables.currIDs:
                        #if singleID not in variables.ids:
                        #    print("singleID: ", singleID)
                        #    print("current loop IDs: ", allids)
                        #    print("aliveIDs: ", variables.currIDs)
                        #    print("all saved IDs: ", variables.ids)
                        #    variables.currIDs.remove(singleID)
                        #    continue
                        idx = variables.ids.index(singleID)
                        currXY.append(variables.parentList[idx][-1])
                        currX.append(currXY[-1][0])
                        currY.append(currXY[-1][1])
                        variables.stagedists[idx].append(instantaneous.linedists(currXY[-1]))
                        if currX[-1] < variables.extents[0][0] or currX[-1] > variables.extents[1][0] or currY[-1] < variables.extents[0][1] or currY[-1] > variables.extents[1][1]:
                            del currXY[-1]
                            del currX[-1]
                            del currY[-1]

                    variables.allX.append(currX)
                    variables.allY.append(currY)

                    unsupervised.clusts2(currXY, variables.currIDs)
                    if variables.epoch % 100 == 0:
                        unsupervised.hotClusts2()

                    #pairwise distances
                    tempPairs = instantaneous.pairwise(currX, currY)

                    #take upper triangular only, no redundant distances
                    #tempPairsTriu = list(np.asarray(tempPairs)[np.triu_indices(len(currX),1)])
                    variables.pairs.append(tempPairs)
                    
                    if variables.epoch % 30 == 0:   
                        for singleID in variables.currIDs:
                            #if singleID not in variables.ids:
                            #    variables.currIDs.remove(singleID)
                            #    continue
                            idx = variables.ids.index(singleID)
                            path = variables.parentList[idx]
                            variables.predictions[idx].append(supervised.predict(path, singleID))
                        
                    for sigID in variables.outofbounds:
                        if sigID in variables.currIDs:
                            variables.currIDs.remove(sigID)
                    
                    if variables.epoch % 25 == 0:
                        doneids = []
                        for singleID in variables.currIDs:
                            idx = variables.ids.index(singleID)
                            if len(variables.parentList[idx]) > 150:
                                path = variables.parentList[idx][-150:]
                            else:
                                path = variables.parentList[idx]
                            variables.dtwdistances[idx] = []
                            for singleID2 in variables.currIDs:
                                idx2 = variables.ids.index(singleID2)
                                if singleID2 in doneids:
                                    sigidx = variables.currIDs.index(singleID)
                                    variables.dtwdistances[idx].append(variables.dtwdistances[idx2][sigidx])
                                    continue
                                if idx == idx2:
                                    variables.dtwdistances[idx].append(0)
                                    continue
                                if len(variables.parentList[idx]) > 150:
                                    otherpath = variables.parentList[idx2][-150:]
                                else:
                                    otherpath = variables.parentList[idx2]

                                variables.dtwdistances[idx].append(shorttime.doFastDTW(path, otherpath))
                            doneids.append(singleID)
                    

                    print(variables.numClusts[-1])

                    """
                    if variables.epoch % variables.pcarefresh == 0 and aliveids > 0:
                        #results ordered as: x1, y1, x2, y1,..., xn, yn
                        variables.e1 = []
                        variables.e2 = []
                        e1, e2 = unsupervised.pca()
                        e1 = list(e1)
                        e2 = list(e2)
                        e1[1] = e1[1].tolist()
                        e2[1] = e2[1].tolist()
                        variables.e1.append(e1)
                        variables.e1.append(e2)
                        """
                    """"
                    MESSAGE = publishing.derPacket()
                    print(MESSAGE)
                    payload = bytes(MESSAGE.encode('utf-8'))
                    s_out.sendto(payload, (variables.UDP_IP, variables.UDP_PORT_OUT))
                    
                    MESSAGE = publishing.distPacket()
                    print(MESSAGE)
                    payload = bytes(MESSAGE.encode('utf-8'))
                    s_out.sendto(payload, (variables.UDP_IP, variables.UDP_PORT_OUT))
                    
                    MESSAGE = publishing.distPacket2()
                    print(MESSAGE)
                    payload = bytes(MESSAGE.encode('utf-8'))
                    s_out.sendto(payload, (variables.UDP_IP, variables.UDP_PORT_OUT))

                    MESSAGE = publishing.clustPacket()
                    print(MESSAGE)
                    payload = bytes(MESSAGE.encode('utf-8'))
                    s_out.sendto(payload, (variables.UDP_IP, variables.UDP_PORT_OUT))
                    
                    MESSAGE = publishing.miscPacket()
                    print(MESSAGE)
                    payload = bytes(MESSAGE.encode('utf-8'))
                    s_out.sendto(payload, (variables.UDP_IP, variables.UDP_PORT_OUT))
                    
                    MESSAGE = publishing.simPacket()
                    print(MESSAGE)
                    payload = bytes(MESSAGE.encode('utf-8'))
                    s_out.sendto(payload, (variables.UDP_IP, variables.UDP_PORT_OUT))
                    """

                    """----------------------------------------"""

                    MESSAGE = json.dumps(publishing.packet())
                    payload = bytes(MESSAGE.encode('utf-8'))
                    s_out.sendto(payload, (variables.UDP_IP, variables.UDP_PORT_OUT))

                    MESSAGE = json.dumps(publishing.secondPacket())
                    payload = bytes(MESSAGE.encode('utf-8'))
                    s_out.sendto(payload, (variables.UDP_IP, variables.UDP_PORT_OUT))

                    if variables.visualize == 1:
                        visualize.pltPaths()
                        visualize.pltClustering(currXY)
                        visualize.pltShapes(fig)
                        plt.pause(0.000000000001)

                    if variables.epoch % 1000:
                        for i in range(len(variables.parentList)):
                            if len(variables.parentList[i]) > 1000:
                                variables.parentList[i] = variables.parentList[i][-1000:]
                                variables.xdersList[i] = variables.xdersList[i][-1000:]
                                variables.ydersList[i] = variables.ydersList[i][-1000:]
                                variables.xseconddersList[i] = variables.xseconddersList[i][-1000:]
                                variables.yseconddersList[i] = variables.yseconddersList[i][-1000:]
                                variables.orientations[i] = variables.orientations[i][-1000:]
                                variables.speeds[i] = variables.speeds[i][-1000:]
                                variables.accel[i] = variables.accel[i][-1000:]
                                variables.dtwdistances[i] = variables.dtwdistances[i][-1000:]
                                variables.stagedists[i] = variables.stagedists[i][-1000:]
                            if len(variables.predictions[i]) > 1000:    
                                variables.predictions[i] = variables.predictions[i][-1000:]

                        if len(variables.pairs) > 1000:
                            variables.pairs = variables.pairs[-1000:]

                        if len(variables.allX) > 1000:
                            variables.allX = variables.allX[-1000:]
                            variables.allY = variables.allY[-1000:]

                        if len(variables.e1) > 1000:
                            variables.e1 = variables.e1[-1000:]
                            variables.e2 = variables.e1[-1000:]

                        if len(variables.numClusts) > 1000:
                            variables.numClusts = variables.numClusts[-1000:]
                            variables.centers = variables.centers[-1000:]
                            variables.clusters = variables.clusters[-1000:]
                            variables.bounds = variables.bounds[-1000:]
                            variables.spreads = variables.spreads[-1000:]
                        
                        variables.epoch += 1
                except:
                    continue
        except KeyboardInterrupt:
            pass 

