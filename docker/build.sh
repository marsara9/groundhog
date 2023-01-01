#! /bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_DIR="${SCRIPT_DIR}/.."
cd "${PROJECT_DIR}"
docker container stop vpnrouter
docker container prune -f
docker image prune -f
docker build -f docker/dockerfile -t marsara9/vpnrouter:latest .
if [ $1 = "install" ]
then
    docker compose -f docker/docker-compose.yml up -d
fi
