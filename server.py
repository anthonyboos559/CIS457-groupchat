import socket
from threading import Thread, Lock

connections_lock = Lock()
connections = {}

def send_message(sender_id, message):
    with connections_lock:
        for connection_id, socket in connections.items():
            if sender_id == connection_id:
                continue
            else:
                socket.write(message)
                socket.flush()

def handle_client(id, io_sock, connection_sock: socket.socket):
    while True:
        print(f"Waiting for messages from client {id}")
        try:
            message = io_sock.readline()
            print(f"Client {id} sent: {message}")
            if message == "\n":
                send_message(id, f"User {id} has left the chat\n")
                with connections_lock:
                    connections.pop(id)
                    io_sock.write("connection closed\n")
                    io_sock.flush()
                    connection_sock.close()
                    print(f"Client {id} socket closed")
                    break
            else:
                send_message(id, message)
        except ConnectionResetError:
            send_message(id, f"User {id} has left the chat\n")
            with connections_lock:
                connections.pop(id)
                connection_sock.close()
                print(f"Client {id} socket closed")
                break

def main():

    server_socket = socket.create_server(("localhost", 5000))
    client_id = 0

    while True:
        connection_socket, _ = server_socket.accept()

        with connections_lock:
            client_id += 1
            print(f"Client {client_id} connected on {connection_socket}!")
            io_socket = connection_socket.makefile("rw", encoding="utf-8")
            connections.update({client_id: io_socket})

            t = Thread(target = handle_client, args=(client_id, io_socket, connection_socket,))
            t.start()

    server_socket.close()

if __name__ == '__main__':
    main()