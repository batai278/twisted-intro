# This is the Twisted Get Poetry Now! client, version 2.0.

# NOTE: This should not be used as the basis for production code.

import datetime, argparse
from arg_parsing import parse_args

from twisted.internet.protocol import Protocol, ClientFactory


class PoetryProtocol(Protocol):

    poem = ''
    task_num = 0

    def dataReceived(self, data):
        self.poem += data.decode()
        msg = 'Task %d: got %d bytes of poetry from %s'
        print(msg % (self.task_num, len(data), self.transport.getPeer()))

    def connectionLost(self, reason):
        self.poemReceived(self.poem)

    def poemReceived(self, poem):
        self.factory.poem_finished(self.task_num, poem)


class PoetryClientFactory(ClientFactory):

    task_num = 1

    # tell base class what proto to build
    # class variable
    # overrides: 
    #       protocol = None
    # in base Factory class
    protocol = PoetryProtocol

    def __init__(self, poetry_count):
        self.poetry_count = poetry_count
        self.poems = {} # task num -> poem

    def buildProtocol(self, address):
        proto = ClientFactory.buildProtocol(self, address)
        proto.task_num = self.task_num
        self.task_num += 1 # if called the first time reads task_num from class variable which is set to 1 for each new Factory
        return proto

    def poem_finished(self, task_num=None, poem=None):
        if task_num is not None:
            self.poems[task_num] = poem

        self.poetry_count -= 1

        if self.poetry_count == 0:
            self.report()
            from twisted.internet import reactor
            reactor.stop()

    def report(self):
        for i in self.poems:
            print ('Task {}: {} bytes of poetry'.format(i, len(self.poems[i])))

    def clientConnectionFailed(self, connector, reason):
        print('Failed to connect to:', connector.getDestination())
        self.poem_finished()


def poetry_main():
    addresses = parse_args()

    start = datetime.datetime.now()

    factory = PoetryClientFactory(len(addresses))

    from twisted.internet import reactor

    for address in addresses:
        host, port = address
        reactor.connectTCP(host, port, factory)

    reactor.run()

    elapsed = datetime.datetime.now() - start

    print('Got {} poems in {}'.format(len(addresses), elapsed))


if __name__ == '__main__':
    poetry_main()
