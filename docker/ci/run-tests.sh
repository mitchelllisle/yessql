#!/usr/bin/env sh
set -e

cd /source
make install
make install-tests
make test
