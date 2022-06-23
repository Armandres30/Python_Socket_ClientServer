### First build docker image
docker build . -t simple_server

docker run -p 8000:8000 .

## Ressource for multicasting implementation
## https://wiki.python.org/moin/UdpCommunication