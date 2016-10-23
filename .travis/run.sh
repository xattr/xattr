#!/bin/bash

set -e
set -x

if [[ -n "$PYENV_VERSION" ]]; then
    PYENV_ROOT="$HOME/.pyenv-xattr"
    PATH="$PYENV_ROOT/bin:$PATH"
    hash -r
    eval "$(pyenv init -)"
fi

python setup.py build_ext -i
python -m compileall -f .
python setup.py test

if [[ -n "$PYENV_VERSION" && $TRAVIS_OS_NAME == 'osx' ]]; then
  python setup.py bdist_wheel
fi
