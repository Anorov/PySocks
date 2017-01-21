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
from test_server import TestServer

from test.util import wait_for_socket
from test import config

# The 10.0.0.0 IP is used to emulate connection timeout errors
NON_ROUTABLE_IP = '10.0.0.0'


def start_extra_test_server():
    from multiprocessing import Event, Process, Queue

    def server_process(wait_event, server_queue):
        test_server = TestServer(address=config.TEST_SERVER_HOST_IP,
                                 port=config.TEST_SERVER_EXTRA_PORT)
        test_server.start()
        test_server.response['data'] = b'zzz'
        wait_event.wait()
        server_queue.put(test_server.request)
        test_server.stop()

    wait_event = Event()
    server_queue = Queue()
    proc = Process(target=server_process, args=[wait_event, server_queue])
    proc.daemon = True
    proc.start()
    wait_for_socket('extra-test-server', config.TEST_SERVER_HOST_IP,
                                         config.TEST_SERVER_EXTRA_PORT)
    return wait_event, server_queue


class PySocksTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_server = TestServer(address=config.TEST_SERVER_HOST,
                                     port=config.TEST_SERVER_PORT)
        cls.test_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.test_server.stop()

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
                            user_agent='PySockTester', client_ip=None):
        status = resp_data.splitlines()[0]
        resp_body = resp_data.split(b'\r\n\r\n')[1]
        self.assertEqual(b'HTTP/1.1 200 OK', status)
        self.assertEqual('PySocksTester',
                         self.test_server.request['headers']['user-agent'])
        self.assertEqual('%s:%d' % address,
                         self.test_server.request['headers']['host'])
        self.assertEqual(content, resp_body)
        self.assertEqual(client_ip or config.PROXY_HOST_IP,
                         self.test_server.request['client_ip'])

    # 0/13
    def test_stdlib_socket(self):
        content = b'zzz'
        address = (config.TEST_SERVER_HOST, config.TEST_SERVER_PORT)
        self.test_server.response['data'] = content
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(address)
        s.sendall(self.build_http_request(*address))
        data = s.recv(2048)
        self.assertProxyResponse(data, content, address,
                                 client_ip=config.TEST_SERVER_HOST_IP)


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
    # TODO: imeplement server that accept connection slowly
    #def test_socks5_negotiation_timeout(self):
    #    """Test timeout during connection to to destination server"""
    #    s = socks.socksocket()
    #    s.settimeout(0.01)
    #    s.set_proxy(socks.SOCKS5, config.PROXY_HOST_IP, config.SOCKS5_PROXY_PORT)
    #    address = (NON_ROUTABLE_IP, config.TEST_SERVER_PORT)
    #    self.assertRaises(socks.GeneralProxyError, s.connect,
    #                      address)

    #    s = socks.socksocket()
    #    s.settimeout(0.1)
    #    s.set_proxy(socks.SOCKS5, config.PROXY_HOST_IP, config.SOCKS5_PROXY_PORT)
    #    address = (NON_ROUTABLE_IP, config.TEST_SERVER_PORT)
    #    try:
    #        s.connect(address)
    #    except socks.GeneralProxyError as ex:
    #        self.assertEqual(str(ex.socket_err), 'timed out')
    #    else:
    #        assert False


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
    def test_urllib2_http(self):
        wait_event, server_queue = start_extra_test_server()
        original_socket = urllib2.socket.socket
        try:
            socks.set_default_proxy(socks.HTTP, config.PROXY_HOST_IP,
                                    config.HTTP_PROXY_PORT)
            socks.wrap_module(urllib2)
            address = (config.TEST_SERVER_HOST,
                       config.TEST_SERVER_EXTRA_PORT)
            url = 'http://%s:%d/' % address 
            res = urllib2.urlopen(url)
            resp_body = res.read()
            wait_event.set()
            request = server_queue.get(block=True, timeout=1)
            self.assertEqual(200, res.getcode())
            self.assertEqual(b'zzz', resp_body)

            self.assertTrue(request['headers']['user-agent']
                                .startswith('Python-urllib'))
            self.assertEqual('%s:%d' % address,
                             request['headers']['host'])
        finally:
            urllib2.socket.socket = original_socket


    # 10/13
    def test_urllib2_socks5(self):
        wait_event, server_queue = start_extra_test_server()
        original_socket = urllib2.socket.socket
        try:
            socks.set_default_proxy(socks.SOCKS5, config.PROXY_HOST_IP,
                                    config.SOCKS5_PROXY_PORT)
            socks.wrap_module(urllib2)
            address = (config.TEST_SERVER_HOST,
                       config.TEST_SERVER_EXTRA_PORT)
            url = 'http://%s:%d/' % address 
            res = urllib2.urlopen(url)
            resp_body = res.read()
            wait_event.set()
            request = server_queue.get(block=True, timeout=1)
            self.assertEqual(200, res.getcode())
            self.assertEqual(b'zzz', resp_body)

            self.assertTrue(request['headers']['user-agent']
                                .startswith('Python-urllib'))
            self.assertEqual('%s:%d' % address,
                             request['headers']['host'])
        finally:
            urllib2.socket.socket = original_socket


    # 11/13
    def test_global_override_http(self):
        wait_event, server_queue = start_extra_test_server()
        original_socket = socket.socket
        try:
            socks.set_default_proxy(socks.HTTP, config.PROXY_HOST_IP,
                                    config.HTTP_PROXY_PORT)
            socket.socket = socks.socksocket
            address = (config.TEST_SERVER_HOST,
                       config.TEST_SERVER_EXTRA_PORT)
            url = 'http://%s:%d/' % address 
            res = urllib2.urlopen(url)
            resp_body = res.read()
            wait_event.set()
            request = server_queue.get(block=True, timeout=1)
            self.assertEqual(200, res.getcode())
            self.assertEqual(b'zzz', resp_body)

            self.assertTrue(request['headers']['user-agent']
                                .startswith('Python-urllib'))
            self.assertEqual('%s:%d' % address,
                             request['headers']['host'])
        finally:
            socket.socket = original_socket


    # 12/13
    def test_global_override_socks5(self):
        wait_event, server_queue = start_extra_test_server()
        original_socket = socket.socket
        try:
            socks.set_default_proxy(socks.SOCKS5, config.PROXY_HOST_IP,
                                    config.SOCKS5_PROXY_PORT)
            socket.socket = socks.socksocket
            address = (config.TEST_SERVER_HOST,
                       config.TEST_SERVER_EXTRA_PORT)
            url = 'http://%s:%d/' % address 
            res = urllib2.urlopen(url)
            resp_body = res.read()
            wait_event.set()
            request = server_queue.get(block=True, timeout=1)
            self.assertEqual(200, res.getcode())
            self.assertEqual(b'zzz', resp_body)

            self.assertTrue(request['headers']['user-agent']
                                .startswith('Python-urllib'))
            self.assertEqual('%s:%d' % address,
                             request['headers']['host'])
        finally:
            socket.socket = original_socket

    # 12/13
    def test_ipv6(self):
        sock = socks.socksocket()
        ipv6_tuple = addr, port, flowinfo, scopeid = "::1", 1234, 0, 0
        self.assertRaises(socket.error, sock.connect, ipv6_tuple)
