#!/usr/bin/env python
"""
SocksiPy + urllib2 handler

version: 0.3
author: e<e@tr0ll.in>

This module provides a Handler which you can use with urllib2 to allow it to tunnel your connection through a socks.sockssocket socket, with out monkey patching the original socket...
"""
import socket
import ssl

try:
    import urllib2
    import httplib
except ImportError: # Python 3
    import urllib.request as urllib2
    import http.client as httplib

import socks # $ pip install PySocks


def is_ipv4(s):
    try:
        socket.inet_aton(s)
    except:
        return False
    else:
        return True

socks4_no_rdns = set()

class SocksiPyConnection(httplib.HTTPConnection):
    def __init__(self, proxyargs, host, **kwargs):
        self.proxyargs = proxyargs
        httplib.HTTPConnection.__init__(self, host, **kwargs)

    def connect(self):
        proxytype, proxyaddr, proxyport, rdns, username, password = self.proxyargs
        if rdns is None:
            # SOCKS4 disable rdns by default
            rdns = proxytype is not socks.SOCKS4
        if rdns:
            rdns = (proxyaddr, proxyport) not in socks4_no_rdns
        
        while True:
            try:
                self.sock = socks.create_connection(
                        (self.host, self.port), self.timeout, None,
                        proxytype, proxyaddr, proxyport, rdns, username, password,
                        ((socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),))
                break
            except socks.SOCKS4Error as e:
                if rdns and e.msg[:4] == "0x5b" and not is_ipv4(self.host):
                    # Maybe a SOCKS4 server that doesn't support remote resolving
                    # Disable rdns and try again
                    rdns = False
                    socks4_no_rdns.add((proxyaddr, proxyport))
                else:
                    raise e

class SocksiPyConnectionS(httplib.HTTPSConnection):
    def __init__(self, proxyargs, host, **kwargs):
        self.proxyargs = proxyargs
        httplib.HTTPSConnection.__init__(self, host, **kwargs)

    def connect(self):
        # Attribute `_check_hostname` used in python 3.2 to 3.6
        check_hostname = getattr(self, "_check_hostname", None)
        if check_hostname:
            self._context.check_hostname = check_hostname
        SocksiPyConnection.connect(self)
        self.sock = self._context.wrap_socket(self.sock, server_hostname=self.host)

class SocksiPyHandler(urllib2.ProxyHandler, urllib2.HTTPHandler, urllib2.HTTPSHandler):
    def __init__(self, proxytype, proxyaddr, proxyport=None, rdns=None,
                       username=None, password=None, debuglevel=0, **kwargs):
        self.proxyargs = proxytype, proxyaddr, proxyport, rdns, username, password
        self.kwargs = kwargs
        urllib2.HTTPSHandler.__init__(self, debuglevel=debuglevel)

    def http_open(self, req):
        def build(host, **kwargs):
            conn = SocksiPyConnection(self.proxyargs, host, **kwargs)
            return conn
        return self.do_open(build, req, **self.kwargs)

    def https_open(self, req):
        def build(host, **kwargs):
            conn = SocksiPyConnectionS(self.proxyargs, host, **kwargs)
            return conn
        return self.do_open(build, req, **self.kwargs)

if __name__ == "__main__":
    import sys
    try:
        port = int(sys.argv[1])
    except (ValueError, IndexError):
        port = 9050
    opener = urllib2.build_opener(SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, "localhost", port))
    print("HTTP: " + opener.open("http://httpbin.org/ip").read().decode())
    print("HTTPS: " + opener.open("https://httpbin.org/ip").read().decode())
