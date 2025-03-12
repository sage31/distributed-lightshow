import socket
import cv2
import numpy as np
import struct

def receive_video(client_socket):
    # Set the window to fullscreen mode
    cv2.namedWindow('Client Video', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Client Video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while True:
        data_size = struct.unpack("!I", client_socket.recv(4))[0]
        data = b''
        while len(data) < data_size:
            
            packet = client_socket.recv(max(data_size - len(data), 4096))
            if not packet:
                break
            data += packet
        frame = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if frame is not None:
            screen_width = 1920  # Set screen width (can fetch dynamically too)
            screen_height = 1200  # Set screen height (can fetch dynamically too)

            # Stretch the frame to fit the full screen
            frame_resized = cv2.resize(frame, (screen_width, screen_height), interpolation=cv2.INTER_LINEAR)

            cv2.imshow('Client Video', frame_resized)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()

# Client setup
def client_connect(master_ip, port=6000):
    position = input("Enter your position (x,y): ").split(',')
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((master_ip, port))
    client_socket.sendall(f"{position[0]},{position[1]}".encode())
    receive_video(client_socket)
    client_socket.close()

client_connect("x.x.x.x", 6000)
