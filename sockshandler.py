#!/usr/bin/env python
"""
SocksiPy + urllib2 handler

version: 0.3
author: e<e@tr0ll.in>

This module provides a Handler which you can use with urllib2 to allow it to tunnel your connection through a socks.sockssocket socket, with out monkey patching the original socket...
"""
import socket
import ssl
import time

try:
    import urllib2
    import httplib
except ImportError: # Python 3
    import urllib.request as urllib2
    import http.client as httplib

import socks # $ pip install PySocks


def is_ip(s):
    try:
        if ':' in s:
            socket.inet_pton(socket.AF_INET6, s)
        elif '.' in s:
            socket.inet_aton(s)
        else:
            return False
    except:
        return False
    else:
        return True

socks4_no_rdns = set()

class SocksiPyConnection(httplib.HTTPConnection):
    def __init__(self, host, proxytype, proxyaddr, proxyport=None, rdns=None, username=None, password=None, **kwargs):
        self.proxyargs = proxytype, proxyaddr, proxyport, rdns, username, password
        httplib.HTTPConnection.__init__(self, host, **kwargs)

    def connect(self):
        proxytype, proxyaddr, proxyport, rdns, username, password = self.proxyargs
        if rdns is None:
            # SOCKS4 disable rdns by default
            rdns = proxytype is not socks.SOCKS4
        if rdns:
            rdns = proxyaddr not in socks4_no_rdns

        try_num = 3 if rdns and proxytype is socks.SOCKS4 else 2
        rest = 3
        ex = None
        sock = None
        
        for i in range(try_num):
            try:
                sock = socks.create_connection(
                    (self.host, self.port), self.timeout, None,
                    proxytype, proxyaddr, proxyport, rdns, username, password)
                break
            except socks.SOCKS4Error as e:
                ex = e
                if rdns and e.msg[:4] == "0x5b" and not is_ip(self.host):
                    # Maybe a SOCKS4 server that doesn't support remote resolving
                    # Disable rdns and try again
                    rdns = False
                    socks4_no_rdns.add(proxyaddr)
                else:
                    raise e
            except socks.GeneralProxyError as e:
                ex = e
                if e.msg != "Connection closed unexpectedly":
                    raise e
            except socks.ProxyConnectionError as e:
                ex = e

            # Need a rest befor retry
            if i + 1 < try_num:
                time.sleep(rest)

        if sock is None:
            raise ex
        self.sock = sock

class SocksiPyConnectionS(httplib.HTTPSConnection):
    def __init__(self, host, proxytype, proxyaddr, proxyport=None, rdns=True, username=None, password=None, **kwargs):
        self.proxyargs = proxytype, proxyaddr, proxyport, rdns, username, password
        httplib.HTTPSConnection.__init__(self, host, **kwargs)

    def connect(self):
        # Attribute `_check_hostname` used in python 3.2 to 3.6
        check_hostname = getattr(self, "_check_hostname", None)
        if check_hostname:
            self._context.check_hostname = check_hostname
        SocksiPyConnection.connect(self)
        self.sock = self._context.wrap_socket(self.sock, server_hostname=self.host)

class SocksiPyHandler(urllib2.HTTPHandler, urllib2.HTTPSHandler):
    def __init__(self, *args, **kwargs):
        debuglevel = kwargs.pop("debuglevel", 0)
        self.args = args
        self.kwargs = kwargs
        urllib2.HTTPSHandler.__init__(self, debuglevel=debuglevel)

    def http_open(self, req):
        def build(host, **kwargs):
            conn = SocksiPyConnection(host, *self.args, **kwargs)
            return conn
        return self.do_open(build, req, **self.kwargs)

    def https_open(self, req):
        def build(host, **kwargs):
            conn = SocksiPyConnectionS(host, *self.args, **kwargs)
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
