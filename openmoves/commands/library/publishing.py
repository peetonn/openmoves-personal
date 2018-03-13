import variables, time, json, os, scipy.signal 
from collections import OrderedDict

def parse():
    """function to parse the config file"""
    fn = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
    with open(fn) as data_file:
        data = json.load(data_file)
    variables.visualize = data["visualize"]
    variables.trackheight = data["trackheight"]
    variables.shorttimespan = data["shorttime"]["shorttime"]
    variables.shortwindow = data["shorttime"]["windowsize"]
    variables.dtwrefresh = data["shorttime"]["dtwrefresh"]
    variables.dtwwindows = data["shorttime"]["dtwwindows"]
    variables.pois = data["instantaneous"]["pois"]
    variables.stagepts = data["instantaneous"]["stagepts"]
    variables.shortclusterwindow = data["unsupervised"]["shortclusterwindowsize"]
    variables.hotspotwindow = data["unsupervised"]["hotspotwindowsize"]
    variables.pcarefresh = data["unsupervised"]["pcarefresh"]
    variables.extents = data["instantaneous"]["extents"]
    variables.stagedirs = data["instantaneous"]["stagedirs"]

"""{
    "packet" : { "type":"openmoves", "version":1, "subtype": "derivatives" },
    "header" : {"seq":1234, "stamp":{"sec":11234, "nsec":11234}},
    "ids" : [14, 23],
    "dims" : 3,
    "values" : {
        "d1": [ [0.12, 0.23, 0.45],} [2.30, 22.1, 43.1] ],
        "d2": [ ... ]
        "speed": [ 0.55, 12.3 ],
        "acceleration" : [ 2.0, 4.4 ]
        }
}"""
def derPacket():
    now = float(time.time())
    sec = int(now)
    nsec = int((now-sec) * 1e9)

    firstdirs = []
    seconddirs = []
    speeds = []
    accel = []

    #what about orientation
    for cur in variables.currIDs:
        idx = variables.ids.index(cur)
        if len(variables.parentList[idx]) > 2 and variables.xdersList[idx][-1] is not None:
            firstdirs.append([round(variables.xdersList[idx][-1], 3), round(variables.ydersList[idx][-1], 3)])
            speeds.append(round(variables.speeds[idx][-1], 3))
        if len(variables.parentList[idx]) > 3 and variables.xdersList[idx][-1] is not None:
            seconddirs.append([round(variables.xseconddersList[idx][-1], 3), round(variables.yseconddersList[idx][-1], 3)])
            accel.append(round(variables.accel[idx][-1], 3))

    return json.dumps({"packet": {"type": "openmoves", "version": 1, "subtype": "derivatives"}, "header": {"seq":variables.SEQ, "stamp":{"sec":sec, "nsec":nsec}}, "ids": variables.currIDs, "dims": 2, 
        "values":{"d1": firstdirs, "d2": seconddirs, "speed": speeds, "acceleration": accel}}, indent=4, separators=(',', ': '))

"""{
    "packet" : { "type":"openmoves", "version":1, "subtype": "pairdistance" },
    "header" : {"seq":1234, "stamp":{"sec":11234, "nsec":11234}},
    "ids" : [14, 23],
    "dims" : 3,
    "values" : {
        "pairwise": [],
        "stage": {},
        "poi" : {}
        }
}"""  
def distPacket():
    now = float(time.time())
    sec = int(now)
    nsec = int((now-sec) * 1e9)
    
    pairs = variables.pairs[-1]
    roundedPairs = []
    for pairlist in pairs:
        rounded = [round(elem, 3) for elem in pairlist]
        roundedPairs.append(rounded)

    return json.dumps({"packet":{"type":"openmoves", "version":1, "subtype": "pairdistance"}, "header": {"seq":variables.SEQ, "stamp":{"sec":sec, "nsec":nsec}}, "ids": variables.currIDs, "dims": 2, 
        "values":{"pairwise": roundedPairs}}, indent=4, separators=(',', ': '))

"""{
    "packet" : { "type":"openmoves", "version":1, "subtype": "stagedistance" },
    "header" : {"seq":1234, "stamp":{"sec":11234, "nsec":11234}},
    "ids" : [14, 23],
    "dims" : 3,
    "values" : {
        "pairwise": [],
        "stage": {},
        "poi" : {}
        }
}"""  
def distPacket2():
    now = float(time.time())
    sec = int(now)
    nsec = int((now-sec) * 1e9)

    stagedists = []
    for cur in variables.currIDs:
        idx = variables.ids.index(cur)
        stagedists.append(variables.stagedists[idx][-1])#[round(elem,3) for elem in variables.stagedists[idx][-1]])
        
    return json.dumps({"packet":{"type":"openmoves", "version":1, "subtype": "stagedistance"}, "header": {"seq":variables.SEQ, "stamp":{"sec":sec, "nsec":nsec}}, "ids": variables.currIDs, "dims": 2, 
        "values":{"stage": stagedists, "poi": []}}, indent=4, separators=(',', ': '))

"""{
    "packet" : { "type":"openmoves", "version":1, "subtype": "cluster" },
    "header" : {"seq":1234, "stamp":{"sec":11234, "nsec":11234}},    
    "ids" : [14, 23],
    "dims" : 3,
    "values" : {
        "center": [],
        "cluster" : [],
        "spread": []
        }
}"""
def clustPacket():
    now = float(time.time())
    sec = int(now)
    nsec = int((now-sec) * 1e9)

    centers = variables.centers[-1]
    clusters = variables.clusters[-1]
    spreads = variables.spreads[-1]

    roundedCenters = []
    for center in centers:
        newCenter = []

    return json.dumps({"packet":{"type":"openmoves", "version":1, "subtype": "cluster"}, "header": {"seq":variables.SEQ, "stamp":{"sec":sec, "nsec":nsec}}, "ids": variables.currIDs, "dims": 2, 
        "values":{"center": centers, "cluster": clusters, "spread": spreads}}, indent=4, separators=(',', ': '))

