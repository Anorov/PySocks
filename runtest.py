#!/usr/bin/env python
"""
To run this tests you need python2.7
EVEN if you run tests agains python3.x
because twisted socsk4 proxy server could be run
only on python2.7
"""
import unittest
import sys
import psutil
import os
import signal
import logging
from subprocess import Popen
from threading import Thread
import threading
from test_server import TestServer
import time
import socket

from test.test_pysocks import PySocksTestCase
from test import config
from test.util import wait_for_socket


def proxy_thread():
    with open('3proxy.conf', 'w') as out:
        out.write('\n'.join((
            'allow *',
            'auth none',
            'proxy -a -n -p%d -e%s' % (config.HTTP_PROXY_PORT,
                                        config.PROXY_HOST_IP),
            'socks -p%d -e%s' % (config.SOCKS4_PROXY_PORT,
                                  config.PROXY_HOST_IP),
            'socks -p%d -e%s' % (config.SOCKS5_PROXY_PORT,
                                  config.PROXY_HOST_IP),
        )))
    cmd = 'test/bin/3proxy 3proxy.conf'
    server = Popen(cmd, shell=True)
    server.wait()


def start_servers():
    th = Thread(target=proxy_thread)
    th.daemon = True
    th.start()
    wait_for_socket('3proxy:http', config.PROXY_HOST_IP,
                    config.HTTP_PROXY_PORT)
    wait_for_socket('3proxy:socks4', config.PROXY_HOST_IP,
                    config.SOCKS4_PROXY_PORT)
    wait_for_socket('3proxy:socks5', config.PROXY_HOST_IP,
                    config.SOCKS5_PROXY_PORT)


def main():
    result = None
    try:
        start_servers()
        #time.sleep(1) # let CPU to process all this proxy stuff

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(PySocksTestCase)
        runner = unittest.TextTestRunner()
        result = runner.run(suite)
    except Exception as ex:
        logging.error('', exc_info=ex)
    finally:
        print('Active threads:')
        for th in threading.enumerate():
            print(' * %s' % th)

        parent = psutil.Process(os.getpid())
        print('Active child processes:')
        for child in parent.children(recursive=True):
            print(' * %s' % child)
            child.send_signal(signal.SIGINT)

    if result and result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
