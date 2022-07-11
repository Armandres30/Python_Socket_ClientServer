### First build docker image
docker build . -t simple_server

docker run -p 8000:8000 .

## Ressource for multicasting implementation
## https://wiki.python.org/moin/UdpCommunication
##  https://tutorialmeta.com/question/python-udp-socket-has-packet-loss-every-65536-packets

## https://github.com/houluy/UDP/blob/master/udp.py

## Installation requirements
pip install opencv-contrib-python
pip install opencv-python