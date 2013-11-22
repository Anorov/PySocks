#!/usr/bin/env python
from distutils.core import setup

VERSION = "1.4"

setup(
    name = "PySocks",
    version = VERSION,
    description = "A Python SOCKS module",
    url = "https://github.com/AnorovPySocks",
    license = "BSD",
    py_modules=["socks"]
)

