# -*- coding: utf-8 -*-
import socket, time, json, random, csv
import numpy as np

from .base import Base

class Record(Base):
    """Record paths for classifier and single-actor DTW"""
    def __init__(self, ops, *args, **kwargs):
        self.ops = ops
        self.args = args
        self.kwargs = kwargs

    def run(self):
        s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s_in.bind(("", variables.UDP_PORT_IN+1))
        print("waiting on port:", variables.UDP_PORT_IN+1)

        if self.ops["--path"] == true:
            x_path_file = open('library/data/paths_x.txt', 'w')
            y_path_file = open('library/data/paths_y.txt', 'w')
            z_path_file = open('library/data/paths_z.txt', 'w')
            label_file = open('library/data/paths_l.txt', 'w')

            # Create empty lists
            x_path = []
            y_path = []
            z_path = []
            l_path = []

        if self.ops["--layout"] == true:
            pass        
        try:
            while True:
                if variables.visualize == 1:
                    plt.clf()
                data, addr = s_in.recvfrom(8192)
                data = data.rstrip("\0")  
                payload = json.dumps(json.loads(data), sort_keys=True, indent=4, separators=(',', ': ') ) 

                #parse as generated
                msg = str(payload)

                trackingData = json.loads(msg)
                variables.SEQ = trackingData['header']['seq']
                if trackingData['header']['frame_id'] == 'heartbeat':
                    aliveids = len(trackingData['alive_IDs'])
                    continue

                tracks = trackingData['people_tracks']
                if tracks == []:
                    continue

                trackData = []
                for singletrack in tracks:
                    trackData.append([singletrack['id'], singletrack['x'], singletrack['y'], singletrack['height']])