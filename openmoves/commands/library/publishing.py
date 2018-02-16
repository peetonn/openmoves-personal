import variables, time, json

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
    for i in len(variables.ids):
        if len(variables.xdersList[i]) == variables.epoch:
            firstdirs.append({"id":variables.ids[i], "x":variables.xdersList[i], "y":variables.ydersList[i]})
            seconddirs.append({"id":variables.ids[i], "x":variables.xseconddersList[i], "y":variables.yseconddersList[i]})
    pairs = variables.pairs[-1]
    centers = variables.centers[-1]
    clusters = variables.clusters[-1]
    return {"header":header, "firstdirs":firstdirs, "seconddirs":seconddirs, "pairwise":pairs, \
        "clusters":clusters, "clustercenters":centers}


