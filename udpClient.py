#!usr/bin/python

from queue import Queue
import socket
import time
import struct
from typing import List
import cv2
import sys
import os
import _pickle as cPickle

server = ("127.0.0.1", 12345)
reverse_path = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # Creates a UDP socket which will be used to receive the statistics from the server
reverse_path.bind(('127.0.0.1', 54321))

control_path = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creates a socket for sending control messages to the server

paths_count = 5

batch_size = 20

class Path:
    def __init__(self, id, socket, delay):
        self.id = id
        self.socket = socket
        self.target = server
        self.delay = delay

def create_transport_paths() -> Queue:
    # path_array = []
    queue = Queue(paths_count)
    
    for i in range(paths_count):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        path = Path(i + 1, sock, 0)
        queue.put(path)
        # path_array.append(path)

    # return path_array
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

def get_headers(pathId, sequence_number):
    time_stamp = int(time.time())
    return struct.pack('bii', pathId, time_stamp, sequence_number)

def main():
    id = 0

    print('Connecting to server' + str(server[0]) + ':' + str(server[1]))

    # Get path to video = current_path + video filename
    file_path = os.path.abspath(os.getcwd()) + "/short_video.mp4"

    path_array = create_transport_paths()

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
                frame_str = str(frame)
                package_size = 1000
                frame_size = len(frame)
                elements = frame_size / package_size

                sequence_number = 1
                current_position = 0
                next_position = current_position + batch_size

                while next_position <= elements:

                    while current_position < next_position:
                        path = path_array.get()

                        headers = get_headers(path.id, sequence_number)
                        subframe = frame_str[int(current_position*package_size):int((current_position+1)*package_size)]
                        packet = headers + bytes(subframe, encoding='utf-8')
                        
                        path.socket.sendto(packet, path.target)

                        path_array.put(path)
                        sequence_number += 1
                        current_position += 1

                    control_headers = get_headers(6, 0)
                    control_packet = control_headers + 'BATCH_FIN'.encode('utf-8')
                    control_path.sendto(control_packet, server)

                    packet, addr = reverse_path.recvfrom(128)

                    delays = list(map(int, packet.decode('utf-8').split(',')))
                    # for curr_path in path_array:
                    #     curr_path.delay = delays[curr_path.id - 1]
                        
                    # next_position = current_position + batch_size
                    # next_position = next_position if elements > next_position else elements # Check if the next position is overflowing
                    

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

main()