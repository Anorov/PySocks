#!/usr/bin/env python
from distutils.core import setup

VERSION = "1.5.0"

setup(
    name = "PySocks",
    version = VERSION,
    description = "A Python SOCKS module",
    url = "https://github.com/Anorov/PySocks",
    download_url = "https://github.com/Anorov/PySocks/tarball/1.5.0",
    license = "BSD",
    author_email = "anorov.vorona@gmail.com",
    keywords = ["socks", "proxy"],
    py_modules=["socks"]
)

