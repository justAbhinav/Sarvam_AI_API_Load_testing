#!/bin/bash

# Simple configuration
locust -f API_test.py --host=https://api.sarvam.ai --users=1 --spawn-rate=1 --run-time=1m --csv=simple_test --headless

# Load sweep configurations
for i in 1 2 3 4; do
    if [ $i -eq 1 ]; then
        users=1; spawn_rate=1; run_time=1m; prefix=test1
    elif [ $i -eq 2 ]; then
        users=5; spawn_rate=2; run_time=1m; prefix=test2
    elif [ $i -eq 3 ]; then
        users=10; spawn_rate=2; run_time=3m; prefix=test3
    elif [ $i -eq 4 ]; then
        users=25; spawn_rate=4; run_time=5m; prefix=test4
    fi
    locust -f API_test.py --host=https://api.sarvam.ai --users=$users --spawn-rate=$spawn_rate --run-time=$run_time --csv=$prefix --headless
done
