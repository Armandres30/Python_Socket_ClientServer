#!usr/bin/python

from queue import Queue
import socket
import time
import struct
import cv2
import sys
import os
import _pickle as cPickle

class Path:
    def __init__(self, id, socket):
        self.id = id
        self.socket = socket
        self.target = (server_ip, server_port)

def create_transport_paths() -> Queue:
    queue = Queue(paths_count)
    
    for i in range(paths_count):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        path = Path(i + 1, sock)
        queue.put(path)

    return queue

def best_path(data):
    min = data[0][0]
    count = 0
    for d in data:
        if d[0] < min:
            min = d[0]
            best = count
        count = count + 1
    return best


sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)      # For UDP

server_ip = "127.0.0.1" #socket.gethostbyname("")	 	# Host IP
server_port = 12345			        # specified port to connect

paths_count = 5

id = 0

print("UDP target IP:", server_ip)
print("UDP target Port:", server_port)

# Get path to video = current_path + video filename
file_path = os.path.abspath(os.getcwd()) + "/short_video.mp4"

msg = [] # TODO: Delete if not needed

queue = create_transport_paths()

# Read video file frames
input_video = cv2.VideoCapture(file_path)
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
            msg.append(p + frame) # TODO: Delete if not needed 
            frame_str = str(frame)
            package_size = 1000
            frame_size = len(frame)
            elements = frame_size / package_size

            sequence_number = 1

            for i in range(0,int(elements)):
                path = queue.get()

                time_stamp = int(time.time())
                headers = struct.pack('bii', path.id, time_stamp, sequence_number)

                subframe = frame_str[int(i*package_size):int((i+1)*package_size)]
                
                path.socket.sendto(headers + bytes(subframe, encoding='utf-8'), path.target)

                queue.put(path)
                sequence_number += 1

                '''

                # Additional steps for optimal path selection after 50 attempts (10 for each path selection)

                if id >= 40:
                    best_path = best_path(data)
                    path = Path(best_path, sock)
                    queue.put(path)
                else:
                    queue.put(path)
                sequence_number += 1


                ## Receive in Client path_id, delay and sequence_number feedback from Server
                print("Waiting for client...")
                packet,addr = sock.recvfrom(1024)	
                headers = packet[0:12] #get headers from packet
                path_id, delay, sequence_number = struct.unpack('bii', headers)	#get path_id and time_stamp from headers
                id= id + 1
                delay_dict[path_id].append(delay)

                for i in range(1,6):
                    if len(delay_dict[i]) > 1:
                        avg[i-1] = np.array(delay_dict[i]).mean()
                    else:
                        avg[i-1] = np.array(delay_dict[i])
                        
                    data[i-1] = [len(delay_dict[i]), avg[i-1]]  
                '''

            break
        else:
           pass