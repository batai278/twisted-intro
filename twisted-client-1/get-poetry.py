# This is the Twisted Get Poetry Now! client, version 1.0.

# NOTE: This should not be used as the basis for production code.
# It uses low-level Twisted APIs as a learning exercise.

import datetime, errno, argparse, socket

from twisted.internet import main


def parse_args(args=None):
    usage = """usage: %prog [options] [hostname]:port ...

    This is the Get Poetry Now! client, asynchronous edition.
    Run it like this:

      python get-poetry.py port1 port2 port3 ...

    If you are in the base directory of the twisted-intro package,
    you could run it like this:

      python async-client/get-poetry.py 10001 10002 10003

    to grab poetry from servers on ports 10001, 10002, and 10003.

    Of course, there need to be servers listening on those ports
    for that to work.
    """

    parser = argparse.ArgumentParser(usage)

    help = 'Adresses of servers providing poetry.'
    parser.add_argument('addresses', metavar='N', nargs='+', help=help)

    try:
        if args is not None:
            args = parser.parse_args(args)
        else:
            args = parser.parse_args()
    except:
        parser.format_help()

    def parse_address(addr):
        if ':' not in addr:
            host = '127.0.0.1'
            port = addr
        else:
            host, port = addr.split(':')

        if not port.isdigit():
            raise ValueError('Ports must be integers.')

        return host, int(port)

    if 'addresses' not in vars(args).keys():
        print('Provide at least one address.')
        return

    return(list(map(parse_address, args.addresses)))


class PoetrySocket(object):

    def __init__(self, task_num, address):
        self.poem = ''
        self.task_num = task_num
        self.address = address
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(address)
        self.sock.setblocking(0)

        # tell the Twisted reactor to monitor this socket for reading
        from twisted.internet import reactor
        reactor.addReader(self)

    def fileno(self):
        try:
            return self.sock.fileno()
        except socket.error:
            return -1

    def connectionLost(self, reason):
        self.sock.close()

        # stop monitoring this socket
        from twisted.internet import reactor
        reactor.removeReader(self)

        # see if there are any poetry sockets left
        for reader in reactor.getReaders():
            if isinstance(reader, PoetrySocket):
                return

        reactor.stop() # no more poetry

    def doRead(self):
        """
            Once there is data staying on the buffer to read (no matter the data is fresh or stale),
            the reactor will call our doRead function until it consumes the entire buffer.
            Notes:
                1. the ‘stale data’ here, I mean,
                is the data in the buffer which is not yet touched by the receiver
                because receiving speed is less than the sending speed from server.
                2. If we get while loop removed from the doRead function,
                the guarantee of consuming data in ‘read buffer’ is relied on reactor.
        """
        bytes = ''

        # just read as much as you can (all "ready" bytes from a buffer)
        while True:
            try:
                # at the first iteration always pass due to inner select() call inside the reactor,
                # which guarantees that some data already came to buffer and socket is ready to read operation
                # 1024 - upper limit for a chunk of data to be read, it ensures that we are not trying to read to much,
                # causing other sockets "starve"
                bytesread = self.sock.recv(1024)
                # just read as much as you can (all "ready" bytes from a buffer)
                # will kick out of the cycle and stop reading data when there is nothing left in the buffer
                # but while loop ensures we consumed all available data from current portion
                if not bytesread:
                    break
                else:
                    bytes += bytesread.decode()
            except socket.error as e:
                # Initially all sockets are in blocking mode.
                # In non-blocking mode, if a recv() CALL DOESN’T FIND ANY DATA,
                # or if a send() call can’t immediately dispose of the data,
                # AN ERROR EXCEPTION IS RAISED.
                # The error exception it's referring to is errno.EWOULDBLOCK.
                # For this to happen, the socket object must be set to non-blocking mode
                # IT`S MESSAGE IS:
                #   IN:
                #       import os
                #       os.strerror(errno.EWOULDBLOCK)
                #   OUT:
                #       'Resource temporarily unavailable'

                if e.args[0] == errno.EWOULDBLOCK:
                    break
                # If Exception is not EWOULDBLOCK we assume that connection is lost
                # and return a FAILURE object according to IReadDescriptor interface specification.
                return main.CONNECTION_LOST

        # We reach right here only when some data was recieved or we were cicked out of the cycle
        # at first iteration or socket couldn`t read the data and since select() guarantees that some data is present
        # it only could mean that we consumed everything server can propose, so the task is finished
        # and we send CONNECTION_DONE (Failure object redirected to self.connectionLost as reason parameter)
        if not bytes:
            print (f'Task {self.task_num} finished')
            return(main.CONNECTION_DONE)
        else:
            msg = f'Task {self.task_num}: got {len(bytes)} bytes of poetry from {self.format_addr()}'
            print(msg)

        self.poem += bytes

    def logPrefix(self):
        return('poetry')

    def format_addr(self):
        host, port = self.address
        return("""{host or '127.0.0.1'}:{port}""")


def poetry_main():
    addresses = parse_args()

    start = datetime.datetime.now()

    sockets = [PoetrySocket(i + 1, addr) for i, addr in enumerate(addresses)]

    from twisted.internet import reactor
    reactor.run()

    elapsed = datetime.datetime.now() - start

    for i, sock in enumerate(sockets):
        print('Task {}: {} bytes of poetry'.format(i + 1, len(sock.poem)))

    print('Got {} poems in {}'.format(len(addresses), elapsed))


if __name__ == '__main__':
    poetry_main()
