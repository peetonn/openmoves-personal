import variables
import numpy as np
from sklearn.cluster import AffinityPropagation
from sklearn.cluster import MeanShift, estimate_bandwidth
from sklearn.cluster import DBSCAN
from sklearn.cluster import Birch
from scipy import linalg
from scipy.spatial import distance
import shapely.geometry as geometry
from descartes import PolygonPatch

"""Unsupervised analysis module"""
#create an interpolated covariance matrix w/o nans?
def covariance(): #deprecated
    #ignore entries of resulting matrix with indicies not both odd or even
    #create a matrix such that each column is the x or y of a particular actor
    allXY = []
    for i in range(len(variables.allX)):
        currentX = variables.allX[i]
        currentY = variables.allY[i]
        recentXY = []
        for j in range(len(currentX)):
            recentXY.append(currentX[j])
            recentXY.append(currentY[j])
        allXY.append(recentXY)
    cov = np.cov(allXY)

    #now filter out x-to-y and y-to-x covariances
    m, n = cov.shape
    truecov = []
    for i in range(m): #rows
        currrow = []
        for j in range(n): #columns
            if i%2==0 and j%2==0:
                currrow.append(cov[i, j])
            elif i%2!=0 and j%2!=0:
                currrow.append(cov[i, j])
        truecov.append(currrow)
    return truecov

def covarianceind(): #deprecated
    covX = np.cov(np.asarray(variables.allX).T)
    covY = np.cov(np.asarray(variables.allY).T)

    return covX, covY

def pca():
    #take cov matrices & evals/evects
    #xcov, ycov = covarianceind()
    #ex, vx = np.linalg.eig(xcov)
    #ey, vy = np.linalg.eig(ycov)
    #print(variables.parentList)
    #print("-------***-------")
    #print("***-----------------***")
    #print(variables.parentList)
    #parlist = filter(None, variables.parentList)
    #print("--------------------------")
    #print(parlist)

    #parlist = np.asarray(parlist)
    #parlist = parlist[np.logical_not(np.isnan(parlist))]
    lists = []
    shortest = float('inf')
    for sigid in variables.currIDs:
        idx = variables.ids.index(sigid)
        if len(variables.parentList[idx]) < 5:
            continue 
        if len(variables.parentList[idx]) < shortest:
            shortest = len(variables.parentList[idx])
        lists.append(variables.parentList[idx])
    
    splitLists = []
    for i in range(len(lists)):
        lists[i] = lists[i][-shortest:]
        splitLists.append([element[0] for element in lists[i]])
        splitLists.append([element[1] for element in lists[i]])

    print("---------------------------")
    print(np.asarray(splitLists))
    if splitLists == []:
        return [], []
    covs = np.cov(np.asarray(splitLists))
    print("---------------------------")
    print(covs)
    ea, va = np.linalg.eig(covs)
    print("---------------------------")

    #pair and sort the eigenvectors with respective eigenvalues
    #expairs = [(np.abs(ex[i]), vx[:,i]) for i in range(len(ex))]
    #eypairs = [(np.abs(ey[i]), vy[:,i]) for i in range(len(ex))]
    #expairs.sort(key=lambda x: x[0], reverse=True)
    #eypairs.sort(key=lambda x: x[0], reverse=True)
    eapairs = [(np.abs(ea[i]), va[:,i]) for i in range(len(ea))]
    eapairs.sort(key=lambda x: x[0], reverse=True)

    #return greatest of each
    return eapairs[0], eapairs[1]

def hotClusts(): 
    #hot locations analysis on recent time window (can adjust)
    if(len(variables.allX) > variables.hotspotwindow):
        recentXY = []
        for i in range(1, variables.hotspotwindow):
            currentX = variables.allX[-i]
            currentY = variables.allY[-i]
            for j in range(len(currentX)):
                    recentXY.append([currentX[j], currentY[j]])

        af = AffinityPropagation().fit(recentXY)
        clusterCenters = af.cluster_centers_indices_

        if clusterCenters is None:
            nClusts = 0
        else:
            nClusts = len(clusterCenters)
        variables.hotSpots = []
        for i in range(nClusts):
            if recentXY[clusterCenters[i]] not in variables.hotSpots:
                variables.hotSpots.append(recentXY[clusterCenters[i]])

def hotClusts2():
    #hot locations analysis on recent time window (can adjust)
    if(len(variables.allX) > variables.hotspotwindow):
        recentXY = []
        for i in range(1, variables.hotspotwindow):
            currentX = variables.allX[-i]
            currentY = variables.allY[-i]
            for j in range(len(currentX)):
                    recentXY.append([currentX[j], currentY[j]])
        if recentXY == []:
            return
 
        af = MeanShift(bandwidth=1, bin_seeding=True).fit(recentXY)
        clusterCenters = af.cluster_centers_
        if clusterCenters is None:
            nClusts = 0
        else:
            nClusts = len(clusterCenters)
        variables.hotSpots = []
        for i in range(nClusts):
            variables.hotSpots.append(clusterCenters[i].tolist())

