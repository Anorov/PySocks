#!/usr/bin/env python
from twisted.internet import reactor
from twisted.protocols.socks import SOCKSv4Factory

def run_proxy(port):
    print('Starting SOCKS proxy on port %s' % port)
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
    print("Running SOCKS4 proxy server")
    run_proxy(7778)
