#! /usr/bin/env bash
set -e
set -x

python /app/app/tests_pre_start.py

bash ./scripts/specific-tests.sh $1
