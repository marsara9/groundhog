#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_DIR="${SCRIPT_DIR}/.."
cd "${PROJECT_DIR}" || { echo >&2 "Project directory doesn't exist?"; exit 1; }
docker container stop vpnrouter
docker container prune -f
docker image prune -f
docker build -f docker/dockerfile -t marsara9/vpnrouter:latest . || exit 1;
if [ $1 = "install" ]
then
    docker compose -f docker/docker-compose.yml up -d
fi
if [ $1 = "push" ]
then
    docker push marsara9/vpnrouter:latest
fi
