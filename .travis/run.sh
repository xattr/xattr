#!/bin/bash

set -e
set -x

if [[ -n "$PYENV_VERSION" ]]; then
    eval "$(pyenv init -)"
fi

pip install pip==9.0.3
python setup.py build_ext -i
python -m compileall -f .
python setup.py test

if [[ -n "$PYENV_VERSION" && $TRAVIS_OS_NAME == 'osx' ]]; then
    python setup.py bdist_wheel
fi
if [[ $BUILD_SDIST == 'true' ]]; then
    python setup.py sdist
fi
