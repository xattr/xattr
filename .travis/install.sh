#!/bin/bash

set -e
set -x

if [[ -n "$PYENV_VERSION" ]]; then
    if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
        brew update >/dev/null
        brew upgrade readline openssl
        brew install expat xz
        brew upgrade pyenv
    fi
    eval "$(pyenv init -)"
    pyenv install --list
    if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
        CFLAGS="-I$(xcrun --show-sdk-path)/usr/include /usr/local/opt/expat/include $CFLAGS" \
        pyenv install -s "$PYENV_VERSION"
    else
        pyenv install -s "$PYENV_VERSION"
    fi
    pyenv rehash
    python -m pip install wheel
fi
