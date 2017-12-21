# This is the blocking version of the Slow Poetry Server.

import argparse, os, socket, time


def parse_args():
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
    parser.add_argument('--num-bytes', type=int, help=help, default=10)

    parser.add_argument('poetry_file')

    args = parser.parse_args()
   
    if 'poetry_file' not in vars(args).keys():
        parser.error('Provide poetry file.')

    poetry_file = args.poetry_file
    if not os.path.exists(poetry_file):
        parser.error('No such file: %s' % poetry_file)

    return args, poetry_file


def send_poetry(sock, poetry_file, num_bytes, delay):
    """Send some poetry slowly down the socket."""

    inputf = open(poetry_file)

    while True:
        send_bytes = inputf.read(num_bytes)

        if not send_bytes: # no more poetry :(
            sock.close()
            inputf.close()
            return

        print (f'Sending {len(send_bytes)} bytes') 

        try:
            sock.sendall(send_bytes) # this is a blocking call
        except socket.error:
            sock.close()
            inputf.close()
            return

        time.sleep(delay)


def serve(listen_socket, poetry_file, num_bytes, delay):
    while True:
        sock, addr = listen_socket.accept()
        print (f'Somebody at {addr} wants poetry!')

        send_poetry(sock, poetry_file, num_bytes, delay)


def main():
    options, poetry_file= parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((options.iface, options.port or 0))

    sock.listen(5)

    print ('Serving {} on port {}.'.format(poetry_file, sock.getsockname()[1]))
    print('Trying to accept connection')
    serve(sock, poetry_file, options.num_bytes, options.delay)


if __name__ == '__main__':
    main()
