import socket
import pyaudio
import threading
import keyboard  # Import the keyboard library

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=True, frames_per_buffer=CHUNK)

mute_flag = False  # Flag to track mute/unmute state

def receive_data():
    try:
        while True:
            data = client.recv(CHUNK)
            if not data:
                break
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
    mute_flag = not mute_flag
    print(f"Microphone {'MUTED' if mute_flag else 'UNMUTED'}")

print("Welcome to TCPVC\n")

ip = input("What is the server IP?:")
port = input("What is the server port?:")

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((ip, int(port)))
    print("Connected!\n")
    print("You can press CTRL + M to toggle mute!\n")
except ConnectionError as e:
    print(f"Failed to Connect! Error: {e}")
    exit(1)

receive_thread = threading.Thread(target=receive_data)
receive_thread.start()

keyboard.add_hotkey('ctrl+m', toggle_mute)  # Register CTRL + M to toggle mute/unmute

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