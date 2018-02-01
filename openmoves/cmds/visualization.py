from template import .template

class offline(template):
    """Offline analyses of OPT data. Will probably be broken up into
    several different CL commands, instead"""

    def __init__(self, ops, *args, **kwargs):
        self.ops = ops
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError("haven't moved stuff here, yet")

    def pltPaths():
        plt.clf()

        #plot paths & points
        for i in range(len(currX)):
            plt.plot([item[i] for item in self.allX], [item[i] for item in self.allY], zorder=-1)

        plt.scatter(currX, currY, zorder=3)
        
    def pltClustering():
        #plot clustering
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

            #get shapes
            pointColl = geometry.MultiPoint(combo)
            convHull = pointColl.convex_hull
            minx, miny, maxx, maxy = convHull.bounds
            if len(x) > 2:
                patch = PolygonPatch(convHull, fc='#999999', ec='#000000', fill=True, zorder=1)
            ax = fig.add_subplot(111)
            if len(x) > 2:
                ax.add_patch(patch)

    def pltShapes():    
         """
        Better method: calculate number of acute angles along convex hull 
        """

        plt.axis([-250,250,-250,250])
        plt.pause(0.05)

        time.sleep(self.PERIOD)
