# Shared variable repository
# Config file read-in vars initialized with None

#general
PERIOD = .0334 
UDP_IP = "127.0.0.1"
UDP_PORT_IN = 21234
UDP_PORT_OUT = 21235
SEQ = 0
epoch = 0
visualize = 0 
trackheight = 0

#instantaneous
ids = []
parentList = []

pois = None
stagepts = None

pairs = []
xdersList = []
ydersList = []
xseconddersList = []
yseconddersList = []

#for plotting (deprecated unsup use)
allX = []
allY = []

#short time
dtwdistances = []
shorttimespan = None #unused
shortwindow = None
dtwrefresh = None
dtwwindows = None

#unsupervised
shortclusterwindow = None #unused
hotspotwindow = None
pcarefresh = None
e1 = []
e2 = []

hotSpots = []
numClusts = []
centers = []
clusters = []
bounds = []
spreads = []