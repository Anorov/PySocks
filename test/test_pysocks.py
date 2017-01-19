from unittest import TestCase
import unittest
import socks
import socket
import six
if six.PY3:
    import urllib.request as urllib2
else:
    import urllib2
import sockshandler

from test import config

# The 10.0.0.0 IP is used to emulate connection timeout errors
NON_ROUTABLE_IP = '10.0.0.0'


# TODO: test in all tests that remote IP is proxy
# use 127.0.0.2 for proxy server

class PySocksTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        assert config.test_server is not None
        cls.test_server = config.test_server

    def setUp(self):
        self.test_server.reset()

    def build_http_request(self, host, port):
        if port == 80:
            port_fragment = ''
        else:
            port_fragment = ':%d' % port
        return (
            'GET / HTTP/1.1\r\n'
            'Host: %s%s\r\n'
            'User-Agent: PySocksTester\r\n'
            'Accept: text/html\r\n'
            '\r\n' % (host, port_fragment)
        ).encode()

    def assertProxyResponse(self, resp_data, content, address,
                            user_agent='PySockTester'):
        status = resp_data.splitlines()[0]
        resp_body = resp_data.split(b'\r\n\r\n')[1]
        self.assertEqual(b'HTTP/1.1 200 OK', status)
        self.assertEqual('PySocksTester',
                         self.test_server.request['headers']['user-agent'])
        self.assertEqual('%s:%d' % address,
                         self.test_server.request['headers']['host'])
        self.assertEqual(content, resp_body)

    # 0/13
    def test_stdlib_socket(self):
        content = b'zzz'
        address = (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT)
        self.test_server.response['data'] = content
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(address)
        s.sendall(self.build_http_request(*address))
        data = s.recv(2048)
        self.assertProxyResponse(data, content, address)


    # 1/13
    def test_http_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT)
        s = socks.socksocket()
        s.set_proxy(socks.HTTP, config.PROXY_HOST_IP, config.HTTP_PROXY_PORT)
        s.connect(address)
        s.sendall(self.build_http_request(*address))
        data = s.recv(2048)
        self.assertProxyResponse(data, content, address)


    # 2/13
    def test_socks4_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT)
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS4, config.PROXY_HOST_IP, config.SOCKS4_PROXY_PORT)
        s.connect(address)
        s.sendall(self.build_http_request(*address))
        data = s.recv(2048)
        self.assertProxyResponse(data, content, address)


    # 3/13
    def test_socks5_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT)
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, config.PROXY_HOST_IP, config.SOCKS5_PROXY_PORT)
        s.connect(address)
        s.sendall(self.build_http_request(*address))
        data = s.recv(2048)
        self.assertProxyResponse(data, content, address)

    # 3-1/13
    def test_urllib2_http_handler(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        opener = urllib2.build_opener(sockshandler.SocksiPyHandler(
            socks.HTTP, config.PROXY_HOST_IP, config.HTTP_PROXY_PORT))
        res = opener.open(self.test_server.get_url())
        body = res.read()
        self.assertTrue(self.test_server.request['headers']['user-agent']
                            .startswith('Python-urllib'))
        self.assertEqual('%s:%d' % (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT),
                         self.test_server.request['headers']['host'])
        self.assertEqual(200, res.getcode())
        self.assertEqual(content, body)


    # 3-2/13
    def test_urllib2_socks4_handler(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        opener = urllib2.build_opener(sockshandler.SocksiPyHandler(
            socks.SOCKS4, config.PROXY_HOST_IP, config.SOCKS4_PROXY_PORT))
        res = opener.open(self.test_server.get_url())
        body = res.read()
        self.assertTrue(self.test_server.request['headers']['user-agent']
                            .startswith('Python-urllib'))
        self.assertEqual('%s:%d' % (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT),
                         self.test_server.request['headers']['host'])
        self.assertEqual(200, res.getcode())
        self.assertEqual(content, body)


    # 3-3/13
    def test_urllib2_socks5_handler(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        opener = urllib2.build_opener(sockshandler.SocksiPyHandler(
            socks.SOCKS5, config.PROXY_HOST_IP, config.SOCKS5_PROXY_PORT))
        res = opener.open(self.test_server.get_url())
        body = res.read()
        self.assertTrue(self.test_server.request['headers']['user-agent']
                            .startswith('Python-urllib'))
        self.assertEqual('%s:%d' % (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT),
                         self.test_server.request['headers']['host'])
        self.assertEqual(200, res.getcode())
        self.assertEqual(content, body)


    # 4/13
    def test_http_ip_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (config.TEST_SERVER_HOST_IP, config.TEST_SERVER_PORT)
        s = socks.socksocket()
        s.set_proxy(socks.HTTP, config.PROXY_HOST_IP, config.HTTP_PROXY_PORT)
        s.connect(address)
        s.sendall(self.build_http_request(*address))
        data = s.recv(2048)
        self.assertProxyResponse(data, content, address)


    # 5/13
    def test_socks4_ip_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (config.TEST_SERVER_HOST_IP, config.TEST_SERVER_PORT)
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS4, config.PROXY_HOST_IP, config.SOCKS4_PROXY_PORT)
        s.connect(address)
        s.sendall(self.build_http_request(*address))
        data = s.recv(2048)
        self.assertProxyResponse(data, content, address)


    # 6/13
    def test_socks5_ip_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (config.TEST_SERVER_HOST_IP, config.TEST_SERVER_PORT)
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, config.PROXY_HOST_IP, config.SOCKS5_PROXY_PORT)
        s.connect(address)
        s.sendall(self.build_http_request(*address))
        data = s.recv(2048)
        self.assertProxyResponse(data, content, address)


    # 7/13
    def test_socks5_proxy_connect_timeout(self):
        """Test timeout during connecting to the proxy server"""
        s = socks.socksocket()
        s.settimeout(0.1)
        s.set_proxy(socks.SOCKS5, NON_ROUTABLE_IP, config.SOCKS5_PROXY_PORT)
        address = (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT)
        self.assertRaises(socks.ProxyConnectionError, s.connect,
                          address)

        s = socks.socksocket()
        s.settimeout(0.1)
        s.set_proxy(socks.SOCKS5, NON_ROUTABLE_IP, config.SOCKS5_PROXY_PORT)
        address = (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT)
        try:
            s.connect(address)
        except socks.ProxyConnectionError as ex:
            self.assertEqual(str(ex.socket_err), 'timed out')
        else:
            assert False


    # 8/13
    def test_socks5_negotiation_timeout(self):
        """Test timeout during connectionto to destination server"""
        s = socks.socksocket()
        s.settimeout(0.1)
        s.set_proxy(socks.SOCKS5, config.PROXY_HOST_IP, config.SOCKS5_PROXY_PORT)
        address = (NON_ROUTABLE_IP, config.TEST_SERVER_PORT)
        self.assertRaises(socks.GeneralProxyError, s.connect,
                          address)

        s = socks.socksocket()
        s.settimeout(0.1)
        s.set_proxy(socks.SOCKS5, config.PROXY_HOST_IP, config.SOCKS5_PROXY_PORT)
        address = (NON_ROUTABLE_IP, config.TEST_SERVER_PORT)
        try:
            s.connect(address)
        except socks.GeneralProxyError as ex:
            self.assertEqual(str(ex.socket_err), 'timed out')
        else:
            assert False


    # 8-1/13
    def test_socks5_read_timeout(self):
        """Test timeout during reading from the connected remote server"""
        self.test_server.response['sleep'] = 5

        s = socks.socksocket()
        s.settimeout(0.1)
        s.set_proxy(socks.SOCKS5, config.PROXY_HOST_IP, config.SOCKS5_PROXY_PORT)
        address = (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT)

        def func():
            s.connect(address)
            s.recv(1)

        self.assertRaises(socket.timeout, func)

    # 9/13
    @unittest.skipIf(six.PY3, 'test_server error on py3k')
    def test_urllib2_http(self):
        # TODO: fix error on py3k
        '''
        ..........ERROR:tornado.application:Exception in callback (<socket.socket fd=8, family=AddressFamily.AF_INET, type=2049, proto=6, laddr=('127.0.0.1', 7777)>, <function wrap.<locals>.null_wrapper at 0x7f23ca31dd90>)
        Traceback (most recent call last):
          File "/usr/local/lib/python3.4/dist-packages/tornado/ioloop.py", line 887, in start
            handler_func(fd_obj, events)
          File "/usr/local/lib/python3.4/dist-packages/tornado/stack_context.py", line 275, in null_wrapper
            return fn(*args, **kwargs)
          File "/usr/local/lib/python3.4/dist-packages/tornado/netutil.py", line 260, in accept_handler
            connection, address = sock.accept()
          File "/usr/lib/python3.4/socket.py", line 185, in accept
            sock = socket(self.family, self.type, self.proto, fileno=fd)
          File "/home/lorien/web/PySocks/socks.py", line 258, in __init__
            raise ValueError(msg.format(type))
        ValueError: Socket type must be stream or datagram, not 2049
        '''
        content = b'zzz'
        self.test_server.response['data'] = content
        socks.set_default_proxy(socks.HTTP, config.PROXY_HOST_IP,
                                config.HTTP_PROXY_PORT)
        socks.wrap_module(urllib2)
        address = (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT)
        res = urllib2.urlopen(self.test_server.get_url())
        resp_body = res.read()
        self.assertEqual(200, res.getcode())
        self.assertTrue(self.test_server.request['headers']['user-agent']
                            .startswith('Python-urllib'))
        self.assertEqual('%s:%d' % address,
                         self.test_server.request['headers']['host'])
        self.assertEqual(content, resp_body)


    # 10/13
    @unittest.skipIf(six.PY3, 'test_server error on py3k')
    def test_urllib2_socks5(self):
        # TODO: fix error on py3k
        content = b'zzz'
        self.test_server.response['data'] = content
        socks.set_default_proxy(socks.SOCKS5, config.PROXY_HOST_IP,
                                config.SOCKS5_PROXY_PORT)
        socks.wrap_module(urllib2)
        address = (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT)
        res = urllib2.urlopen(self.test_server.get_url())
        resp_body = res.read()
        self.assertEqual(200, res.getcode())
        self.assertTrue(self.test_server.request['headers']['user-agent']
                            .startswith('Python-urllib'))
        self.assertEqual('%s:%d' % address,
                         self.test_server.request['headers']['host'])
        self.assertEqual(content, resp_body)


    # 11/13
    @unittest.skipIf(six.PY3, 'test_server error on py3k')
    def test_global_override_http(self):
        # TODO: fix error on py3k
        original_socket = socket.socket
        try:
            content = b'zzz'
            self.test_server.response['data'] = content
            socks.set_default_proxy(socks.HTTP, config.PROXY_HOST_IP,
                                    config.HTTP_PROXY_PORT)
            socket.socket = socks.socksocket
            address = (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT)
            res = urllib2.urlopen(self.test_server.get_url())
            resp_body = res.read()
            self.assertEqual(200, res.getcode())
            self.assertTrue(self.test_server.request['headers']['user-agent']
                                .startswith('Python-urllib'))
            self.assertEqual('%s:%d' % address,
                             self.test_server.request['headers']['host'])
            self.assertEqual(content, resp_body)
        finally:
            socket.socket = original_socket


    # 12/13
    @unittest.skipIf(six.PY3, 'test_server error on py3k')
    def test_global_override_socks5(self):
        # TODO: fix error on py3k
        original_socket = socket.socket
        try:
            content = b'zzz'
            self.test_server.response['data'] = content
            socks.set_default_proxy(socks.SOCKS5, config.PROXY_HOST_IP,
                                    config.SOCKS5_PROXY_PORT)
            socket.socket = socks.socksocket
            address = (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT)
            res = urllib2.urlopen(self.test_server.get_url())
            resp_body = res.read()
            self.assertEqual(200, res.getcode())
            self.assertTrue(self.test_server.request['headers']['user-agent']
                                .startswith('Python-urllib'))
            self.assertEqual('%s:%d' % address,
                             self.test_server.request['headers']['host'])
            self.assertEqual(content, resp_body)
        finally:
            socket.socket = original_socket

    # 12/13
    def test_ipv6(self):
        sock = socks.socksocket()
        ipv6_tuple = addr, port, flowinfo, scopeid = "::1", 1234, 0, 0
        self.assertRaises(socket.error, sock.connect, ipv6_tuple)
