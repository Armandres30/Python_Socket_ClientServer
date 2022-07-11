#!usr/bin/python

import socket
import time
import struct
import cv2
import sys
import os
import _pickle as cPickle

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)      # For UDP

udp_host = "127.0.0.1" #socket.gethostbyname("")	 	# Host IP
udp_port = 12345			        # specified port to connect

path_id = 1


server_port = 12000
sock.bind(("127.0.0.1", server_port))

print("UDP target IP:", udp_host)
print("UDP target Port:", udp_port)

# Get path to video = current_path + video filename
path = os.path.abspath(os.getcwd()) + "/short_video.mp4"

msg = []

# Read video file frames
input_video = cv2.VideoCapture(path)
if input_video.isOpened() == False:
    print("Video not found")
    sys.exit(1)
else:
    # Read until the video is completed
    while(input_video.isOpened()):
        # Capture frame by frame
        ret, frame = input_video.read()
        if ret == True:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.imshow('frame',frame)
            frame = cPickle.dumps(frame)
            size = len(frame)
            p = struct.pack('I', size)
            msg.append(p + frame) 
            frame_str = str(frame)
            package_size = 1000
            frame_size = len(frame)
            elements = frame_size / package_size

            time_stamp = int(time.time())
            headers = struct.pack('bi', path_id, time_stamp)

            for i in range(0,int(elements)):
                subframe = frame_str[int(i*package_size):int((i+1)*package_size)]
                #print(len(subframe))
                sock.sendto(headers + bytes(subframe, encoding='utf-8'),(udp_host,udp_port))
            break
        else:
           # input_video.set(cv2.cv.CV_CAP_PROP_POS_FRAMES, pos_frame-1)

            '''
        if input_video.get(cv2.cv.CV_CAP_PROP_POS_FRAMES) == input_video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT):
            size = 10
            p = struct.pack("I", size)
            sock.send(p)
            sock.send('')
            break
            '''

#for m in msg:
    #sock.sendto(str(m).encode(),(udp_host,udp_port))		# Sending message to UDP server
 #   pass



'''

sport = 4711    # arbitrary source port
dport = 45134   # arbitrary destination port
length = 8 + len(msg)
checksum = 0

start = time.time()

src_addr = socket.handshake.address
dest_addr

##First way
zero = 0
protocol = socket.IPPROTO_UDP 
data_len = len(msg)
udp_length = 8 + data_len
src_ip, dest_ip = ip2int(src_addr[0]), ip2int(dest_addr[0])
src_ip = struct.pack('!4B', *src_ip)
#Get source ip for obtaining udp header

pseudo_header = struct.pack('!BBH', zero, protocol, udp_length)
pseudo_header = src_ip + dest_ip + pseudo_header
udp_header = struct.pack('!4H', src_port, dest_port, udp_length, checksum)
checksum = checksum_func(pseudo_header + udp_header + msg)
udp_header = struct.pack('!4H', src_port, dest_port, udp_length, checksum)

udp_header = struct.pack(str(start), sport, dport, length, checksum)

sock.sendto(bytes(udp_header + msg, encoding='utf-8'),(udp_host,udp_port))		# Sending message to UDP server

'''

#sock.sendto(bytes(msg, encoding='utf-8'),(udp_host,udp_port))		# Sending message to UDP server


#Our udpServer.py is up and running, so now we try to run the udpclient.py script,

def ip2int(ip_addr):
    if ip_addr == 'localhost':
        ip_addr = '127.0.0.1'
    return [int(x) for x in ip_addr.split('.')]