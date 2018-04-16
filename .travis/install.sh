#!/bin/bash

set -e
set -x

if [[ -n "$PYENV_VERSION" ]]; then
    if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
        brew update && brew upgrade pyenv
        brew install readline xz
    fi
    eval "$(pyenv init -)"
    pyenv install --list
    if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
        CFLAGS="-I$(xcrun --show-sdk-path)/usr/include" pyenv install -s "$PYENV_VERSION"
    else
        pyenv install -s "$PYENV_VERSION"
    fi
    pyenv rehash
    python -m pip install wheel
    python -m pip install pip==9.0.3
fi
