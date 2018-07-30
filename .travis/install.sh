#!/bin/bash

set -e
set -x

install_pypy() {
    pypy_dir="/home/travis/pypy"
    curl -L "$PYPY_URL" -o "pypy.tar.bz2"
    mkdir "$pypy_dir"
    tar xf "pypy.tar.bz2" -C "$pypy_dir" --strip-components=1
    if [ -f "$pypy_dir/bin/pypy" ]; then
        ln -s "$pypy_dir/bin/pypy" "pypy"
    elif [ -f "$pypy_dir/bin/pypy3" ]; then
        ln -s "$pypy_dir/bin/pypy3" "pypy"
    fi
    ./pypy -m ensurepip
}

install_pyenv() {
    brew update  > /dev/null
    brew upgrade readline openssl pyenv
    eval "$(pyenv init -)"
    pyenv install -sv "$PYENV_VERSION"
    pip install --upgrade pip
    pyenv rehash
    python -m pip install wheel
}

if [[ -n "$PYPY_URL" ]]; then
    install_pypy
elif [[ -n "$PYENV_VERSION" && "$TRAVIS_OS_NAME" == "osx" ]]; then
    install_pyenv
fi
