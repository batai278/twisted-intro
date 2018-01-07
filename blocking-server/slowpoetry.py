# This is the blocking version of the Slow Poetry Server.

import os, socket, time


from twisted_intro.arg_parsing import parse_blocking_server_args

def send_poetry(sock, poetry_file, num_bytes, delay):
    """Send some poetry slowly down the socket."""

    inputf = open(poetry_file)

    while True:
        send_bytes = inputf.read(num_bytes)
        print(send_bytes)

        if not send_bytes: # no more poetry :(
            sock.close()
            inputf.close()
            return

        print(f'Sending {len(send_bytes)} bytes')

        try:
            sock.sendall(send_bytes.encode()) # this is a blocking call
        except (socket.error, ConnectionAbortedError) as e:
            sock.close()
            inputf.close()
            return

        time.sleep(delay)


def serve(listen_socket, poetry_file, num_bytes, delay):
    while True:
        sock, addr = listen_socket.accept()
        print (f'Somebody at {addr} wants poetry!')

        send_poetry(sock, poetry_file, num_bytes, delay)


def main(args=None):
    if args is not None:
        options, poetry_file = parse_blocking_server_args(args)
    else:
        options, poetry_file = parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((options.iface, options.port or 0))

    sock.listen(5)

    print ('Serving {} on port {}.'.format(poetry_file, sock.getsockname()[1]))
    print('Trying to accept connection')
    serve(sock, poetry_file, options.num_bytes, options.delay)


if __name__ == '__main__':
    main()