#experimenting with different clustering techniques
def clusts2(currXY, allids):
    #get clusters
    if len(currXY) < 2:
        variables.numClusts.append(len(currXY))
        variables.clusters.append([allids[0], currXY[0][0], currXY[0][1]])
        variables.bounds.append(currXY)
        variables.spreads.append([0])
        variables.centers.append(currXY)
        return
    #bandwidth = estimate_bandwidth(currXY, n_samples=len(currXY))
    ms = MeanShift(bandwidth=1, bin_seeding=True)
    ms.fit(currXY)
    labels = ms.labels_
    cluster_centers = ms.cluster_centers_ #_indices_
    if cluster_centers is None:
        nClusts = 0
    else:
        nClusts = len(cluster_centers)
    variables.numClusts.append(nClusts)
    centers = []
    for i in range(nClusts):
        centers.append(cluster_centers[i].tolist())
    variables.centers.append(centers)

    currClusters = []
    currBounds = []
    currSpreads = []
    for k in range(nClusts):
        classMems = labels == k
        classMem = []
        for t in classMems:
            if isinstance(t, tuple):
                for x in t:
                    classMem.append(x)
            else:
                classMem.append(t)
        classMems = np.asarray(classMem)
        currXY = np.asarray(currXY)
        center = centers[k]

        #combine points
        ids = []
        for j in range(len(classMems)):
            if classMems[j] == True:
                ids.append(allids[j])
        x, y = currXY[classMems, 0], currXY[classMems, 1]
        combo = [] #push combo to save each cluster at each time step
        for i in range(len(x)):
            combo.append((ids[i], x[i], y[i]))
        currClusters.append(combo)

        #bounds
        pointColl = geometry.MultiPoint(combo)
        convHull = pointColl.convex_hull
        minx, miny, maxx, maxy = convHull.bounds
        currBounds.append([minx, miny, maxx, maxy])

        #spreads
        dists = []
        for j in range(len(combo)):
            dists.append(distance.euclidean(combo[j][1:2], center))
        currSpreads.append(sum(dists) / float(len(dists))) #normalize

    variables.clusters.append(currClusters)
    variables.bounds.append(currBounds)
    variables.spreads.append(currSpreads)

def clusts3(currXY, allids):
    #get clusters
    if len(currXY) < 2:
        variables.numClusts.append(len(currXY))
        variables.clusters.append([allids[0], currXY[0][0], currXY[0][1]])
        variables.bounds.append(currXY)
        variables.spreads.append([0])
        variables.centers.append(currXY)
        return
    #bandwidth = estimate_bandwidth(currXY, n_samples=len(currXY))
    ms = Birch(threshold=1, n_clusters=None)
    ms.fit(currXY)
    labels = ms.labels_
    cluster_centers = ms.subcluster_centers_ #_indices_
    if cluster_centers is None:
        nClusts = 0
    else:
        nClusts = len(cluster_centers)
    variables.numClusts.append(nClusts)
    centers = []
    for i in range(nClusts):
        centers.append(cluster_centers[i])
    variables.centers.append(centers)

    currClusters = []
    currBounds = []
    currSpreads = []
    for k in range(nClusts):
        classMems = labels == k
        classMem = []
        for t in classMems:
            if isinstance(t, tuple):
                for x in t:
                    classMem.append(x)
            else:
                classMem.append(t)
        classMems = np.asarray(classMem)
        currXY = np.asarray(currXY)
        center = centers[k]

        #combine points
        ids = []
        for j in range(len(classMems)):
            if classMems[j] == True:
                ids.append(allids[j])
        x, y = currXY[classMems, 0], currXY[classMems, 1]
        combo = [] #push combo to save each cluster at each time step
        for i in range(len(x)):
            combo.append((ids[i], x[i], y[i]))
        currClusters.append(combo)

        #bounds
        pointColl = geometry.MultiPoint(combo)
        convHull = pointColl.convex_hull
        minx, miny, maxx, maxy = convHull.bounds
        currBounds.append([minx, miny, maxx, maxy])

        #spreads
        dists = []
        for j in range(len(combo)):
            dists.append(distance.euclidean(combo[j][1:], center))
        currSpreads.append(sum(dists) / float(len(dists))) #normalize

    variables.clusters.append(currClusters)
    variables.bounds.append(currBounds)
    variables.spreads.append(currSpreads)

def clusts(currXY, allids):
    if len(currXY) < 2:
        variables.numClusts.append(len(currXY))
        variables.clusters.append(currXY)
        variables.bounds.append(currXY)
        variables.spreads.append([0])
        variables.centers.append(currXY)
        return
    #get clusters
    af = AffinityPropagation().fit(currXY)
    clusterCenters = af.cluster_centers_indices_
    labs = af.labels_
    if clusterCenters is None:
        nClusts = 0
    else:
        nClusts = len(clusterCenters)
    variables.numClusts.append(nClusts)
    
    #cluster distances
    centers = []
    for i in range(nClusts):
        centers.append(currXY[clusterCenters[i]])
    variables.centers.append(centers)

    currClusters = []
    currBounds = []
    currSpreads = []
    for k in range(nClusts):
        classMems = labs == k
        classMem = []
        for t in classMems:
            if isinstance(t, tuple):
                for x in t:
                    classMem.append(x)
            else:
                classMem.append(t)
        classMems = np.asarray(classMem)
        currXY = np.asarray(currXY)
        center = centers[k]

        #combine points
        ids = []
        for j in range(len(classMems)):
            if classMems[j] == True:
                ids.append(allids[j])
        x, y = currXY[classMems, 0], currXY[classMems, 1]
        combo = [] #push combo to save each cluster at each time step
        for i in range(len(x)):
            combo.append((ids[i], x[i], y[i]))        
        currClusters.append(combo)

        #bounds
        pointColl = geometry.MultiPoint(combo)
        convHull = pointColl.convex_hull
        minx, miny, maxx, maxy = convHull.bounds
        currBounds.append([minx, miny, maxx, maxy])

        #spreads
        dists = []
        for j in range(len(combo)):
            dists.append(distance.euclidean(combo[j][1:2], center))        
        currSpreads.append(sum(dists) / float(len(dists))) #normalize

    variables.clusters.append(currClusters)
    variables.bounds.append(currBounds)
    variables.spreads.append(currSpreads)

