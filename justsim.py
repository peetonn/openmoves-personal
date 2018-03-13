#!/usr/bin/python

import socket, time, json, time, random, sys
from time import sleep

UDP_IP = "127.0.0.1"
# UDP_IP = "255.255.255.255"
UDP_IP = "192.168.1.255" # 169.254.255.255

def main(port, rate, dat, loop):
	delay = 1000./float(rate)
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP   
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

		with open(data, "r") as f:
			allLines = f.readlines()
			run = 1
			progress = 0
			while run > 0:
				for line in allLines:
					try:
						jsonPacket = json.loads(line)
						payload = bytes(json.dumps(jsonPacket).encode('utf-8'))
						sock.sendto(payload, (UDP_IP, port))
						progress += 1
						print "SENT ", progress, "/", len(allLines), " : ", payload
						# print float(progress)/float(len(allLines)) * 100, "%"
						sleep(delay/1000.)
					except Exception as e:
						# print "error parsing json", e, line
						pass
				if not loop:
					run -= 1
	except Exception as e:
		print "caught exception: ", e
		exit(1)

nArgs = 3

if __name__ == '__main__':
	if len(sys.argv) <= nArgs:
		print ("specify port, rate, data file")
		exit(1)

	port = int(sys.argv[1])
	rate = float(sys.argv[2])
	data = sys.argv[3]
	loop = True

	print "sending data from ", data, " on port ", port, " at rate ", rate, " looping: ", loop
	main(port, rate, data, loop)