import socket, select, errno, sys, time
from arg_parsing import parse_args, parse_blocking_server_args

READ_SOCK = [] # Server socket listening on 'host:port' for incoming clients connection
WRITE_SOCKS = [] # Client sockets returned by sock.accept() on READ_SOCK currently connected for obtaining poetry
POETRY_DESCRIPTORS = {} # Open descriptors for each 'client' socket: pairs sock:descr
NUM_BYTES = 10
DELAY = 3.5

def serve(listen_socket, poetry):
    while True:
        try:
            accept_ready, send_ready, _ = select.select(READ_SOCK, WRITE_SOCKS, [])
        except select.error as sel_err:
            break
        except socket.error as sock_err:
            break
        except KeyboardInterrupt as key_int_err:
            print('Keyboard Interruption')
            sys.exit(0)
            break

        # Accept new client connections, open poetry file for it and keep track of them
        for server in accept_ready:
            client_sock, client_addr = server.accept()
            client_sock.setblocking(0)
            print(f"Accepted new connection on {client_addr}")
            WRITE_SOCKS.append(client_sock)

            client_poetry_descr = open(poetry)
            POETRY_DESCRIPTORS[client_sock] = client_poetry_descr
        # For each client ready to accept new chunks of poetry send latter
        for client_ready_sock in send_ready:
            try:
                send_to_client(client_ready_sock)
            except Exception as err:
                print(err)
                #raise

def send_to_client(sock):

    send_bytes = POETRY_DESCRIPTORS[sock].read(NUM_BYTES)

    if not send_bytes: # no more poetry :(
        finish_sending(sock)
        return

    print(f'Sending {len(send_bytes)} bytes to {sock.getpeername()}')

    try:
        sock.send(send_bytes.encode())
    except socket.error as send_err:
        if send_err.args[0] == errno.EWOULDBLOCK:
            return
        else:
            finish_sending(sock)
            raise
    except ConnectionAbortedError as broken_connection_err:
        finish_sending(sock)
        return

    time.sleep(DELAY)

def finish_sending(sock):
    print(f'Closing connection with {sock.getpeername()}')

    POETRY_DESCRIPTORS[sock].close() # close descriptor
    del POETRY_DESCRIPTORS[sock] # forget about that descriptor

    WRITE_SOCKS.remove(sock) # select(): forget about socket, connection broke
    sock.close() # close 'client' socket with broken connection

def main():
    options, poetry_filename = parse_blocking_server_args()
    NUM_BYTES = options.num_bytes
    DELAY = options.delay

    SERVER_ADDRESS = (options.iface, options.port or 0)

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(SERVER_ADDRESS)
    server_sock.listen(5)
    READ_SOCK.append(server_sock) # Add to list for passing as select 1-st argument

    print(f"""Serving {poetry_filename} on {':'.join([options.iface, str(options.port)])}""")

    serve(server_sock, poetry_filename)

if __name__ == '__main__':
    main()