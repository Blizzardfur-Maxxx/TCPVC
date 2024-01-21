import socket
import threading
import pyaudio
from concurrent.futures import ThreadPoolExecutor
import sys

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

clients = set()
clients_lock = threading.Lock()
client_buffers = {}  # Dictionary to store individual client buffers

def handle_client(client_socket):
    with clients_lock:
        clients.add(client_socket)
        client_buffers[client_socket] = bytearray()  # Initialize individual buffer
    
    try:
        while True:
            data = client_socket.recv(CHUNK)
            if not data:
                break
            with clients_lock:
                client_buffers[client_socket].extend(data)
            broadcast(client_socket)
    except ConnectionResetError:
        print(f"Connection reset by the remote host.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        with clients_lock:
            clients.remove(client_socket)
            del client_buffers[client_socket]  # Remove client buffer
        print(f"Client {client_socket.getpeername()} disconnected.")
        client_socket.close()

def broadcast(sender_socket):
    with clients_lock:
        for client in clients.copy():
            if client != sender_socket:
                try:
                    data = client_buffers[client][:CHUNK]
                    client_buffers[client] = client_buffers[client][CHUNK:]
                    client.send(data)
                except Exception as e:
                    print(f"Error broadcasting to client: {e}")
                    clients.remove(client)
                    del client_buffers[client]

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    print("Listening for Clients...\n")

    with ThreadPoolExecutor(max_workers=10) as executor:
        try:
            while True:
                client, addr = server.accept()
                print(f"Accepted connection from {addr}")
                executor.submit(handle_client, client)
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            server.close()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        port = input("What will be the server port?: ")

    try:
        start_server(port)
    except OSError as e:
        if e.errno == 10048:
            print(f"Port {port} is already in use. Please choose a different port.")
        else:
            print(f"Error binding to port: {e}")