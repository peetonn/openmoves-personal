import json, os

# Shared variable repository
# Config file read-in vars initialized with None

#general
PERIOD = .100 
UDP_IP = "127.0.0.1"
UDP_PORT_IN = 21234
UDP_PORT_OUT = 21235
SEQ = 0
epoch = 0

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
memorywindow = None

hotSpots = []
numClusts = []
centers = []
clusters = []
bounds = []
spreads = []

def parse():
    """function to parse the config file"""
    fn = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
    with open(fn) as data_file:
        data = json.load(data_file)
    shorttimespan = data["shorttime"]
    shortwindow = data["windowsize"]
    shortclusterwindow = data["unsupervised"]["shortclusterwindowsize"]
    memorywindow = data["unsupervised"]["memorywindowsize"]