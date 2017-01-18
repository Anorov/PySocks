from unittest import TestCase
import socks
import socket
import six
if six.PY3:
    import urllib.request as urllib2
else:
    import urllib2
import sockshandler

from test import config


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
        address = (config.TEST_HOST, config.TEST_SERVER_PORT)
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
        address = (config.TEST_HOST, config.TEST_SERVER_PORT)
        s = socks.socksocket()
        s.set_proxy(socks.HTTP, config.TEST_HOST, config.HTTP_PROXY_PORT)
        s.connect(address)
        s.sendall(self.build_http_request(*address))
        data = s.recv(2048)
        self.assertProxyResponse(data, content, address)


    # 2/13
    def test_socks4_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (config.TEST_HOST, config.TEST_SERVER_PORT)
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS4, config.TEST_HOST, config.SOCKS4_PROXY_PORT)
        s.connect(address)
        s.sendall(self.build_http_request(*address))
        data = s.recv(2048)
        self.assertProxyResponse(data, content, address)


    # 3/13
    def test_socks5_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (config.TEST_HOST, config.TEST_SERVER_PORT)
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, config.TEST_HOST, config.SOCKS5_PROXY_PORT)
        s.connect(address)
        s.sendall(self.build_http_request(*address))
        data = s.recv(2048)
        self.assertProxyResponse(data, content, address)

    # 3-1/13
    def test_urllib2_http_handler(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        opener = urllib2.build_opener(sockshandler.SocksiPyHandler(
            socks.HTTP, config.TEST_HOST, config.HTTP_PROXY_PORT))
        res = opener.open(self.test_server.get_url())
        body = res.read()
        self.assertTrue(self.test_server.request['headers']['user-agent']
                            .startswith('Python-urllib'))
        self.assertEqual('%s:%d' % (config.TEST_HOST, config.TEST_SERVER_PORT),
                         self.test_server.request['headers']['host'])
        self.assertEqual(200, res.getcode())
        self.assertEqual(content, body)


    # 3-2/13
    def test_urllib2_socks4_handler(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        opener = urllib2.build_opener(sockshandler.SocksiPyHandler(
            socks.SOCKS4, config.TEST_HOST, config.SOCKS4_PROXY_PORT))
        res = opener.open(self.test_server.get_url())
        body = res.read()
        self.assertTrue(self.test_server.request['headers']['user-agent']
                            .startswith('Python-urllib'))
        self.assertEqual('%s:%d' % (config.TEST_HOST, config.TEST_SERVER_PORT),
                         self.test_server.request['headers']['host'])
        self.assertEqual(200, res.getcode())
        self.assertEqual(content, body)


    # 3-3/13
    def test_urllib2_socks5_handler(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        opener = urllib2.build_opener(sockshandler.SocksiPyHandler(
            socks.SOCKS5, config.TEST_HOST, config.SOCKS5_PROXY_PORT))
        res = opener.open(self.test_server.get_url())
        body = res.read()
        self.assertTrue(self.test_server.request['headers']['user-agent']
                            .startswith('Python-urllib'))
        self.assertEqual('%s:%d' % (config.TEST_HOST, config.TEST_SERVER_PORT),
                         self.test_server.request['headers']['host'])
        self.assertEqual(200, res.getcode())
        self.assertEqual(content, body)

    # 4/13
    def test_http_ip_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (config.TEST_HOST_IP, config.TEST_SERVER_PORT)
        s = socks.socksocket()
        s.set_proxy(socks.HTTP, config.TEST_HOST_IP, config.HTTP_PROXY_PORT)
        s.connect(address)
        s.sendall(self.build_http_request(*address))
        data = s.recv(2048)
        self.assertProxyResponse(data, content, address)

    # 5/13
    def test_socks4_ip_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (config.TEST_HOST_IP, config.TEST_SERVER_PORT)
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS4, config.TEST_HOST_IP, config.SOCKS4_PROXY_PORT)
        s.connect(address)
        s.sendall(self.build_http_request(*address))
        data = s.recv(2048)
        self.assertProxyResponse(data, content, address)

    # 6/13
    def test_socks5_ip_proxy(self):
        content = b'zzz'
        self.test_server.response['data'] = content
        address = (config.TEST_HOST_IP, config.TEST_SERVER_PORT)
        s = socks.socksocket()
        s.set_proxy(socks.SOCKS5, config.TEST_HOST_IP, config.SOCKS5_PROXY_PORT)
        s.connect(address)
        s.sendall(self.build_http_request(*address))
        data = s.recv(2048)
        self.assertProxyResponse(data, content, address)


    #def test_urllib2(self):
    #    # ?????????????
    #    # HTTPError: 405: Method Not Allowed
    #    # [*] Note: The HTTP proxy server may not be supported by PySocks
    #    # (must be a CONNECT tunnel proxy)
    #    socks.set_default_proxy(socks.HTTP, TEST_HOST, TEST_SERVER_PORT)
    #    socks.wrap_module(urllib2)
    #    res = urllib2.urlopen(self.test_server.get_url())
    #    self.assertEqual(200, res.getcode())


#import sys
#sys.path.append("..")
#import socks
#import socket
#
#PY3K = sys.version_info[0] == 3
#
#if PY3K:
#    import urllib.request as urllib2
#else:
#    import sockshandler
#    import urllib2
#

#def SOCKS5_connect_timeout_test():
#    s = socks.socksocket()
#    s.settimeout(0.0001)
#    s.set_proxy(socks.SOCKS5, "8.8.8.8", 80)
#    try:
#        s.connect(("ifconfig.me", 80))
#    except socks.ProxyConnectionError as e:
#        assert str(e.socket_err) == "timed out"
#
#def SOCKS5_timeout_test():
#    s = socks.socksocket()
#    s.settimeout(0.0001)
#    s.set_proxy(socks.SOCKS5, "127.0.0.1", 1081)
#    try:
#        s.connect(("ifconfig.me", 4444))
#    except socks.GeneralProxyError as e:
#        assert str(e.socket_err) == "timed out"
#
#
#def socket_SOCKS5_auth_test():
#    # TODO: add support for this test. Will need a better SOCKS5 server.
#    s = socks.socksocket()
#    s.set_proxy(socks.SOCKS5, "127.0.0.1", 1081, username="a", password="b")
#    s.connect(("ifconfig.me", 80))
#    s.sendall(build_http_request())
#    status = s.recv(2048).splitlines()[0]
#    assert status.startswith(b"HTTP/1.1 200")
#
#def socket_HTTP_IP_test():
#    s = socks.socksocket()
#    s.set_proxy(socks.HTTP, "127.0.0.1", 8081)
#    s.connect(("133.242.129.236", 80))
#    s.sendall(build_http_request())
#    status = s.recv(2048).splitlines()[0]
#    assert status.startswith(b"HTTP/1.1 200")
#
#def socket_SOCKS4_IP_test():
#    s = socks.socksocket()
#    s.set_proxy(socks.SOCKS4, "127.0.0.1", 1080)
#    s.connect(("133.242.129.236", 80))
#    s.sendall(build_http_request())
#    status = s.recv(2048).splitlines()[0]
#    assert status.startswith(b"HTTP/1.1 200")
#
#def socket_SOCKS5_IP_test():
#    s = socks.socksocket()
#    s.set_proxy(socks.SOCKS5, "127.0.0.1", 1081)
#    s.connect(("133.242.129.236", 80))
#    s.sendall(build_http_request())
#    status = s.recv(2048).splitlines()[0]
#    assert status.startswith(b"HTTP/1.1 200")
#
#def urllib2_SOCKS5_test():
#    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1081)
#    socks.wrap_module(urllib2)
#    status = urllib2.urlopen("http://ifconfig.me/ip").getcode()
#    assert status == 200
#
#def urllib2_handler_HTTP_test():
#    import sockshandler
#    opener = urllib2.build_opener(sockshandler.SocksiPyHandler(socks.HTTP, "127.0.0.1", 8081))
#    status = opener.open("http://ifconfig.me/ip").getcode()
#    assert status == 200
#
#def urllib2_handler_SOCKS5_test():
#    import sockshandler
#    opener = urllib2.build_opener(sockshandler.SocksiPyHandler(socks.SOCKS5, "127.0.0.1", 1081))
#    status = opener.open("http://ifconfig.me/ip").getcode()
#    assert status == 200
#
#def global_override_HTTP_test():
#    socks.set_default_proxy(socks.HTTP, "127.0.0.1", 8081)
#    good = socket.socket
#    socket.socket = socks.socksocket
#    status = urllib2.urlopen("http://ifconfig.me/ip").getcode()
#    socket.socket = good
#    assert status == 200
#
#def global_override_SOCKS5_test():
#    default_proxy = (socks.SOCKS5, "127.0.0.1", 1081)
#    socks.set_default_proxy(*default_proxy)
#    good = socket.socket
#    socket.socket = socks.socksocket
#    status = urllib2.urlopen("http://ifconfig.me/ip").getcode()
#    socket.socket = good
#    assert status == 200
#    assert socks.get_default_proxy()[1].decode() == default_proxy[1]
#
#def bail_early_with_ipv6_test():
#    sock = socks.socksocket()
#    ipv6_tuple = addr, port, flowinfo, scopeid = "::1", 1234, 0, 0
#    try:
#        sock.connect(ipv6_tuple)
#    except socket.error:
#        return
#    else:
#        assert False, "was expecting"
#
#def main():
#    print("Running tests...")
#    socket_HTTP_test()
#    print("1/13")
#    socket_SOCKS4_test()
#    print("2/13")
#    socket_SOCKS5_test()
#    print("3/13")
#    if not PY3K:
#        urllib2_handler_HTTP_test()
#        print("3.33/13")
#        urllib2_handler_SOCKS5_test()
#        print("3.66/13")
#    socket_HTTP_IP_test()
#    print("4/13")
#    socket_SOCKS4_IP_test()
#    print("5/13")
#    socket_SOCKS5_IP_test()
#    print("6/13")

# ---- TODO: -------------

#    SOCKS5_connect_timeout_test()
#    print("7/13")
#    SOCKS5_timeout_test()
#    print("8/13")
#    urllib2_HTTP_test()
#    print("9/13")
#    urllib2_SOCKS5_test()
#    print("10/13")
#    global_override_HTTP_test()
#    print("11/13")
#    global_override_SOCKS5_test()
#    print("12/13")
#    bail_early_with_ipv6_test()
#    print("13/13")
#    print("All tests ran successfully")
#
#
#if __name__ == "__main__":
#    main()
