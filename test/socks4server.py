#!/usr/bin/env python
from twisted.internet import reactor
from twisted.protocols.socks import SOCKSv4Factory
import sys


def run_proxy(port):
    print('Starting SOCKS4 proxy on port %s' % port)
    reactor.listenTCP(port, SOCKSv4Factory("/dev/null"), interface="127.0.0.1")
    try:
        reactor.run()
    except (KeyboardInterrupt, SystemExit):
        print('stop socks proxy')
        reactor.stop()
    except Exception as ex:
        logging.error('', exc_info=ex)
        raise


if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
    except IndexError, ValueError:
        print('Usage: socks4server <port>')
    else:
        run_proxy(port)
