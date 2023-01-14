#!/bin/bash
if [ "$1" = "linux/arm/v7" ]
then
    echo "Installing from Source"

    mkdir -p $HOME/.cargo
    chmod 777 $HOME/.cargo
    mount -t tmpfs none $HOME/.cargo

    curl https://sh.rustup.rs -sSf | bash -s -- -y --profile minimal

    source "$HOME/.cargo/env"

    pip3 install --verbose --no-warn-script-location --no-cache-dir --user \
            bcrypt
    
else
    echo "Installing from PyPi"
    pip3 install --verbose --no-warn-script-location --no-cache-dir --user \
        bcrypt
fi
