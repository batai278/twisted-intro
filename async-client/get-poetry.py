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
    parser.add_argument('adresses', metavar='N', nargs='+', help=help)
        
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

    if 'adresses' not in vars(args).keys():
        print('Provide at least one adress.')
        return
    
    return(list(map(parse_address, args.addresses)))


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
    parser.add_argument('adresses', metavar='N', nargs='+', help=help)
        
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
            host, port = addr.split(':')

        if not port.isdigit():
            print('Ports must be integers.')
            return

        return((host, int(port)))

    if "adresses" not in vars(args).keys():
        print('Provide at least one adress.')
        return
    
    return(map(parse_address, args.adresses))


def connect(address):
    """Connect to the given server and return a non-blocking socket."""

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(address)
    sock.setblocking(0)
    return(sock)


def format_address(address):
    host, port = address
    return(f"""{(host or '127.0.0.1')} : {port}""")


def main():
    addresses = parse_args()

    start = datetime.datetime.now()

    sockets = map(connect, addresses)

    poems = get_poetry(sockets)

    elapsed = datetime.datetime.now() - start

    for i, sock in enumerate(sockets):
        print(f'Task {i + 1} : {len(poems[sock])} bytes of poetry')

    print(f'Got {len(addresses)} poems in elapsed')


if __name__ == '__main__':
    main()
