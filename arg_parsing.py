import argparse

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