#!usr/bin/python

from operator import contains
import socket
import struct
import time
from datetime import datetime
import numpy as np
import sys

server_addr = ("127.0.0.1", 12345)
main_path = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
main_path.bind(server_addr)

client_addr = ('127.0.0.1', 54321)
reverse_path = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def initialize_path_delays():
	for i in range(paths_count):
		path_delays.append([])

databus = []
count = 0
total = 0

t1 = []
t2 = []
Dj = []

path_delays = []
paths_count = 5 # TODO: move to a common file

expected_sequence_number = 1
missing_packets = []

initialize_path_delays()
while True:
	print("Waiting for client...")
	packet, addr = main_path.recvfrom(1024)	        #receive data from client
	
	headers = packet[0:12] #get headers from packet
	data = packet[12:]	#get data from packet

	if(data.decode('utf-8').strip() == 'BATCH_FIN'):
		result_array = []
		for delay_arr in path_delays:
			result_array.append(round(np.mean(delay_arr)))

		statistics_message = ','.join(map(str, result_array)).encode('utf-8')
		reverse_path.sendto(statistics_message, client_addr)

		initialize_path_delays()
		continue


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
	path_delays[path_id - 1].append(delay)

	t1.append(start_time)
	t2.append(end_time)

	## Calculate jitter
	if count > 1:
		for delay_arr in range(1,count):
			Dj.append((t2[delay_arr]-t1[delay_arr]) - (t2[delay_arr-1]-t1[delay_arr-1])) #Get array of delays
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