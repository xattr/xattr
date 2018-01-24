#!/bin/bash

set -e
set -x

if [[ -n "$PYENV_VERSION" ]]; then
    if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
        brew update && brew upgrade pyenv
        brew install readline xz
        export CFLAGS="-I$(xcrun --show-sdk-path)/usr/include"
    fi
    eval "$(pyenv init -)"
    pyenv install --list
    pyenv install -s "$PYENV_VERSION"
    pyenv rehash
    python -m pip install wheel
fi
