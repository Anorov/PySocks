#!/bin/bash
echo "Starting proxy servers..."
python2 socks4server.py > /dev/null 2>&1 &
python2 httpproxy.py > /dev/null 2>&1 &
./mocks start >/dev/null 2>&1 &

sleep 2
echo "Python 2.x tests"
python2 sockstest.py

sleep 2
echo "Python 3.x tests"
python3 sockstest.py

pkill python2 > /dev/null 2>&1
./mocks shutdown >/dev/null 2>&1 &
echo "Finished tests"
