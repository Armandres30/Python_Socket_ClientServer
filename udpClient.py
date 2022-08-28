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
import constants

reverse_path = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # Creates a UDP socket which will be used to receive the statistics from the server
reverse_path.bind(constants.CLIENT_ADDRESS)

control_path = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creates a socket for sending control messages to the server

class Path:
    def __init__(self, id, socket, delay):
        self.id = id
        self.socket = socket
        self.target = constants.SERVER_ADDRESS
        self.delay = delay

def create_transport_paths() -> Queue:
    # path_array = []
    queue = Queue(constants.PATHS_COUNT)
    
    for i in range(constants.PATHS_COUNT):
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

def send_control_message(message):
    control_headers = get_headers(6, 0)
    control_packet = control_headers + message.encode('utf-8')
    control_path.sendto(control_packet, constants.SERVER_ADDRESS)

def main():
    print('Connecting to server' + str(constants.SERVER_ADDRESS[0]) + ':' + str(constants.SERVER_ADDRESS[1]))

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
                next_position = current_position + constants.BATCH_SIZE

                while current_position < elements:

                    while current_position < next_position:
                        path = path_array.get()

                        headers = get_headers(path.id, sequence_number)
                        subframe = frame_str[int(current_position*package_size):int((current_position+1)*package_size)]
                        packet = headers + bytes(subframe, encoding='utf-8')
                        
                        path.socket.sendto(packet, path.target)

                        path_array.put(path)
                        sequence_number += 1
                        current_position += 1

                    send_control_message(constants.BATCH_FIN_MSG)

                    packet, addr = reverse_path.recvfrom(128)

                    delays = list(map(int, packet.decode('utf-8').split(',')))
                    
                    # for curr_path in path_array:
                    #     curr_path.delay = delays[curr_path.id - 1]
                        
                    next_position = current_position + constants.BATCH_SIZE
                    next_position = next_position if elements > next_position else elements # Check if the next position is overflowing
                    
                send_control_message(constants.FIN_MSG)
                return

main()