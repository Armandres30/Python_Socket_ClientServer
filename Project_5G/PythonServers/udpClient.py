#!usr/bin/python

import socket

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)      # For UDP

udp_host = socket.gethostbyname("")	 	# Host IP
udp_port = 12345			        # specified port to connect

msg = "Hello Python!"
print("UDP target IP:", udp_host)
print("UDP target Port:", udp_port)

sock.sendto(bytes(msg, encoding='utf-8'),(udp_host,udp_port))		# Sending message to UDP server

received_bytes, peer = sock.recvfrom(512)

print("Received %s from %s:%u" % (received_bytes.decode('utf8'), peer[0], peer[1]))

#Our udpServer.py is up and running, so now we try to run the udpclient.py script,