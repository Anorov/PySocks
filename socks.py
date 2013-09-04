"""SocksiPy - Python SOCKS module.
Version 1.3

Copyright 2006 Dan-Haim. All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
3. Neither the name of Dan Haim nor the names of his contributors may be used
   to endorse or promote products derived from this software without specific
   prior written permission.
   
THIS SOFTWARE IS PROVIDED BY DAN HAIM "AS IS" AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
EVENT SHALL DAN HAIM OR HIS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMANGE.


This module provides a standard socket-like interface for Python
for tunneling connections through SOCKS proxies.

===============================================================================

Minor modifications made by Christopher Gilbert (http://motomastyle.com/)
for use in PyLoris (http://pyloris.sourceforge.net/)

Minor modifications made by Mario Vilas (http://breakingcode.wordpress.com/)
mainly to merge bug fixes found in Sourceforge

Modifications made by Anorov (https://github.com/Anorov)
-Renamed to PySocks
-Fixed issue with HTTP proxy failure checking (same bug that was in the old __recvall() method)
-Included SocksiPyHandler (sockshandler.py), to be used as a urllib2 handler, 
 courtesy of e000 (https://github.com/e000): https://gist.github.com/869791#file_socksipyhandler.py
-Re-styled code to make it readable
    -Aliased PROXY_TYPE_SOCKS5 -> SOCKS5 etc.
    -Improved exception handling and output
    -Removed irritating use of sequence indexes, replaced with tuple unpacked variables
    -Fixed up Python 3 bytestring handling - chr(0x03).encode() -> b"\x03"
    -Other general fixes
-Added clarification that the HTTP proxy connection method only supports CONNECT-style tunneling HTTP proxies
"""

__version__ = "1.3"

import socket
import struct

PROXY_TYPE_SOCKS4 = SOCKS4 = 1
PROXY_TYPE_SOCKS5 = SOCKS5 = 2
PROXY_TYPE_HTTP = HTTP = 3

_orgsocket = _orig_socket = socket.socket

class ProxyError(Exception): pass
class GeneralProxyError(ProxyError): pass
class SOCKS5AuthError(ProxyError): pass
class SOCKS5Error(ProxyError): pass
class SOCKS4Error(ProxyError): pass
class HTTPError(ProxyError): pass

SOCKS4errors = { 0x5B: "Request rejected or failed",
                 0x5C: "Request rejected because SOCKS server cannot connect to identd on the client",
                 0x5D: "Request rejected because the client program and identd report different user-ids"
               }

SOCKS5errors = { 0x01: "General SOCKS server failure",
                 0x02: "Connection not allowed by ruleset",
                 0x03: "Network unreachable",
                 0x04: "Host unreachable",
                 0x05: "Connection refused",
                 0x06: "TTL expired",
                 0x07: "Command not supported, or protocol error",
                 0x08: "Address type not supported"
               }

def set_default_proxy(proxy_type=None, addr=None, port=None, rdns=True, username=None, password=None):
    """setdefault_proxy(proxy_type, addr[, port[, rdns[, username, password]]])
    Sets a default proxy which all further socksocket objects will use,
    unless explicitly changed.
    """
    #global default_proxy
    socksocket.default_proxy = (proxy_type, addr.encode(), port, rdns, 
                                username.encode() if username else None,
                                password.encode() if password else None)

setdefaultproxy = set_default_proxy

def wrap_module(module):
    """wrap_module(module)
    Attempts to replace a module's socket library with a SOCKS socket. Must set
    a default proxy using setdefault_proxy(...) first.
    This will only work on modules that import socket directly into the namespace;
    most of the Python Standard Library falls into this category.
    """
    if socksocket.default_proxy:
        module.socket.socket = socksocket
    else:
        raise GeneralProxyError("No default proxy specified")

wrapmodule = wrap_module

def create_connection(address, proxy_type=None, proxy_host=None, 
                      proxy_port=None, proxy_username=None,
                      proxy_password=None, timeout=None):
    sock = socksocket()
    if isinstance(timeout, (int, float)):
        sock.settimeout(timeout)
    sock.set_proxy(proxy_type, proxy_host, proxy_port, proxy_username, proxy_password)
    sock.connect(address)
    return sock

