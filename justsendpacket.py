#!/usr/bin/python

import socket, time, json, time, random, sys
from time import sleep

UDP_IP = "127.0.0.1"

def main(port, rate, packet):
	delay = 1000./float(rate)
	try:
		with open(packet) as json_data:
			jsonPacket = json.load(json_data)
			print "packet to send: ", jsonPacket
			sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP   
			payload = bytes(json.dumps(jsonPacket).encode('utf-8'))# + bytes(bytearray(100))
	except Exception as e:
		print "error reading json: ", e
		exit(1)

	while True:
		sock.sendto(payload, (UDP_IP, port))
		print payload
		sleep(delay/1000.)

nArgs = 3

if __name__ == '__main__':
	if len(sys.argv) <= nArgs:
		print ("specify port, rate and packet.json file")
		exit(1)

	port = int(sys.argv[1])
	rate = int(sys.argv[2])
	packet = sys.argv[3]

	print "sending ", packet, " on port ", port, " at rate ", rate
	main(port, rate, packet)