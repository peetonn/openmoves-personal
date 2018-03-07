import variables
import numpy as np
from sklearn.cluster import AffinityPropagation
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
    print(variables.parentList)
    print(np.asarray(variables.parentList))
    covs = np.cov(np.asarray(variables.parentList)[0].T)
    print("---------------------------")
    print(covs)
    ea, va = np.linalg.eig(covs)

    #pair and sort the eigenvectors with respective eigenvalues
    #expairs = [(np.abs(ex[i]), vx[:,i]) for i in range(len(ex))]
    #eypairs = [(np.abs(ey[i]), vy[:,i]) for i in range(len(ex))]
    #expairs.sort(key=lambda x: x[0], reverse=True)
    #eypairs.sort(key=lambda x: x[0], reverse=True)
    eapairs = [(np.abs(ea[i]), va[:,i]) for i in range(len(ea))]
    eapairs.sort(key=lambda x: x[0], reverse=True)

    #return greatest of each
    return eapairs[0], eapairs[1]

def hotClusts(): #need to remove duplicates
    #hot locations analysis on recent time window (can adjust)
    if(len(variables.allX) > variables.hotspotwindow):
        recentXY = []
        for i in range(1, variables.hotspotwindow):
            currentX = variables.allX[-i]
            currentY = variables.allY[-i]
            for j in range(len(currentX)):
                #if currentX[j] != float('nan') and currentY[j] != float('nan'):
                    recentXY.append([currentX[j], currentY[j]])

        af = AffinityPropagation().fit(recentXY)
        clusterCenters = af.cluster_centers_indices_
        #print(clusterCenters)
        if clusterCenters is None:
            nClusts = 0
        else:
            nClusts = len(clusterCenters)
        print(nClusts)
        variables.hotSpots = []
        for i in range(nClusts):
            if recentXY[clusterCenters[i]] not in variables.hotSpots:
                
                variables.hotSpots.append(recentXY[clusterCenters[i]])

def clusts(currXY):
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
        x, y = currXY[classMems, 0], currXY[classMems, 1]
        combo = [] #push combo to save each cluster at each time step
        for i in range(len(x)):
            combo.append((x[i],y[i]))
        currClusters.append(combo)

        #bounds
        pointColl = geometry.MultiPoint(combo)
        convHull = pointColl.convex_hull
        minx, miny, maxx, maxy = convHull.bounds
        currBounds.append([minx, miny, maxx, maxy])

        #spreads
        dists = []
        for j in range(len(combo)):
            dists.append(distance.euclidean(combo[j], center))
        currSpreads.append(sum(dists) / float(len(dists))) #normalize

    variables.clusters.append(currClusters)
    variables.bounds.append(currBounds)
    variables.spreads.append(currSpreads)

