#!/usr/bin/env python
import unittest
import sys

from test.test_pysocks import PySocksTestCase


def main():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(PySocksTestCase)
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    if result.wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
