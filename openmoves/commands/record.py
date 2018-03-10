# -*- coding: utf-8 -*-
import socket, time, json, random, csv
import numpy as np
import library.variables as variables
import library.publishing as publishing

from .base import Base

class Record(Base):
    """Record paths for classifier and single-actor DTW"""
    def __init__(self, ops, *args, **kwargs):
        self.ops = ops
        self.args = args
        self.kwargs = kwargs

        self.x = []
        self.y = []
        self.z = []

        publishing.parse()

    def run(self):
        s_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        s_in.bind(("", variables.UDP_PORT_IN))
        print("waiting on port:", variables.UDP_PORT_IN)

        if self.ops["--path"] == True:
            x_path_file = open('openmoves/commands/library/data/paths_x.csv', 'ab')
            y_path_file = open('openmoves/commands/library/data/paths_y.csv', 'ab')
            z_path_file = open('openmoves/commands/library/data/paths_z.csv', 'ab')
            label_file = open('openmoves/commands/library/data/paths_l.txt', 'ab')

        if self.ops["--layout"] == True:
            x_layout_file = open('library/data/layouts_x.csv', 'ab')
            y_layout_file = open('library/data/layouts_y.csv', 'ab')
            z_layout_file = open('library/data/layouts_z.csv', 'ab')
            label_file = open('library/data/layouts_l.txt', 'ab')

        try:
            while True:
                data, addr = s_in.recvfrom(8192)
                data = data.rstrip("\0")  
                payload = json.dumps(json.loads(data), sort_keys=True, indent=4, separators=(',', ': ') ) 

                #parse as generated
                msg = str(payload)
                trackingData = json.loads(msg)

                if trackingData['header']['frame_id'] == 'heartbeat':
                    aliveids = len(trackingData['alive_IDs'])
                    continue

                tracks = trackingData['people_tracks']
                if tracks == []:
                    continue

                #print(maxx, maxy, minx, miny)
                #(4.79668, 5.13825, -3.98568, -3.31501)

                trackData = []
                for singletrack in tracks:
                    if singletrack['x'] < variables.extents[0][0] or singletrack['x'] > variables.extents[1][0] or singletrack['y'] < variables.extents[0][1] or singletrack['y'] > variables.extents[1][1]:
                        continue
                    trackData.append([singletrack['id'], singletrack['x'], singletrack['y'], singletrack['height']])
                
                if trackData == []:
                    continue
                self.x.append(trackData[0][1])
                self.y.append(trackData[0][2])
                self.z.append(trackData[0][3])

        except KeyboardInterrupt:
            wr = csv.writer(x_path_file)
            wr.writerow(self.x)
            wr = csv.writer(y_path_file)
            wr.writerow(self.y)
            wr = csv.writer(z_path_file)
            wr.writerow(self.z)

            label_file.write(str(input("Enter label:"))+'\n')