import variables

class Track:
    """Proposed class for storing all data related to one track"""

    def __init__(self, track, sigid):
        self.id = sigid
        paddedList = [[float('inf'), float('inf'), float('inf')]] * variables.epoch
        self.track = paddedList.append(track)
        self.xders = [[float('inf'), float('inf'), float('inf')]] * variables.epoch
        self.yders = [[float('inf'), float('inf'), float('inf')]] * variables.epoch
        self.xsecondders = [[float('inf'), float('inf'), float('inf')]] * variables.epoch
        self.ysecondders = [[float('inf'), float('inf'), float('inf')]] * variables.epoch
        self.distances = [[float('inf')]] * variables.epoch
        #self.stagedists = [[float('inf')]] * variables.epoch



    
