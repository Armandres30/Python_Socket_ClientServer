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
import numpy as np
import constants as const

reverse_path = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) # Creates a UDP socket which will be used to receive the statistics from the server
reverse_path.bind(const.CLIENT_ADDRESS)

control_path = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creates a socket for sending control messages to the server

class Path:
    def __init__(self, id, socket, delay, packets_count):
        self.id = id
        self.socket = socket
        self.target = const.SERVER_ADDRESS
        self.delay = delay
        self.packet_slots = packets_count

def create_transport_paths() -> List[Path]:
    path_array = []
    
    for i in range(const.PATHS_COUNT):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        path = Path(i + 1, sock, 0, 0)
        path_array.append(path)

    return path_array

def distribute_packets(path_array: List[Path], packets_count: int):
    path_array.sort(key=lambda x: x.delay) # Sort the paths array by the delay
    best_path_delay = path_array[0].delay # Take the first item (the best path)
    best_path_count = [path.delay for path in path_array].count(best_path_delay) # Find the number of paths having the same delay
    
    packets_per_path = packets_count / best_path_count # Split the packets among the best paths
   
    for index in range(best_path_count):
        path_array[index].packet_slots = packets_per_path

    path_array[0].packet_slots += packets_count % best_path_count # Add the remaining packets to the first path

def get_best_path(path_array: List[Path]) -> Path:
    return next(filter(lambda x: x.packet_slots > 0, path_array))

def update_path_delays(path_array: List[Path], delays: List[int]):
    for curr_path in path_array:
        curr_path.delay = delays[curr_path.id - 1]

def get_headers(pathId, sequence_number):
    time_stamp = int(time.time())
    return struct.pack('bii', pathId, time_stamp, sequence_number)

def send_control_message(message):
    control_headers = get_headers(6, 0)
    control_packet = control_headers + message.encode('utf-8')
    control_path.sendto(control_packet, const.SERVER_ADDRESS)

def main():
    print('Connecting to server' + str(const.SERVER_ADDRESS[0]) + ':' + str(const.SERVER_ADDRESS[1]))

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
                next_position = current_position + const.BATCH_SIZE

                while current_position < elements:
                    packets_count = next_position - current_position
                    distribute_packets(path_array, packets_count)

                    while current_position < next_position:
                        path = get_best_path(path_array)

                        while path.packet_slots > 0:
                            headers = get_headers(path.id, sequence_number)
                            subframe = frame_str[int(current_position*package_size):int((current_position+1)*package_size)]
                            packet = headers + bytes(subframe, encoding='utf-8')
                            
                            path.socket.sendto(packet, path.target)

                            sequence_number += 1
                            current_position += 1

                            path.packet_slots -= 1

                    send_control_message(const.BATCH_FIN_MSG)

                    packet, addr = reverse_path.recvfrom(128)

                    delays = list(map(int, packet.decode('utf-8').split(',')))
                    
                    update_path_delays(path_array, delays)

                    next_position = current_position + const.BATCH_SIZE
                    next_position = next_position if elements > next_position else elements # Check if the next position is overflowing
                    
                send_control_message(const.FIN_MSG)
                print('The file was sent successfully!')
                return

main()