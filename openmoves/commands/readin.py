import socket, time, json, time, random
import shapely.geometry as geometry
from descartes import PolygonPatch
import matplotlib.pyplot as plt
import numpy as np

import library.variables as variables
import library.instantaneous as instantaneous
import library.publishing as publishing

from .base import Base

class Readin(Base):
    """Read in data from OPT, organize it and save to variables"""

    def __init__(self, options, *args, **kwargs):
        self.options = options
        self.args = args
        self.kwargs = kwargs
        variables.parse()

    def run(self):
        plt.ion()
        plt.interactive(False)
        fig = plt.figure(figsize=(5,5)) 

        s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s_in.bind(("", variables.UDP_PORT_IN))
        #print("waiting on port:", self.port)
        
        try:
            while True:
                plt.clf()
                data, addr = s_in.recvfrom(8192)
                data = data.rstrip("\0")  
                payload = json.dumps(json.loads(data), sort_keys=True, indent=4, separators=(',', ': ') ) 

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
                        variables.parentList.append([[float('inf'), float('inf'), float('inf')]] * variables.epoch)
                        variables.xdersList.append([[float('inf'), float('inf'), float('inf')]] * variables.epoch)
                        variables.ydersList.append([[float('inf'), float('inf'), float('inf')]] * variables.epoch)
                        variables.xseconddersList.append([[float('inf'), float('inf'), float('inf')]] * variables.epoch)
                        variables.yseconddersList.append([[float('inf'), float('inf'), float('inf')]] * variables.epoch)
                
                    #append each track to appropriate list
                    childList = []
                    for singletrack in trackData:
                        if(singletrack[0] == singleID):
                            del singletrack[0]
                            childList = singletrack
                    idx = variables.ids.index(singleID)
                    variables.parentList[idx].append(childList)

                    instantaneous.ders(idx, childList)
               
                for singleID in variables.ids:
                    if singleID not in allids:
                        idx = variables.ids.index(singleID)
                        variables.parentList[idx].append([float('inf'), float('inf'), float('inf')])
                        variables.xdersList[idx].append([float('inf'), float('inf'), float('inf')])
                        variables.ydersList[idx].append([float('inf'), float('inf'), float('inf')])
                        variables.xseconddersList[idx].append([float('inf'), float('inf'), float('inf')])
                        variables.yseconddersList[idx].append([float('inf'), float('inf'), float('inf')])
                
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

                variables.allXY.append(currXY)
                variables.allX.append(currX)
                variables.allY.append(currY)
                variables.epoch += 1

                MESSAGE = json.dumps(publishing.packet())
                payload = bytes(MESSAGE.encode('utf-8')) + bytes(bytearray(100))
                s_out.sendto(payload, (variables.UDP_IP, variables.UDP_PORT_OUT))

                plt.pause(0.05)
                time.sleep(variables.PERIOD)

        except KeyboardInterrupt:
            pass 

