#!/usr/bin/env python
import unittest
from test.test_pysocks import PySocksTestCase


def main():
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(PySocksTestCase)
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
    main()
