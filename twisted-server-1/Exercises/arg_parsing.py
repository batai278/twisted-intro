import argparse
import os

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

def parse_twisted_server_args():
    usage = """usage: %prog [options] poetry-file

    This is the Fast Poetry Server, Twisted edition.
    Run it like this:

      python fastpoetry.py <path-to-poetry-file>

    If you are in the base directory of the twisted-intro package,
    you could run it like this:

      python twisted-server-1/fastpoetry.py poetry/ecstasy.txt

    to serve up John Donne's Ecstasy, which I know you want to do.
    """

    parser = argparse.ArgumentParser(usage)

    help = "The port to listen on. Default to a random available port."
    parser.add_argument('--port', type=int, help=help)

    help = "The interface to listen on. Default is localhost."
    parser.add_argument('--iface', help=help, default='localhost')

    help = "Poetry file to serve."
    parser.add_argument('poetry', help=help)

    args = parser.parse_args()

    if 'poetry' not in vars(args).keys():
        parser.error('Provide exactly one poetry file.')

    poetry_file = args.poetry

    if not os.path.exists(args.poetry):
        parser.error('No such file: %s' % poetry_file)

    return args, args.poetry

def parse_blocking_server_args(args=None):
    usage = """usage: %prog [options] poetry-file

    This is the Slow Poetry Server, blocking edition.
    Run it like this:

      python slowpoetry.py <path-to-poetry-file>

    If you are in the base directory of the twisted-intro package,
    you could run it like this:

      python blocking-server/slowpoetry.py poetry/ecstasy.txt

    to serve up John Donne's Ecstasy, which I know you want to do.
    """

    parser = argparse.ArgumentParser(usage)

    help = "The port to listen on. Default to a random available port."
    parser.add_argument('--port', type=int, help=help)

    help = "The interface (host) to listen on. Default is localhost."
    parser.add_argument('--iface', help=help, default='localhost')

    help = "The number of seconds between sending bytes."
    parser.add_argument('--delay', type=float, help=help, default=.7)

    help = "The number of bytes to send at a time."
    parser.add_argument('--num_bytes', type=int, help=help, default=10)

    parser.add_argument('poetry_file')
    if args is not None:
        args = parser.parse_args(args)
    else:
        args = parser.parse_args()

    if 'poetry_file' not in vars(args).keys():
        parser.error('Provide poetry file.')

    poetry_file = args.poetry_file
    if not os.path.exists(poetry_file):
        parser.error('No such file: %s' % poetry_file)

    return args, poetry_file