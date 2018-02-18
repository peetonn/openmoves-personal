# Shared variable repository
# Config file read-in vars initialized with None

#general
PERIOD = .100 
UDP_IP = "127.0.0.1"
UDP_PORT_IN = 21234
UDP_PORT_OUT = 21235
SEQ = 0
epoch = 0
visualize = 0 # 0 or 1

#instantaneous
ids = []
parentList = []

pairs = []
xdersList = []
ydersList = []
xseconddersList = []
yseconddersList = []

#for use when sparsity doesn't matter
allXY = []
allX = []
allY = []

#short time
shorttimespan = None
shortwindow = None

#unsupervised
shortclusterwindow = None
hotspotwindow = None
pcarefresh = None
expair = []
eypair = []

hotSpots = []
numClusts = []
centers = []
clusters = []
bounds = []
spreads = []