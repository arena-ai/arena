#!/usr/bin/env bash

set -e
set -x

echo "Testing $1"
python -m pytest -s -vvv $1
