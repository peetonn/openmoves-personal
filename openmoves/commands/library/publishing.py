import variables, variables2, time, json, os, scipy.signal 

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
    variables2.extents = data["instantaneous"]["extents"]
    variables.stagedirs = data["instantaneous"]["stagedirs"]


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
    for cur in variables.aliveIDs:
        idx = variables.ids.index(cur)
        if len(variables.parentList[idx]) > 2 and variables.xdersList[idx][-1] is not None:
            firstdirs.append([variables.xdersList[idx][-1], variables.ydersList[idx][-1]])
            speeds.append(variables.speeds[idx][-1])
        if len(variables.parentList[idx]) > 3 and variables.xdersList[idx][-1] is not None:
            seconddirs.append([variables.xseconddersList[idx][-1], variables.yseconddersList[idx][-1]])
            accel.append(variables.accel[idx][-1])
    #print(speeds)
    #speeds = scipy.signal.medfilt(speeds)
    pairs = variables.pairs[-1]
    centers = variables.centers[-1]
    clusters = variables.clusters[-1]
    spreads = variables.spreads[-1]
    return {"header":header, "epoch": variables.epoch, "firstdirs":firstdirs, "seconddirs":seconddirs, "speeds": speeds, "accel":accel, "pairwise":pairs,  
        "clusters":clusters, "clustercenters":centers, "spreads":spreads, "stagedists":variables.stagedists[-1]} 

def secondPacket():
    now = float(time.time())
    sec = int(now)
    nsec = int((now-sec) * 1e9)
    hots = []
    header = {"seq":variables.SEQ, "stamp":{"sec":sec, "nsec":nsec}}
    return {"seq":variables.SEQ, "dtwdistances":[], "idorder": variables.ids, "aliveIDs":variables.aliveIDs, "hotspots":variables.hotSpots[:15], "pca1":[1,[1,2,3]], "pca2":[1,[1,2,3]]}

def patternPacket():
    return {"predictions": variables2.predictions}