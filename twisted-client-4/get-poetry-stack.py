# This is the Twisted Get Poetry Now! client, version 4.0, with stacktrace.

import argparse, os, sys, traceback

from twisted.internet import defer
from twisted.internet.protocol import Protocol, ClientFactory
from arg_parsing import parse_args


class PoetryProtocol(Protocol):

    poem = ''

    def dataReceived(self, data):
        self.poem += data

    def connectionLost(self, reason):
        self.poemReceived(self.poem)

    def poemReceived(self, poem):
        self.factory.poem_finished(poem)


class PoetryClientFactory(ClientFactory):

    protocol = PoetryProtocol

    def __init__(self, deferred, timeout):
        self.deferred = deferred
        self.timeout = timeout

    def poem_finished(self, poem):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback(poem)

    def clientConnectionFailed(self, connector, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)


def get_poetry(host, port):
    """
    Download a poem from the given host and port. This function
    returns a Deferred which will be fired with the complete text of
    the poem or a Failure if the poem could not be downloaded.
    """
    d = defer.Deferred()
    from twisted.internet import reactor
    factory = PoetryClientFactory(d)
    reactor.connectTCP(host, port, factory)
    return d


def poetry_main():
    addresses = parse_args()

    from twisted.internet import reactor

    poems = []
    errors = []

    def got_poem(poem):
        traceback.print_stack()
        os._exit(0)

    def poem_failed(err):
        print >>sys.stderr, 'Poem failed:', err
        errors.append(err)

    def poem_done(_):
        if len(poems) + len(errors) == len(addresses):
            reactor.stop()

    for address in addresses:
        host, port = address
        d = get_poetry(host, port)
        d.addCallbacks(got_poem, poem_failed)
        d.addBoth(poem_done)

    reactor.run()

    for poem in poems:
        print poem


if __name__ == '__main__':
    poetry_main()
