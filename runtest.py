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
from multiprocessing import Process
from threading import Thread, Event
import threading
from test_server import TestServer
import time

from test.test_pysocks import PySocksTestCase
from test import config


def socks4_proxy_thread(shutdown_event):
    cmd = 'python2.7 test/socks4server.py %d' % config.SOCKS4_PROXY_PORT
    server = Popen(cmd, shell=True)
    server.wait()
    if not shutdown_event.is_set():
        raise Exception('socks4server process has been terminated')


def http_proxy_thread(shutdown_event):
    cmd = 'python2.7 test/httpproxy.py %d' % config.HTTP_PROXY_PORT
    server = Popen(cmd, shell=True)
    server.wait()
    if not shutdown_event.is_set():
        raise Exception('httpproxy process has been terminated')


def socks5_proxy_thread(shutdown_event):
    client_cmd = 'sslocal -l %d -k bar -m rc4-md5 -s %s -p %d' % (
        config.SOCKS5_PROXY_PORT,
        config.TEST_HOST,
        config.SOCKS5_SHADOWSOCKS_SERVER_PORT,
    )
    client = Popen(client_cmd, shell=True)
    server_cmd = 'ssserver -s %s -k bar -p %d -m rc4-md5 --forbidden-ip ""' % (
        config.TEST_HOST,
        config.SOCKS5_SHADOWSOCKS_SERVER_PORT,
    )
    server = Popen(server_cmd, shell=True)
    server.wait()
    if not shutdown_event.is_set():
        raise Exception('shadowsocks server process has been terminated')


def start_servers(shutdown_event):
    thread_targets = (
        http_proxy_thread,
        socks4_proxy_thread,
        socks5_proxy_thread,
    )
    for target in thread_targets:
        th = Thread(target=target, args=[shutdown_event])
        th.daemon = True
        th.start()

    test_server = TestServer(address=config.TEST_HOST,
                             port=config.TEST_SERVER_PORT)
    test_server.start()
    config.test_server = test_server


def main():
    result = None
    try:
        shutdown_event = Event()
        start_servers(shutdown_event) 
        time.sleep(1) # let CPU to process all this proxy stuff

        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(PySocksTestCase)
        runner = unittest.TextTestRunner()
        result = runner.run(suite)
        if config.test_server:
            config.test_server.stop()
        shutdown_event.set()
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
            child.send_signal(signal.SIGTERM)

    if result and result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
