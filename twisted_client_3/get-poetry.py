# This is the Twisted Get Poetry Now! client, version 3.0.

# NOTE: This should not be used as the basis for production code.
import sys
import datetime, argparse
from arg_parsing import parse_args

from twisted.internet.protocol import Protocol, ClientFactory

class PoetryProtocol(Protocol):

    poem = ''

    def dataReceived(self, data):
        self.poem += data.decode()

    def connectionLost(self, reason):
        self.poemReceived(self.poem)

    def poemReceived(self, poem):
        self.factory.poem_finished(poem)


class PoetryClientFactory(ClientFactory):

    protocol = PoetryProtocol

    def __init__(self, callback):
        self.callback = callback

    def poem_finished(self, poem):
        self.callback(poem)


def get_poetry(host, port, callback):
    """
    Download a poem from the given host and port and invoke

      callback(poem)

    when the poem is complete.
    """
    from twisted.internet import reactor
    factory = PoetryClientFactory(callback)
    reactor.connectTCP(host, port, factory)


def poetry_main():
    try:
        addresses = parse_args()
    except:
        print("Provide valid arguments.")
        sys.exit()

    from twisted.internet import reactor

    poems = []

    def got_poem(poem):
        poems.append(poem)
        if len(poems) == len(addresses):
            reactor.stop()

    for address in addresses:
        host, port = address
        get_poetry(host, port, got_poem)

    reactor.run()

    for poem in poems:
        print(poem)


if __name__ == '__main__':
    poetry_main()
