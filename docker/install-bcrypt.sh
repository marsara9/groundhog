#!/bin/bash
if [ "$1" = "linux/arm/v7" ]
then
    echo "Installing from Source"

    ## This is a workaround for https://github.com/rust-lang/rustup/issues/2700.
    ## Alternatively, if cryptopraphy ever uploads an armv7 wheel, I should be
    ## able to remove the rust dependency entirely, but they have some roadblocks 
    ## as outlined here: https://github.com/pyca/cryptography/issues/6286.

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
