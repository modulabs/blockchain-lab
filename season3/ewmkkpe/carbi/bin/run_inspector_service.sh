#!/usr/bin/env bash

nohup python -u run_inspector.py $* >> logs/inspector.out 2>> logs/inspector.err < /dev/null &
