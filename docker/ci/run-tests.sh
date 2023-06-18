#!/usr/bin/env sh
set -e

cd /source
curl -sSL https://install.python-poetry.org | python3 -
make install
make install-tests
make test
