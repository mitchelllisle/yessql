#!/usr/bin/env sh
set -e

cd /source
pip install poetry
make install
make install-tests
make test
