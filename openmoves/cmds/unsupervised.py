from template import .template
import variables

class unsupervised(template):
    """Unsupervised analysis module"""

    def __init__(self, ops, *args, **kwargs):
        self.ops = ops
        self.args = args
        self.kwargs = kwargs

    def run(self):
        raise NotImplementedError("haven't moved stuff here, yet")

    def covariance(): 
        #ignore entries of resulting matrix with indicies not both odd or even
        #todo: keep track of longest length for zero padding / otherwise account for different n in each timestep  
        #create a matrix such that each column is the x or y of a particular actor
        allXY = []
        for i in range(len(self.allX)):
            currentX = self.allX[i]
            currentY = self.allY[i]
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

    def covarianceind():
        covX = np.cov(np.asarray(self.allX).T)
        covY = np.cov(np.asarray(self.allY).T)

        return covX, covY

    def pca():
        #take cov matrices & evals/evects
        xcov, ycov = covarianceind()
        ex, vx = np.eig(xcov)
        ey, vy = np.eig(ycov)

        #pair and sort the eigenvectors with respective eigenvalues
        expairs = [(np.abs(ex[i]), vx[:,i]) for i in range(len(ex))]
        eypairs = [(np.abs(ey[i]), vy[:,i]) for i in range(len(ex))]
        expairs.sort(key=lambda x: x[0], reverse=True)
        eypairs.sort(key=lambda x: x[0], reverse=True)

        #return greatest of each
        return expairs[0], eypairs[0]

    #dtw-based classification
    #iterate through template paths, find corresponding live paths
    #use dtw distance as metric for closest corresponding template path
    def classify(live, template, window):
        pass

    def hotClusts():
        #hot locations analysis on recent time window (can adjust)
        if(len(self.allX) > 100):
            recentXY = []
            for i in range(1, 100):
                currentX = self.allX[len(self.allX)-i]
                currentY = self.allY[len(self.allX)-i]
                for j in range(len(currentX)):
                    recentXY.append([currentX[j], currentY[j]])

        af = AffinityPropagation().fit(recentXY)
        clusterCenters = af.cluster_centers_indices_
        labs = af.labels_
        nClusts = len(clusterCenters)
        hotSpots = []
        for i in range(nClusts):
            hotSpots.append(recentXY[clusterCenters[i]])

    def clusts():
        #get clusters
        af = AffinityPropagation().fit(currXY)
        clusterCenters = af.cluster_centers_indices_
        labs = af.labels_
        nClusts = len(clusterCenters) #push to save at each time step
        
        #cluster distances
        centers = []
        for i in range(nClusts):
            centers.append(currXY[clusterCenters[i]])