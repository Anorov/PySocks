#!/usr/bin/env python
import unittest
import sys
import threading
import psutil
import os
import signal

from test.test_pysocks import PySocksTestCase


def main():
    result = None
    try:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(PySocksTestCase)
        runner = unittest.TextTestRunner()
        result = runner.run(suite)
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
