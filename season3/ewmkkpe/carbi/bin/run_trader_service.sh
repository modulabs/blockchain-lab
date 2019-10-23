#!/usr/bin/env bash

nohup python -u run_trader.py $* >> logs/trader.out 2>> logs/trader.err < /dev/null &