"""{
    "packet" : { "type":"openmoves", "version":1, "subtype": "massdynamics" },
    "header" : {"seq":1234, "stamp":{"sec":11234, "nsec":11234}},    
    "ids" : [14, 23],
    "dims" : 3,
    "values" : {
        "hotspot": []
        "trend": []
        }
}"""
def miscPacket():
    now = float(time.time())
    sec = int(now)
    nsec = int((now-sec) * 1e9)
    
    return json.dumps({"packet":{"type":"openmoves", "version":1, "subtype": "massdynamics"}, "header": {"seq":variables.SEQ, "stamp":{"sec":sec, "nsec":nsec}}, "ids": variables.currIDs, "dims": 2, 
        "values":{"hotspot":variables.hotSpots, "trend":{"eigenvalue": 1, "eigenvector": [1,2,3]}}}, indent=4, separators=(',', ': '))

"""{
    "packet" : { "type":"openmoves", "version":1, "subtype": "similarity" },
    "header" : {"seq":1234, "stamp":{"sec":11234, "nsec":11234}},    
    "ids" : [14, 23],
    "dims" : 3,
    "values" : {
        "similarity": [],
        "predictions": [],
        }
}"""
def simPacket():
    now = float(time.time())
    sec = int(now)
    nsec = int((now-sec) * 1e9)

    distances = []
    predictions = []
    for cur in variables.currIDs:
        idx = variables.ids.index(cur)
        distances.append(variables.dtwdistances[idx])
        predictions.append(variables.predictions[idx][-1])
    
    return json.dumps({"packet":{"type":"openmoves", "version":1, "subtype": "similarity"}, "header": {"seq":variables.SEQ, "stamp":{"sec":sec, "nsec":nsec}}, "ids": variables.currIDs, "dims": 2, 
        "values":{"similarity": distances, "predictions": predictions}}, indent=4, separators=(',', ': '))

"""-----------------------------------------------------"""
def packet():
    """
    packet design:
            {"header":{"seq":(from OPT),"stamp":{"sec":1441244414,"nsec":266356327}},
                "firstdirs":[{"id":170,"x":0.740519,"y":-3.21577},{"id":172,"x":0.843167,"y":-3.29433}],
                "seconddirs:[{"id":170,"x":0.740519,"y":-3.21577},{"id":172,"x":0.843167,"y":-3.29433}],
                "pairwise":[[12.3,12.3,12.3,12.3,12.3,12.3],[12.3,12.3,12.3,12.3,12.3,12.3],...,[12.3,12.3,12.3,12.3,12.3,12.3]],
                "clusters":[[[1,2],[1,2],...,[1,2]],[[1,2],[1,2],...,[1,2]],...,[[1,2],[1,2],...,[1,2]]],
                "clustercenters": [[1,2],[1,2],[1,2],[1,2],..,[1,2]],...}
    all arrays formatted arr[col][row]
    """
    now = float(time.time())
    sec = int(now)
    nsec = int((now-sec) * 1e9)
    header = {"seq":variables.SEQ, "stamp":{"sec":sec, "nsec":nsec}}
    
    firstdirs = []
    seconddirs = []
    speeds = []
    accel = []
    stagedists = []

    for cur in variables.currIDs:
        idx = variables.ids.index(cur)
        if len(variables.parentList[idx]) > 2 and variables.xdersList[idx][-1] is not None:
            firstdirs.append([variables.xdersList[idx][-1], variables.ydersList[idx][-1]])
            speeds.append(variables.speeds[idx][-1])
        if len(variables.parentList[idx]) > 3 and variables.xdersList[idx][-1] is not None:
            seconddirs.append([variables.xseconddersList[idx][-1], variables.yseconddersList[idx][-1]])
            accel.append(variables.accel[idx][-1])
        try:
            stagedists.append(variables.stagedists[idx][-1])
        except:
            stagedists = []

    pairs = variables.pairs[-1]
    centers = variables.centers[-1]
    clusters = variables.clusters[-1]
    spreads = variables.spreads[-1]
    return {"header":header, "epoch": variables.epoch, "firstdirs":firstdirs, "seconddirs":seconddirs, "speeds": speeds, "accel":accel, "pairwise":pairs,  
        "clusters":clusters, "clustercenters":centers, "spreads":spreads, "stagedists":stagedists} 

def secondPacket():
    now = float(time.time())
    sec = int(now)
    nsec = int((now-sec) * 1e9)

    distances = []
    predictions = []
    for cur in variables.currIDs:
        idx = variables.ids.index(cur)
        distances.append(variables.dtwdistances[idx])
        predictions.append(variables.predictions[idx][-1])

    header = {"seq":variables.SEQ, "stamp":{"sec":sec, "nsec":nsec}}
    return {"seq":variables.SEQ, "pathsimilarity":distances, "idorder": variables.currIDs, "aliveIDs":variables.aliveIDs, "hotspots":variables.hotSpots[:15], "pca1":[1,[1,2,3]], "pca2":[1,[1,2,3]]}

def patternPacket():
    return {"predictions": variables.predictions}