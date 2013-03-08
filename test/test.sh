#!/bin/bash
echo "Starting proxy servers..."
python socks4server.py > /dev/null 2>&1 &
python httpproxy.py > /dev/null 2>&1 &
./mocks start >/dev/null 2>&1 &

sleep 2
echo "Python 2.x tests"
python sockstest.py

sleep 2
echo "Python 3.x tests"
python3 sockstest.py

pkill python > /dev/null 2>&1
pkill mocks > /dev/null 2>&1
echo "Finished tests"
