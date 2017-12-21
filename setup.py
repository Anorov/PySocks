#!/usr/bin/env python
import os
import sys
from setuptools import setup

VERSION = "1.6.8"

requirements = []
if os.name == "nt" and sys.version_info < (3, 0):
    # Required due to missing socket.inet_ntop & socket.inet_pton method in Windows Python 2.x
    requirements.append("win-inet-pton")

setup(
    name = "PySocks",
    version = VERSION,
    description = "A Python SOCKS client module. See https://github.com/Anorov/PySocks for more information.",
    url = "https://github.com/Anorov/PySocks",
    license = "BSD",
    author = "Anorov",
    author_email = "anorov.vorona@gmail.com",
    keywords = ["socks", "proxy"],
    py_modules=["socks", "sockshandler"],
    install_requires=requirements,
    classifiers=(
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    )
)
