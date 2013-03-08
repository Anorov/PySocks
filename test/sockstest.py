import sys
sys.path.append("..")
import socks
import socket

PY3K = sys.version_info.major == 3

if PY3K:
    import urllib.request as urllib2    
else:
    import sockshandler
    import urllib2

def raw_HTTP_request():
    req = "GET /ip/ HTTP/1.1\r\n"
    req += "Host: api.externalip.net\r\n"
    req += "User-Agent: Mozilla\r\n"
    req += "Accept: text/html\r\n"
    req += "\r\n"
    return req.encode()

def socket_HTTP_test():
    s = socks.socksocket()
    s.setproxy(socks.PROXY_TYPE_HTTP, "127.0.0.1", 8080)
    s.connect(("api.externalip.net", 80))
    s.sendall(raw_HTTP_request())
    status = s.recv(2048).splitlines()[0]
    assert status.startswith(b"HTTP/1.1 200")

def socket_SOCKS4_test():
    s = socks.socksocket()
    s.setproxy(socks.PROXY_TYPE_SOCKS4, "127.0.0.1", 1080)
    s.connect(("api.externalip.net", 80))
    s.sendall(raw_HTTP_request())
    status = s.recv(2048).splitlines()[0]
    assert status.startswith(b"HTTP/1.1 200")

def socket_SOCKS5_test():
    s = socks.socksocket()
    s.setproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1081)
    s.connect(("api.externalip.net", 80))
    s.sendall(raw_HTTP_request())
    status = s.recv(2048).splitlines()[0]
    assert status.startswith(b"HTTP/1.1 200")

def socket_SOCKS5_auth_test():
    # TODO: add support for this test. Will need a better SOCKS5 server.
    s = socks.socksocket()
    s.setproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1081, username="a", password="b")
    s.connect(("api.externalip.net", 80))
    s.sendall(raw_HTTP_request())
    status = s.recv(2048).splitlines()[0]
    assert status.startswith(b"HTTP/1.1 200")

def socket_HTTP_IP_test():
    s = socks.socksocket()
    s.setproxy(socks.PROXY_TYPE_HTTP, "127.0.0.1", 8080)
    s.connect(("109.74.3.220", 80))
    s.sendall(raw_HTTP_request())
    status = s.recv(2048).splitlines()[0]
    assert status.startswith(b"HTTP/1.1 200")

def socket_SOCKS4_IP_test():
    s = socks.socksocket()
    s.setproxy(socks.PROXY_TYPE_SOCKS4, "127.0.0.1", 1080)
    s.connect(("109.74.3.220", 80))
    s.sendall(raw_HTTP_request())
    status = s.recv(2048).splitlines()[0]
    assert status.startswith(b"HTTP/1.1 200")

def socket_SOCKS5_IP_test():
    s = socks.socksocket()
    s.setproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1081)
    s.connect(("109.74.3.220", 80))
    s.sendall(raw_HTTP_request())
    status = s.recv(2048).splitlines()[0]
    assert status.startswith(b"HTTP/1.1 200")

def socket_SOCKS4_test():
    s = socks.socksocket()
    s.setproxy(socks.PROXY_TYPE_SOCKS4, "127.0.0.1", 1080)
    s.connect(("api.externalip.net", 80))
    s.sendall(raw_HTTP_request())
    status = s.recv(2048).splitlines()[0]
    assert status.startswith(b"HTTP/1.1 200")

def urllib2_HTTP_test():
    socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, "127.0.0.1", 8080)
    socks.wrapmodule(urllib2)
    status = urllib2.urlopen("http://api.externalip.net/ip/").getcode()
    assert status == 200

def urllib2_SOCKS5_test():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1081)
    socks.wrapmodule(urllib2)
    status = urllib2.urlopen("http://api.externalip.net/ip/").getcode()
    assert status == 200

def urllib2_handler_HTTP_test():
    opener = urllib2.build_opener(sockshandler.SocksiPyHandler(socks.PROXY_TYPE_HTTP, "127.0.0.1", 8080))
    status = opener.open("http://api.externalip.net/ip/").getcode()
    assert status == 200

def urllib2_handler_SOCKS5_test():
    opener = urllib2.build_opener(sockshandler.SocksiPyHandler(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1081))
    status = opener.open("http://api.externalip.net/ip/").getcode()
    assert status == 200

def global_override_HTTP_test():
    socks.setdefaultproxy(socks.PROXY_TYPE_HTTP, "127.0.0.1", 8080)
    good = socket.socket
    socket.socket = socks.socksocket
    status = urllib2.urlopen("http://api.externalip.net/ip/").getcode()
    socket.socket = good
    assert status == 200

def global_override_SOCKS5_test():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1081)
    good = socket.socket
    socket.socket = socks.socksocket
    status = urllib2.urlopen("http://api.externalip.net/ip/").getcode()
    socket.socket = good
    assert status == 200

def main():
    print("Running tests...")
    socket_HTTP_test()
    print("1/10")
    socket_SOCKS4_test()
    print("2/10")
    socket_SOCKS5_test()
    print("3/10")
    if not PY3K:
        urllib2_handler_HTTP_test()
        print("3.33/10")
        urllib2_handler_SOCKS5_test()
        print("3.66/10")
    socket_HTTP_IP_test()
    print("4/10")
    socket_SOCKS4_IP_test()
    print("5/10")
    socket_SOCKS5_IP_test()
    print("6/10")
    urllib2_HTTP_test()
    print("7/10")
    urllib2_SOCKS5_test()
    print("8/10")
    global_override_HTTP_test()
    print("9/10")
    global_override_SOCKS5_test()
    print("10/10")
    print("All tests ran successfully")

if __name__ == "__main__":
    main()
