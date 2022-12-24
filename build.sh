#! /bin/bash
docker container stop vpnserver
docker container prune -f
docker image prune -f
docker build -f dockerfile -t marsara9/vpnserver:latest .