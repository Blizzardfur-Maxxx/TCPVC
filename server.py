import socket
import threading
import pyaudio

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

clients = []
clients_lock = threading.Lock()

def handle_client(client_socket):
    try:
        while True:
            data = client_socket.recv(CHUNK)
            if not data:
                break
            broadcast(data, client_socket)
    except ConnectionResetError:
        print(f"Connection reset by the remote host.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        with clients_lock:
            clients.remove(client_socket)
        print(f"Client {client_socket.getpeername()} disconnected.")
        client_socket.close()

def broadcast(data, sender_socket):
    with clients_lock:
        for client in clients:
            if client != sender_socket:
                try:
                    client.send(data)
                except Exception as e:
                    print(f"Error broadcasting to client: {e}")
                    clients.remove(client)

print("Welcome to TCPVC Server\n")

while True:
    port = input("What will be the server port?:")

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', int(port)))
        server.listen(5)
        print("Listening for Clients...\n")
        break  # Break out of the loop if port binding is successful
    except OSError as e:
        if e.errno == 10048:
            print(f"Port {port} is already in use. Please choose a different port.")
        else:
            print(f"Error binding to port: {e}")

while True:
    client, addr = server.accept()
    print(f"Accepted connection from {addr}")
    with clients_lock:
        clients.append(client)

    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()