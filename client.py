import socket
import pyaudio
import threading
import keyboard
import sys

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK)

mute_flag = False
mute_lock = threading.Lock()

def receive_data():
    try:
        while True:
            data = client.recv(CHUNK)
            if not data:
                break
            with mute_lock:
                if not mute_flag:
                    stream.write(data)
    except ConnectionAbortedError:
        print("Connection aborted by the software in your host machine.")
    except Exception as e:
        print(f"Error receiving data: {e}")
    finally:
        print("Disconnected.")
        client.close()

def toggle_mute():
    global mute_flag
    with mute_lock:
        mute_flag = not mute_flag
    print(f"Microphone {'MUTED' if mute_flag else 'UNMUTED'}")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        ip = sys.argv[1]
        port = int(sys.argv[2])
    else:
        print("Welcome to TCPVC!\n")
        ip = input("What is the server IP?: ")
        port = int(input("What is the server port?: "))

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((ip, port))  # Connect to the correct IP and port
        print("Connected!\n")
        print("You can press CTRL + M to toggle mute!\n")
    except ConnectionError as e:
        print(f"Failed to Connect! Error: {e}")
        exit(1)

    receive_thread = threading.Thread(target=receive_data)
    receive_thread.start()

    keyboard.add_hotkey('ctrl+m', toggle_mute)

    try:
        while True:
            data = stream.read(CHUNK)
            if not mute_flag:
                client.send(data)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        client.close()
        stream.stop_stream()
        stream.close()
        p.terminate()
