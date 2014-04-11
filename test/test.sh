#!/bin/bash
echo "Starting proxy servers..."
python2 socks4server.py > /dev/null &
python2 httpproxy.py > /dev/null &
./mocks start

sleep 2
echo "Python 2.x tests"
python2 sockstest.py

sleep 2
echo "Python 3.x tests"
python3 sockstest.py

pkill python2 > /dev/null
./mocks shutdown
echo "Finished tests"
