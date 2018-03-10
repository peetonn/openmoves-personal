import variables

class Track:
    """Proposed class for storing all data related to one track"""

    def __init__(self, track, sigid, epoch):
        self.id = sigid
        self.track = [track]

        self.xders = []
        self.yders = []
        
        self.xsecondders = []
        self.ysecondders = []
        
        self.distances = []
        self.stagedists = []

        self.born = epoch
        self.died = float('inf')


    
