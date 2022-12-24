#! /bin/bash
sudo docker container stop vpnserver
sudo docker container prune -f
sudo docker image prune -f
sudo docker build -f dockerfile -t marsara/vpnserver:latest .