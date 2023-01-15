#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_DIR="${SCRIPT_DIR}/.."
cd "${PROJECT_DIR}" || { echo >&2 "Project directory doesn't exist?"; exit 1; }

apt-get install --no-install-recommends \
    build-essential

chmod +x docker/install-bcrypt.sh

case $(uname -m) in
    "arm")
        apt-get install --no-install-recommends \
            curl

        docker/install-bcrypt.sh "linux/arm/v7"
        ;;
    "aarch64")    
        docker/install-bcrypt.sh "linux/arm64"
        ;;
    *)
        docker/install-bcrypt.sh "linux/amd64"
        ;;

pip3 install nmcli simplejson

if[ $1 == "docker" ]; then
    docker build -f docker/dockerfile -t groundhog .
