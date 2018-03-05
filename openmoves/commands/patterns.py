import socket, time, json, random, fastdtw
import library.shorttime as shorttime
import library.supervised as supervised

from .base import Base

class Patterns(Base):
    """Seperate runnable for pattern computations as they are expensive"""
    def __init__(self, ops, *args, **kwargs):
        self.ops = ops
        self.args = args
        self.kwargs = kwargs

        self.ids = []
        self.parentList = []
        self.dtwdistances = []

    def run(self):
        epoch = 0
        s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s_in.bind(("", 21234))
        print("waiting on port:", 21234)
        
        try:
            while True:
                data, addr = s_in.recvfrom(8192)
                data = data.rstrip("\0")  
                payload = json.dumps(json.loads(data), sort_keys=True, indent=4, separators=(',', ': ') ) 

                #parse as generated
                msg = str(payload)

                trackingData = json.loads(msg)
            
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
                        self.ids.append(singleID)
                        self.parentList.append([[float('nan'), float('nan')]] * variables.epoch)
                        self.dtwdistances.append([])
                
                    #append each track to appropriate list
                    childList = []
                    for singletrack in trackData:
                        if(singletrack[0] == singleID):
                            del singletrack[0]
                            del singletrack[2]
                            childList = singletrack
                    idx = variables.ids.index(singleID)
                    variables.parentList[idx].append(childList)
               
                for singleID in variables.ids:
                    if singleID not in allids:
                        idx = variables.ids.index(singleID)
                        variables.parentList[idx].append([float('nan'), float('nan')])

                if variables.epoch % 50 == 0:
                    for singleID in allids:
                        idx = self.ids.index(singleID)
                        path = self.parentList[idx]
                        for singleID in allids:
                            idx2 = variables.ids.index(singleID)
                            otherpath = variables.parentList[idx2]
                            if path == otherpath:
                                continue
                            else:
                                self.dtwdistances[idx].append(shorttime.slidingdtw(path, otherpath, 20))

                supervised.readin("path")
                epoch = epoch + 1
