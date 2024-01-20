import socket
import pyaudio
import threading

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK)

def receive_data():
    try:
        while True:
            data = client.recv(CHUNK)
            if not data:
                break
            stream.write(data)
    except ConnectionAbortedError:
        print("Connection aborted by the software in your host machine.")
    except Exception as e:
        print(f"Error receiving data: {e}")
    finally:
        print("Disconnected.")
        client.close()

print("Welcome to UDPVC\n")

ip = input("What is the server IP?:")
port = input("What is the server port?:")

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, int(port)))
    print("Connected!\n")
except ConnectionError as e:
    print(f"Failed to Connect! Error: {e}")
    exit(1)

receive_thread = threading.Thread(target=receive_data)
receive_thread.start()

try:
    while True:
        data = stream.read(CHUNK)
        client.send(data)
except KeyboardInterrupt:
    print("Exiting...")
finally:
    client.close()
    stream.stop_stream()
    stream.close()
    p.terminate()