#!usr/bin/python

import socket
import threading
import time

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
		data,addr = sock.recvfrom(1024)	        #receive data from client
		count+=1
		#kill.set()
		#time.sleep(1)
		size = len(data)
		databus.append(list)
		
		if len(databus) >= 1000:
			for i in range(0, size-1):
				current = int.from_bytes(databus[i][0:4], byteorder='big')
				next = int.from_bytes(databus[i+1][0:4], byteorder='big')
				step = next - current

				miss = miss + step
		

		print("Received Messages:",data," from",addr)
		print("Size of Message: "+str(size))
		print("Count Messages sent: " +  str(count))

		print("Number of missing packets: ",miss)
		print("Packet loss: ", float(miss/size))
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