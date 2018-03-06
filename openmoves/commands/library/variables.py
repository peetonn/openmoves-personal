# Shared variable repository
# Config file read-in vars initialized with None

#general
PERIOD = .0334 
UDP_IP = "255.255.255.255"
UDP_PORT_IN = 21234
UDP_PORT_OUT = 21235
SEQ = 0
epoch = 0
visualize = 0
trackheight = 0

#instantaneous
ids = []
aliveIDs = []
parentList = []

pois = None
stagepts = None

pairs = []
xdersList = []
ydersList = []
xseconddersList = []
yseconddersList = []
orientations = []

#for plotting
allX = []
allY = []

#short time
lastlength = 0
dtwdistances = []
shorttimespan = None #unused
shortwindow = None #unused
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

#supervised
x_layout = []
y_layout = []
z_layout = []
l_layout = []

x_path = []
y_path = []
z_path = []
l_path = []