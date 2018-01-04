# This is the Twisted Get Poetry Now! client, version 3.2
# Timeout handling added - Exercise 1 (Pt. 6)

# NOTE: This should not be used as the basis for production code.

import argparse, sys
from arg_parsing import parse_args
from twisted.internet.protocol import Protocol, ClientFactory
import twisted.python.failure
from twisted.python.failure import Failure

class PoetryClientTimeoutError(Exception):
    def __init__(self, address):
        self.message = "Connection with {} expired!".format(address)

    def __str__(self):
        return(repr(self.message))

class PoetryProtocol(Protocol):

    poem = ''
    timeoutSet = None

    def connectionMade(self):
        from twisted.internet import reactor
        if self.factory.connectionTimeout is not None:
            self.timeoutSet = reactor.callLater(self.factory.connectionTimeout, self.fireTimeout, Failure(PoetryClientTimeoutError(self.transport.getPeer())))

    def dataReceived(self, data):
        self.poem += data.decode()

    def connectionLost(self, reason):
        if self.timeoutSet is None:
            self.poemReceived(self.poem, self.transport.getPeer())
        elif self.timeoutSet.active():
            self.timeoutSet.cancel()
            self.poemReceived(self.poem, self.transport.getPeer())

    def poemReceived(self, poem, address):
        self.factory.poem_finished(poem, address)

    def fireTimeout(self, reason):
        self.factory.errback(reason)
        self.transport.loseConnection()

class PoetryClientFactory(ClientFactory):

    protocol = PoetryProtocol

    def __init__(self, callback, errback, connectionTimeout=None):
        self.callback = callback
        self.errback = errback
        self.connectionTimeout = connectionTimeout

    def poem_finished(self, poem, address):
        self.callback(poem, address)

    def clientConnectionFailed(self, connector, reason):
        self.errback(reason)


def get_poetry(host, port, callback, errback, connectionTimeout=None):
    """
    Download a poem from the given host and port and invoke

      callback(poem)

    when the poem is complete. If there is a failure, invoke:

      errback(err)

    instead, where err is a twisted.python.failure.Failure instance.
    """
    from twisted.internet import reactor
    factory = PoetryClientFactory(callback, errback, connectionTimeout=connectionTimeout)
    reactor.connectTCP(host, port, factory)


def poetry_main():
    addresses = parse_args()

    from twisted.internet import reactor

    poems = []
    errors = []
    timeouts = [40, 7, None]

    def got_poem(poem, address):
        poems.append(poem)
        print('Success on downloading poem from {}'.format(address))
        poem_done()

    def poem_failed(err):
        #stdo = sys.stdout
        #sys.stdout = sys.stderr
        print('Poem failed:', err)
        #sys.stdout = stdo
        errors.append(err)
        poem_done()

    def poem_done():
        if len(poems) + len(errors) == len(addresses):
            reactor.stop()

    for address, timeout in zip(addresses, timeouts):
        host, port = address
        get_poetry(host, port, got_poem, poem_failed, connectionTimeout = timeout)

    reactor.run()

    for poem in poems:
        print(poem)


if __name__ == '__main__':
    poetry_main()
