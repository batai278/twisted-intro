# This is the Twisted Get Poetry Now! client, version 4.1

import argparse, sys

from twisted.internet import defer
from twisted.internet.protocol import Protocol, ClientFactory

from twisted_intro.arg_parsing import parse_args

class PoetryClientTimeoutError(Exception):
    def __init__(self, address):
        self.message = "Connection with {} expired!".format(address)

    def __str__(self):
        return(repr(self.message))

class PoetryProtocol(Protocol):

    poem = ''
    timeoutSet = None

    def connectionMade(self):
        if self.factory.timeout is not None:
            from twisted.internet import reactor
            self.timeoutSet = reactor.callLater(self.factory.timeout, self.fireTimeout, PoetryClientTimeoutError(self.transport.getPeer()))

    def dataReceived(self, data):
        self.poem += data.decode()

    def connectionLost(self, reason):
        self.poemReceived(self.poem)

    def poemReceived(self, poem):
        self.factory.poem_finished(poem)

    def fireTimeout(self, exc_reason):
        self.factory.fireErrback(exc_reason)
        self.transport.loseConnection()


class PoetryClientFactory(ClientFactory):

    protocol = PoetryProtocol

    def __init__(self, deferred, timeout):
        self.deferred = deferred
        self.timeout = timeout

    def poem_finished(self, poem):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.callback(poem)

    def fireErrback(self, reason):
        if self.deferred is not None:
            d, self.deferred = self.deferred, None
            d.errback(reason)

    def clientConnectionFailed(self, connector, reason):
        self.fireErrback(reason)


def get_poetry(host, port, timeout):
    """
    Download a poem from the given host and port. This function
    returns a Deferred which will be fired with the complete text of
    the poem or a Failure if the poem could not be downloaded.
    """
    d = defer.Deferred()
    from twisted.internet import reactor
    factory = PoetryClientFactory(d, timeout)
    reactor.connectTCP(host, port, factory)
    return d


def poetry_main():
    addresses = parse_args()

    from twisted.internet import reactor

    poems = []
    errors = []
    timeouts = [40, 7 , None]

    def got_poem(poem, address):
        poems.append(poem)
        print('Success on downloading poem from {}'.format(address))

    def poem_failed(err, host, port):
        print(f'Error on {host}:{port}')
        print('Poem failed:', err)
        errors.append(err)

    def poem_done(_):
        if len(poems) + len(errors) == len(addresses):
            reactor.stop()

    for address, timeout in zip(addresses, timeouts):
        host, port = address
        d = get_poetry(host, port, timeout)
        d.addCallbacks(got_poem, poem_failed, callbackArgs=(address,), errbackArgs=(host, port,))
        d.addBoth(poem_done)

    reactor.run()

    for poem in poems:
        print(poem)


if __name__ == '__main__':
    poetry_main()
