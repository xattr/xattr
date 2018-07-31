#!/bin/bash

set -e
set -x

if [[ -n "$PYENV_VERSION" ]]; then
    eval "$(pyenv init -)"
fi

if [[ -n "$PYPY_URL" ]]; then
    cmd=./pypy
else
    cmd=python
fi

"$cmd" setup.py build_ext -i
"$cmd" -m compileall -f .
"$cmd" setup.py test

if [[ -n "$PYENV_VERSION" && "$TRAVIS_OS_NAME" == 'osx' ]]; then
    python setup.py bdist_wheel
fi

if [[ "$BUILD_SDIST" == 'true' ]]; then
    "$cmd" setup.py sdist --formats=gztar
    # Ensure the package installs from tarball correctly.
    filename=$("$cmd" setup.py --fullname)
    pip install "dist/$filename.tar.gz"
fi
