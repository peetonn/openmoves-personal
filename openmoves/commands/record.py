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
            x_path_file = open('library/data/paths_x.txt', 'wt')
            y_path_file = open('library/data/paths_y.txt', 'wt')
            z_path_file = open('library/data/paths_z.txt', 'wt')
            label_file = open('library/data/paths_l.txt', 'wt')

        if self.ops["--layout"] == true:
            x_layout_file = open('library/data/layouts_x.txt', 'wt')
            y_layout_file = open('library/data/layouts_y.txt', 'wt')
            z_layout_file = open('library/data/layouts_z.txt', 'wt')
            label_file = open('library/data/layouts_l.txt', 'wt')
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