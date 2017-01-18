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


def wait_for_socket(server_name, port, timeout=2):
    ok = False
    for x in range(10):
        try:
            print('Testing [%s] proxy server on %s:%d'
                  % (server_name, config.TEST_HOST, port))
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((config.TEST_HOST, port))
            s.close()
        except socket.error as ex:
            print('ERROR', ex)
            time.sleep(timeout/10.0)
        else:
            print('Connection established')
            ok = True
            break
    if not ok:
        raise Exception('The %s proxy server has not started in %d seconds'
                        % (server_name, timeout))


def proxy_thread():
    with open('3proxy.conf', 'w') as out:
        out.write('\n'.join((
            'allow *',
            'auth none',
            'proxy -a -n -p%d' % config.HTTP_PROXY_PORT,
            'socks -p%d' % config.SOCKS4_PROXY_PORT,
            'socks -p%d' % config.SOCKS5_PROXY_PORT,
        )))
    cmd = 'test/bin/3proxy 3proxy.conf'
    server = Popen(cmd, shell=True)
    server.wait()


def start_servers():
    th = Thread(target=proxy_thread)
    th.daemon = True
    th.start()

    test_server = TestServer(address=config.TEST_HOST,
                             port=config.TEST_SERVER_PORT)
    test_server.start()
    config.test_server = test_server

    wait_for_socket('3proxy:http', config.HTTP_PROXY_PORT)
    wait_for_socket('3proxy:socks4', config.SOCKS4_PROXY_PORT)
    wait_for_socket('3proxy:socks5', config.SOCKS5_PROXY_PORT)
    wait_for_socket('test-server', config.TEST_SERVER_PORT)


def main():
    result = None
    try:
        start_servers()
        #time.sleep(1) # let CPU to process all this proxy stuff

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(PySocksTestCase)
        runner = unittest.TextTestRunner()
        result = runner.run(suite)
        if config.test_server:
            config.test_server.stop()
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
