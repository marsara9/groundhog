#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_DIR="${SCRIPT_DIR}/.."
cd "${PROJECT_DIR}" || { echo >&2 "Project directory doesn't exist?"; exit 1; }

if [ $1 == "docker" ]; then
    ## User chose to install via docker.  We can just use the existing dockerfile
    ## to do the build.
    docker build -f docker/dockerfile -t groundhog .
else
    ## User chose to install locally.  
    ##   1) We need to install all of the build tools if they're not already 
    ##      available.
    ##   2) Run the install-bcrypt script to the python bcrypt package depending
    ##      on the target platform, as there's currently extra steps required for
    ##      armv7 architectures
    ##   3) Finally install all of the other required python modules.

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
    esac

    pip3 install nmcli simplejson
fi
