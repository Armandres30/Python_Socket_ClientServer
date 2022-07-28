#!usr/bin/python

import socket
import struct
import threading
import time
from datetime import datetime
import numpy as np

## Ressources based on:
## https://tutorialmeta.com/question/python-udp-socket-has-packet-loss-every-65536-packets

def receive():
	global data
	global addr
	while not kill.is_set():
		d, addr = sock.recvfrom(512)
		data.append(d)
		address.append(addr)

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)      # For UDP

udp_host =  "127.0.0.1" #socket.gethostbyname("")	        # Host IP
udp_port = 12345			                # specified port to connect


#print type(sock) ============> 'type' can be used to see type 
				# of any variable ('sock' here)

#sock.bind((udp_host,udp_port))
miss = 0
#kill = threading.Event()
#p = threading.Thread(target = receive())
#p.start()
databus = []
count = 0
total = 0
total_miss = 0

t1 = []
t2 = []
Dj = []

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
		
		headers = packet[0:8] #get headers from packet
		path_id, start_time = struct.unpack('bi', headers)	#get path_id and time_stamp from headers
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

		data = packet[8:]	#get data from packet
		
		count+=1
		#kill.set()
		#time.sleep(1)
		size = len(data)	# get size of data
		databus.append(packet)
		total = total + size
		miss = 0
		length = len(databus)
		step = 0

		start = int.from_bytes(databus[0][0:4], byteorder='big')
		end = int.from_bytes(databus[length-1][0:4], byteorder='big')
		print("start: ",start)
		print("end: ",end)
		total = end - start + 1
		print("Number of packets: ",total)
		
		if len(databus) >= 1000:
			for i in range(0, size-1):
				current = int.from_bytes(databus[i][0:4], byteorder='big')
				next = int.from_bytes(databus[i+1][0:4], byteorder='big')
				step = next - current
				if step < 0:
					print("out of order detected!!!")
					break

			miss = miss + step
		
		total_miss = total_miss + miss
		#"""
		print("Received Message:",data," from ",addr)

		print("Start Time: ", start_time)
		print("End Time: ", end_time)

		print("Path ID: ", path_id)
		print("Delay: ", delay, "s")

		print("Jitter: ", jitter)

		print("Step: ", step)
		print("Size of Message: "+str(size))
		print("Count Messages sent: " +  str(count))

		print("Number of missing packets: ",miss)
		print("Number of packets: ",total)
		print("Total Miss: ", total_miss)
		print("Packet loss: ", float(miss/size))
		print("Packet loss Total: ", float(total_miss/total))
		#"""
except KeyboardInterrupt:
    pass
	

	#sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	#sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	#sock.bind(('', addr))

	#sock1 = sock.setsockopt(socket.IPPROTO_IPV6, socket.IP_HDRINCL, 1)
	#print(sock1)

'''
	rtt = []

while True:
	print("Waiting for client...")
	data,addr = sock.recvfrom(1024)	        #receive data from client

	start=time.time() #the current time
	while sequence_number<=10:
		data = ('PING %d %d' % (sequence_number, start)) #client message
		try:
			data, addr = sock.recvfrom(1024) #recieves message from server
			elapsed = (time.time()-start) # calculates the rtt
			rtt.append(elapsed)
			print(data)
			print('Round Trip Time is:' + str(elapsed) + ' seconds')
		except socket.timeout: #if no reply within 1 second
			print(data)
			print('Request timed out')
			sequence_number+=1 #incremented by 1
	print("Received Messages:",data," from",addr)

	print("Received %s from %s:%u" % (data.decode('utf8'), addr[0], addr[1]))

	print('Packet loss rate is:' + str((10-len(rtt))*10)+ ' percent')

	sock = socket.socket(socket.AF_INET6, socket.SOCK_RAW)
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	sock.bind(('', addr[1]))

	#sock1 = sock.setsockopt(socket.IPPROTO_IPV6, socket.IP_HDRINCL, 1)
	#print(sock1)
'''