class socksocket(socket.socket):
    """socksocket([family[, type[, proto]]]) -> socket object
    Open a SOCKS enabled socket. The parameters are the same as
    those of the standard socket init. In order for SOCKS to work,
    you must specify family=AF_INET, type=SOCK_STREAM and proto=0.
    """

    default_proxy = None

    def __init__(self, family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0, _sock=None):
        _orig_socket.__init__(self, family, type, proto, _sock)
        
        if self.default_proxy:
            self.proxy = self.default_proxy
        else:
            self.proxy = (None, None, None, None, None, None)
        self.proxy_sockname = None
        self.proxy_peername = None

    def recvall(self, count):
        """recvall(count) -> data
        Receive EXACTLY the number of bytes requested from the socket.
        Blocks until the required number of bytes have been received.
        """
        data = self.recv(count)
        while len(data) < count:
            d = self.recv(count - len(data))
            if not d:
                raise GeneralProxyError("Connection closed unexpectedly")
            data += d
        return data

    def set_proxy(self, proxy_type=None, addr=None, port=None, rdns=True, username=None, password=None):
        """set_proxy(proxy_type, addr[, port[, rdns[, username[, password]]]])
        Sets the proxy to be used.
        proxy_type -    The type of the proxy to be used. Three types
                        are supported: PROXY_TYPE_SOCKS4 (including socks4a),
                        PROXY_TYPE_SOCKS5 and PROXY_TYPE_HTTP
        addr -        The address of the server (IP or DNS).
        port -        The port of the server. Defaults to 1080 for SOCKS
                       servers and 8080 for HTTP proxy servers.
        rdns -        Should DNS queries be performed on the remote side
                       (rather than the local side). The default is True.
                       Note: This has no effect with SOCKS4 servers.
        username -    Username to authenticate with to the server.
                       The default is no authentication.
        password -    Password to authenticate with to the server.
                       Only relevant when username is also provided.
        """
        self.proxy = (proxy_type, addr.encode(), port, rdns, 
                      username.encode() if username else None,
                      password.encode() if password else None)

    setproxy = set_proxy

    def get_proxy_sockname(self):
        """get_proxy_sockname() -> address info
        Returns the bound IP address and port number at the proxy.
        """
        return self.proxy_sockname

    getproxysockname = get_proxy_sockname

    def get_proxy_peername(self):
        """get_proxy_peername() -> address info
        Returns the IP and port number of the proxy.
        """
        return _orig_socket.getpeername(self)

    getproxypeername = get_proxy_peername

    def get_peername(self):
        """get_peername() -> address info
        Returns the IP address and port number of the destination
        machine (note: get_proxy_peername returns the proxy)
        """
        return self.proxy_peername

    getpeername = get_peername

    def _negotiate_SOCKS5(self, dest_addr, dest_port):
        """_negotiate_SOCKS5(self, dest_addr, dest_port)
        Negotiates a connection through a SOCKS5 server.
        """
        proxy_type, addr, port, rdns, username, password = self.proxy

        # First we'll send the authentication packages we support.
        if username and password:
            # The username/password details were supplied to the
            # set_proxy method so we support the USERNAME/PASSWORD
            # authentication (in addition to the standard none).
            self.sendall(b"\x05\x02\x00\x02")
        else:
            # No username/password were entered, therefore we
            # only support connections with no authentication.
            self.sendall(b"\x05\x01\x00")
        
        # We'll receive the server's response to determine which
        # method was selected
        chosen_auth = self.recvall(2)

        if chosen_auth[0:1] != b"\x05":
            # Note: string[i:i+1] is used because indexing of a bytestring 
            # via bytestring[i] yields an integer in Python 3
            self.close()
            raise GeneralProxyError("SOCKS5 proxy server sent invalid data")
        
        # Check the chosen authentication method
        
        if chosen_auth[1:2] == b"\x02":
            # Okay, we need to perform a basic username/password
            # authentication.
            self.sendall(b"\x01" + chr(len(username)).encode() + username + chr(len(password)).encode() + password)
            auth_status = self.recvall(2)
            if auth_status[0:1] != b"\x01":
                # Bad response
                self.close()
                raise GeneralProxyError("SOCKS5 proxy server sent invalid data")
            if auth_status[1:2] != b"\x00":
                # Authentication failed
                self.close()
                raise SOCKS5AuthError("SOCKS5 authentication failed")
            # Authentication succeeded

        # No authentication is required if 0x00 
        elif chosen_auth[1:2] != b"\x00":
            # Reaching here is always bad
            self.close()
            if chosen_auth[1:2] == b"\xFF":
                raise SOCKS5AuthError("All offered SOCKS5 authentication methods were rejected")
            else:
                raise GeneralProxyError("SOCKS5 proxy server sent invalid data")
        
        # Now we can request the actual connection
        req = b"\x05\x01\x00"
        # If the given destination address is an IP address, we'll
        # use the IPv4 address request even if remote resolving was specified.
        try:
            addr_bytes = socket.inet_aton(dest_addr)
            req += b"\x01" + addr_bytes
        except socket.error:
            # Well it's not an IP number, so it's probably a DNS name.
            if rdns:
                # Resolve remotely
                addr_bytes = None
                req += b"\x03" + chr(len(dest_addr)).encode() + dest_addr.encode()
            else:
                # Resolve locally
                addr_bytes = socket.inet_aton(socket.gethostbyname(dest_addr))
                req += b"\x01" + addr_bytes

        req += struct.pack(">H", dest_port)
        self.sendall(req)
        
        # Get the response
        resp = self.recvall(4)
        if resp[0:1] != b"\x05":
            self.close()
            raise GeneralProxyError("SOCKS5 proxy server sent invalid data")
        elif resp[1:2] != b"\x00":
            # Connection failed
            self.close()
            if ord(resp[1:2]) <= 8:
                raise SOCKS5Error("{:#04x}: {}".format(ord(resp[1:2]), SOCKS5errors[ord(resp[1:2])]))
            else:
                raise SOCKS5Error("Unknown error")
        
        # Get the bound address/port
        elif resp[3:4] == b"\x01":
            bound_addr = self.recvall(4)
        elif resp[3:4] == b"\x03":
            resp += self.recv(1)
            bound_addr = self.recvall(ord(resp[4:5]))
        else:
            self.close()
            raise GeneralProxyError("SOCKS5 proxy server sent invalid data")
        
        bound_port = struct.unpack(">H", self.recvall(2))[0]
        self.proxy_sockname = bound_addr, bound_port
        if addr_bytes:
            self.proxy_peername = socket.inet_ntoa(addr_bytes), dest_port
        else:
            self.proxy_peername = dest_addr, dest_port

    def _negotiate_SOCKS4(self, dest_addr, dest_port):
        """_negotiate_SOCKS4(self, dest_addr, dest_port)
        Negotiates a connection through a SOCKS4 server.
        """
        proxy_type, addr, port, rdns, username, password = self.proxy

        # Check if the destination address provided is an IP address
        remote_resolve = False
        try:
            addr_bytes = socket.inet_aton(dest_addr)
        except socket.error:
            # It's a DNS name. Check where it should be resolved.
            if rdns:
                addr_bytes = b"\x00\x00\x00\x01"
                remote_resolve = True
            else:
                addr_bytes = socket.inet_aton(socket.gethostbyname(dest_addr))
        
        # Construct the request packet
        req = struct.pack(">BBH", 0x04, 0x01, dest_port) + addr_bytes
        
        # The username parameter is considered userid for SOCKS4
        if username:
            req += username
        req += b"\x00"
        
        # DNS name if remote resolving is required
        # NOTE: This is actually an extension to the SOCKS4 protocol
        # called SOCKS4A and may not be supported in all cases.
        if remote_resolve:
            req += dest_addr.encode() + b"\x00"
        self.sendall(req)

        # Get the response from the server
        resp = self.recvall(8)
        if resp[0:1] != b"\x00":
            # Bad data
            self.close()
            raise GeneralProxyError("SOCKS4 proxy server sent invalid data")
        if resp[1:2] != b"\x5A":
            # Server returned an error
            self.close()
            if resp[1:2] in (b"\x5B", b"\x5C", b"\x5D"):
                self.close()
                raise SOCKS4Error("{:#04x}: {}".format(ord(resp[1:2]), SOCKS4errors[ord(resp[1:2])]))
            else:
                raise SOCKS4Error("Unknown error")
        
        # Get the bound address/port
        self.proxy_sockname = (socket.inet_ntoa(resp[4:]), struct.unpack(">H", resp[2:4])[0])
        if remote_resolve:
            self.proxy_peername = socket.inet_ntoa(addr_bytes), dest_port
        else:
            self.proxy_peername = dest_addr, dest_port

    def _negotiate_HTTP(self, dest_addr, dest_port):
        """_negotiate_HTTP(self, dest_addr, dest_port)
        Negotiates a connection through an HTTP server.
        NOTE: This currently only supports HTTP CONNECT-style proxies.
        """
        proxy_type, addr, port, rdns, username, password = self.proxy

        # If we need to resolve locally, we do this now
        addr = dest_addr if rdns else socket.gethostbyname(dest_addr)

        self.sendall(b"CONNECT " + addr.encode() + b":" + str(dest_port).encode() + 
                     b" HTTP/1.1\r\n" + b"Host: " + dest_addr.encode() + b"\r\n\r\n")
        
        resp = self.recv(4096)
        while b"\r\n\r\n" not in resp and b"\n\n" not in resp:
            d = self.recv(4096)
            if not d:
                raise GeneralProxyError("Connection closed unexpectedly")
            resp += d
            
       # We just need the first line to check if the connection was successful
        status_line = resp.splitlines()[0].split(b" ", 2)
        if status_line[0] not in (b"HTTP/1.0", b"HTTP/1.1"):
            self.close()
            raise GeneralProxyError("Proxy server does not appear to be an HTTP proxy")
        try:
            status_code = int(status_line[1])
        except ValueError:
            self.close()
            raise HTTPError("HTTP proxy server did not return a valid HTTP status")
        if status_code != 200:
            self.close()
            error = "{}: {}".format(status_code, status_line[2].decode())
            if status_code in (400, 403, 405):
                # It's likely that the HTTP proxy server does not support the CONNECT tunneling method
                error += "\n[*] Note: The HTTP proxy server may not be supported by PySocks"
            raise HTTPError(error)

        self.proxy_sockname = (b"0.0.0.0", 0)
        self.proxy_peername = addr, dest_port

    def connect(self, dest_pair):
        """connect(self, dest_pair)
        Connects to the specified destination through a proxy.
        dest_pair - A tuple of the IP/DNS address and the port number.
        Uses the same API as socket's connect().
        To select the proxy server, use set_proxy().
        """
        proxy_type, addr, port, rdns, username, password = self.proxy
        dest_addr, dest_port = dest_pair

        # Do a minimal input check first
        if (not isinstance(dest_pair, (list, tuple)) or len(dest_pair) != 2
            or not isinstance(dest_addr, type("")) or not isinstance(dest_port, int)):
            raise GeneralProxyError("Invalid destination-connection (address, port) pair")
        try:
            if proxy_type == PROXY_TYPE_SOCKS5:
                if port is not None:
                    port_num = port
                else:
                    port_num = 1080 # default SOCKS proxy port
                _orig_socket.connect(self, (addr, port_num))
                self._negotiate_SOCKS5(dest_addr, dest_port)
            elif proxy_type == PROXY_TYPE_SOCKS4:
                if port is not None:
                    port_num = port
                else:
                    port_num = 1080 # default SOCKS proxy port
                _orig_socket.connect(self, (addr, port_num))
                self._negotiate_SOCKS4(dest_addr, dest_port)
            elif proxy_type == PROXY_TYPE_HTTP:
                if port is not None:
                    port_num = port
                else:
                    port_num = 8080 # default HTTP proxy port
                _orig_socket.connect(self, (addr, port_num))
                self._negotiate_HTTP(dest_addr, dest_port)
            elif proxy_type is None:
                _orig_socket.connect(self, (dest_addr, dest_port))
            else:
                raise GeneralProxyError("Invalid proxy type")
        except socket.error as error:
            self.close()
            errno, msg = error.args
            msg = "Proxy connection error: {}".format(msg)
            raise socket.error(errno, msg)
