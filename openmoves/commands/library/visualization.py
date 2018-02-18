import variables
import shapely.geometry as geometry
from descartes import PolygonPatch
import matplotlib.pyplot as plt

def plotting():
    plt.ion()
    plt.interactive(False)
    fig = plt.figure(figsize=(5,5)) 

def pltPaths():
    #plot paths & points
    for i in range(len(variables.allX[-1])):
        plt.plot([item[i] for item in variables.allX], [item[i] for item in variables.allY], zorder=-1)

    plt.scatter(variables.allX[-1], variables.allY[-1], zorder=3)
    
def pltClustering():
    #plot clustering
    centers = variables.centers[-1]
    clusters = variables.clusters[-1]
    for k in range(variables.numClusts[-1]):
        center = centers[k]
        combo = clusters[k]

        plt.plot(center[0], center[1], 'y' + '*', zorder=4)
        for x in combo:
            plt.plot([center[0], x[0]], [center[1], x[1]], 'r' + '--', zorder=2)

def pltShapes(fig):    
    #Better method: calculate number of acute angles along convex hull 
    centers = variables.centers[-1]
    clusters = variables.clusters[-1]
    for k in range(variables.numClusts[-1]):
        center = centers[k]
        combo = clusters[k]

        #get shapes
        pointColl = geometry.MultiPoint(combo)
        convHull = pointColl.convex_hull
        ax = fig.add_subplot(111)
        if len(combo) > 2:
            patch = PolygonPatch(convHull, fc='#999999', ec='#000000', fill=True, zorder=1)
            ax.add_patch(patch)
        
            #label shapes
            #todo: calculate number of acute angles along convex hull instead
            x, y = convHull.exterior.coords.xy
            if len(x) == 4:
                plt.text(centers[0] + 5, centers[1] + 5, r'triangle', fontdict={'size': 8})
            if len(x) == 5:
                plt.text(centers[0] + 5, centers[1] + 5, r'quad', fontdict={'size': 8})
            if len(x) == 6:
                plt.text(centers[0] + 5, centers[1] + 5, r'pentagon', fontdict={'size': 8})
            if len(x) > 6:
                plt.text(centers[0] + 5, centers[1] + 5, r'poly', fontdict={'size': 8})
