#!/bin/bash

set -e
set -x

if [[ -n "$PYENV_VERSION" ]]; then
    if [ ! -e "$HOME/.pyenv-xattr/.git" ]; then
      if [ -e "$HOME/.pyenv-xattr" ]; then
        rm -rf ~/.pyenv-xattr
      fi
      git clone https://github.com/yyuu/pyenv.git ~/.pyenv-xattr
    fi
    PYENV_ROOT="$HOME/.pyenv-xattr"
    PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    hash -r
    pyenv install --list
    pyenv install -s $PYENV_VERSION
    pip install wheel
fi
