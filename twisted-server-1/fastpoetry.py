# This is the Twisted Fast Poetry Server, version 1.0

from twisted.internet.protocol import ServerFactory, Protocol

from twisted_intro.arg_parsing import parse_twisted_server_args

class PoetryProtocol(Protocol):

    def connectionMade(self):
        self.transport.write(self.factory.poem)
        self.transport.loseConnection()


class PoetryFactory(ServerFactory):

    protocol = PoetryProtocol

    def __init__(self, poem):
        self.poem = poem


def main():
    options, poetry_file = parse_twisted_server_args()

    poem = open(poetry_file).read()

    factory = PoetryFactory(poem)

    from twisted.internet import reactor

    port = reactor.listenTCP(options.port or 0, factory,
                             interface=options.iface)

    print('Serving %s on %s.' % (poetry_file, port.getHost()))

    reactor.run()


if __name__ == '__main__':
    main()
