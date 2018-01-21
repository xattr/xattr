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
    PYENV="$PYENV_ROOT/bin/pyenv"
    PATH="$PYENV_ROOT/bin:$PATH"
    (cd "$PYENV_ROOT" && git fetch origin && git reset --hard origin/master)
    hash -r
    eval "$("$PYENV" init -)"
    hash -r
    "$PYENV" install --list
    "$PYENV" install -s "$PYENV_VERSION"
    pip install wheel
fi
