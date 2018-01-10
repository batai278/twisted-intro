# This is the Twisted Poetry Transform Server, version 1.0

import arg_parsing

from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import NetstringReceiver


class TransformService(object):

    @staticmethod
    def cummingsify(poem):
        return poem.lower()


class TransformProtocol(NetstringReceiver):

    def stringReceived(self, request):
        if '.' not in request: # bad request
            self.transport.loseConnection()
            return

        xform_name, poem = request.split('.', 1)

        self.xform_request_received(xform_name, poem)

    def xform_request_received(self, xform_name, poem):
        new_poem = self.factory.transform(xform_name, poem)

        if new_poem is not None:
            self.sendString(new_poem)

        self.transport.loseConnection()


class TransformFactory(ServerFactory):

    protocol = TransformProtocol

    def __init__(self, service):
        self.service = service

    def transform(xform_name, poem):
        thunk = getattr(self, 'xform_{}'.format(xform_name), None)

        if thunk is None: # no such transform
            return None

        try:
            return thunk(poem)
        except:
            return None # transform failed

    def xform_cummingsify(self, poem):
        return self.service.cummingsify(poem)


def main():
    options = arg_parsing.parse_twisted_server_args()

    service = TransformService()

    factory = TransformFactory(service)

    from twisted.internet import reactor

    port = reactor.listenTCP(options.port or 0,
                             factory,
                             interface=options.iface
                             )

    print(f'Serving transforms on {port.getHost()}')

    reactor.run()


if __name__ == '__main__':
    main()
