#!usr/bin/python

from operator import contains
import socket
import struct
import time
from datetime import datetime
import numpy as np
import sys

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)      # For UDP

udp_host =  "127.0.0.1" #socket.gethostbyname("")	        # Host IP
udp_port = 12345			                # specified port to connect

databus = []
count = 0
total = 0

t1 = []
t2 = []
Dj = []

expected_sequence_number = 1
missing_packets = []

while True:
	try:
        # server must bind to an ip address and port
		sock.bind((udp_host,udp_port))
		print("Listening on Port:", udp_port)
		break
	except Exception:
		print("ERROR: Cannot connect to Port:", udp_port)
		udp_port += 1

try:
	while True:
		print("Waiting for client...")
		packet,addr = sock.recvfrom(1024)	        #receive data from client
		
		headers = packet[0:12] #get headers from packet
		data = packet[12:]	#get data from packet

		path_id, start_time, sequence_number = struct.unpack('bii', headers)	#get path_id and time_stamp from headers

		print("expected seq num, seq num", (expected_sequence_number, sequence_number))
		if(expected_sequence_number != sequence_number):
			if(sequence_number in missing_packets):
				missing_packets.remove(sequence_number)
			else:
				missing_packets.append(expected_sequence_number)

		expected_sequence_number += 1

		end_time = int(time.time())

		delay = end_time - start_time

		t1.append(start_time)
		t2.append(end_time)

		## Calculate jitter
		if count > 1:
			for i in range(1,count):
				Dj.append((t2[i]-t1[i]) - (t2[i-1]-t1[i-1])) #Get array of delays
		j = np.array(Dj)
		jitter = j.mean() #Jitter is meand deviation of delays 
		
		count+=1
		size = len(data)	# get size of data
		size2 = sys.getsizeof(packet)	# get size of data
		databus.append(packet)
		total = total + size
		length = len(databus)

		if delay:
			capacity = size2/delay
		else:
			capacity = size2

		
		print("Received Message:",data," from ",addr)

		print("Start Time: ", start_time)
		print("End Time: ", end_time)

		print("Path ID: ", path_id)
		print("Sequence number: ", sequence_number)
		print("Delay: ", delay, "s")

		print("Jitter: ", jitter)

		print("Size of Message: "+str(size))
		print("Count Messages sent: " +  str(count))

		print("Missing packets: ", missing_packets)
		print("Number of missing packets: ", len(missing_packets))
		print("Total bytes received: ",total)

		print("Capacity: ", capacity)

		'''
		headers = struct.pack('bii', path_id, delay, sequence_number)    
		sock.sendto(headers, addr)
		time.sleep(1)
		'''


except KeyboardInterrupt:
    pass