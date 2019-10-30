#!/usr/bin/env bash

nohup python -u run_seeker.py $* >> logs/seeker.out 2>> logs/seeker.err < /dev/null &
