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
        lastAssess = 0
        s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #s_out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        supervised.readin("path")

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

                if trackingData['header']['frame_id'] == 'heartbeat':
                    aliveids = len(trackingData['alive_IDs'])
                    continue

                tracks = trackingData['people_tracks']
                if tracks == []:
                    continue

                trackData = []
                for singletrack in tracks:
                    if singletrack['x'] < variables2.extents[0][0] or singletrack['x'] > variables2.extents[1][0] or singletrack['y'] < variables2.extents[0][1] or singletrack['y'] > variables2.extents[1][1]:
                        continue
                    trackData.append([singletrack['id'], singletrack['x'], singletrack['y'], singletrack['height']])

                #create/update list of IDs
                allids = [singletrack[0] for singletrack in trackData]
                for singleID in allids:
                    if singleID not in self.ids:
                        self.ids.append(singleID)
                        self.parentList.append([[float('nan'), float('nan')]] * epoch)
                        self.dtwdistances.append([])
                
                    #append each track to appropriate list
                    childList = []
                    for singletrack in trackData:
                        if(singletrack[0] == singleID):
                            del singletrack[0]
                            del singletrack[2]
                            childList = singletrack
                    idx = self.ids.index(singleID)
                    self.parentList[idx].append(childList)
               
                for singleID in self.ids:
                    if singleID not in allids:
                        idx = self.ids.index(singleID)
                        self.parentList[idx].append([float('nan'), float('nan')])

                """if epoch % 50 == 0:
                    for singleID in allids:
                        idx = self.ids.index(singleID)
                        path = self.parentList[idx]
                        for singleID in allids:
                            idx2 = self.ids.index(singleID)
                            otherpath = self.parentList[idx2]
                            if path == otherpath:
                                continue
                            else:
                                self.dtwdistances[idx].append(shorttime.slidingdtw(path, otherpath, 20))
                """
                if epoch % 450 == 0:
                    supervised.readin("path")

                if epoch % 30 == 0:   
                    for singleID in allids:
                        idx = self.ids.index(singleID)
                        path = self.parentList[idx]
                        #print("enter predict")
                        supervised.predict(path, singleID)

                epoch = epoch + 1
        
        except KeyboardInterrupt:
            pass 