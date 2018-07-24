#!/usr/bin/env python
import os
import sys
from setuptools import setup

VERSION = "1.6.8"

requirements = []
if os.name == "nt" and sys.version_info < (3, 0):
    # Required due to missing socket.inet_ntop & socket.inet_pton method in Windows Python 2.x
    requirements.append("win-inet-pton")

with open('README.md') as f:
    long_description = f.read()

setup(
    name = "PySocks",
    version = VERSION,
    description = "A Python SOCKS client module. See https://github.com/Anorov/PySocks for more information.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url = "https://github.com/Anorov/PySocks",
    license = "BSD",
    author = "Anorov",
    author_email = "anorov.vorona@gmail.com",
    keywords = ["socks", "proxy"],
    py_modules=["socks", "sockshandler"],
    install_requires=requirements,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    classifiers=(
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    )
)
