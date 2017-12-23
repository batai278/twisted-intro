# This is the asynchronous Get Poetry Now! client.

import datetime, errno, argparse, select, socket


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
        print(parser.format_help())

    def parse_address(addr):
        if ':' not in addr:
            host = '127.0.0.1'
            port = addr
        else:
            host, port = addr.split(':', 1)

        if not port.isdigit():
            parser.error('Ports must be integers.')

        return host, int(port)

    if 'addresses' not in vars(args).keys():
        print('Provide at least one address.')
        return

    return(list(map(parse_address, args.addresses)))


def connect(address):
    """Connect to the given server and return a non-blocking socket."""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    sock.setblocking(0)
    return(sock)


def get_poetry(sockets):
    """Download poety from all the given sockets."""

    poems = dict.fromkeys(sockets, '') # socket -> accumulated poem

    # socket -> task numbers
    sock2task = dict([(s, i + 1) for i, s in enumerate(sockets)])

    sockets = list(sockets) # make a copy

    # we go around this loop until we've gotten all the poetry
    # from all the sockets. This is the 'reactor loop'.
    print(sockets)
    while sockets: # TO DO: check out why the client doesn`t even reaches here
        # this select call blocks until one or more of the
        # sockets is ready for read I/O
        rlist, _, _ = select.select(sockets, [], [])
        print(rlist)
        # rlist is the list of sockets with data ready to read

        for sock in rlist:
            data = ''

            while True:
                try:
                    new_data = sock.recv(1024)
                except socket.error as err:
                    if err.args[0] == errno.EWOULDBLOCK:
                        # this error code means we would have
                        # blocked if the socket was blocking.
                        # instead we skip to the next socket
                        break
                    raise
                else:
                    if not new_data:
                        break
                    else:
                        print(new_data.decode())
                        data += new_data.decode()

            # Each execution of this inner loop corresponds to
            # working on one asynchronous task in Figure 3 here:
            # http://krondo.com/?p=1209#figure3

            task_num = sock2task[sock]

            if not data:
                sockets.remove(sock)
                sock.close()
                print (f'Task {task_num} finished')
            else:
                addr_fmt = format_address(sock.getpeername())
                msg = f'Task {task_num}: got {len(data)} bytes of poetry from {addr_fmt}'
                print(msg)

            poems[sock] += data

    return(poems)


def format_address(address):
    host, port = address
    return(f"""{(host or '127.0.0.1')} : {port}""")


def main(args=None):

    if args is not None:
        addresses = parse_args(args)
    else:
        addresses = parse_args()

    start = datetime.datetime.now()

    sockets = list(map(connect, addresses))
    poems = get_poetry(sockets)
    #print(poems)

    elapsed = datetime.datetime.now() - start

    for i, sock in enumerate(sockets):
        print(f'Task {i + 1} : {len(poems[sock])} bytes of poetry')

    print(f'Got {len(addresses)} poems in {elapsed}')


if __name__ == '__main__':
    main(['10653'])
