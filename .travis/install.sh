#!/bin/bash

set -e
set -x

if [[ -n "$PYENV_VERSION" ]]; then
    if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
        brew update && brew upgrade pyenv
    fi
    eval "$(pyenv init -)"
    pyenv install --list
    pyenv install -s "$PYENV_VERSION"
    pip install wheel
fi
