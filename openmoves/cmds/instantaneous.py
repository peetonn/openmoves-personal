#from template import .template
import variables

#class instantaneous():
"""Instantaneous features module functionality"""

"""    def __init__(self, ops, *args, **kwargs):
        self.ops = ops
        self.args = args
        self.kwargs = kwargs
"""

def pairwise(X, Y):
    tempPairs = []
    if(len(X) > len(Y)):
        rng = len(Y)
    else:
        rng = len(X)

    for i in range(rng):
        jArr = []
        for j in range(rng):
            jArr.append(np.sqrt((X[j]-X[i])**2 + (Y[j]-Y[i])**2))
        tempPairs.append(jArr)
    
    return tempPairs

def ders(idx, childList):
    if len(variables.parentList[idx]) > 2:
        x = childList[0]
        y = childList[1]
        prevpoint = variables.parentList[idx][len(variables.parentList[idx])-2]
        variables.xdersList[idx].append((x-prevpoint[0])/variables.PERIOD)
        variables.ydersList[idx].append((y-prevpoint[1])/variables.PERIOD)
        variables.xseconddersList[idx].append(((variables.xdersList[idx][0] - 
            variables.xdersList[idx-1][0])/variables.PERIOD))
        variables.yseconddersList[idx].append(((variables.ydersList[idx][1] - 
            variables.ydersList[idx-1][1])/variables.PERIOD))