import socket
import cv2
import numpy as np
import time
import struct

# Split video into grid segments
def split_video(video_path, grid_size):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception("Error opening video")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    grid_w, grid_h = grid_size
    
    segment_width = width // grid_w
    segment_height = height // grid_h
    
    return cap, segment_width, segment_height, fps

# Sending video frames to clients
def stream_video_to_clients(video_path, clients, grid_size, start_time):
    cap, seg_w, seg_h, fps = split_video(video_path, grid_size)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        for (client_socket, (x, y)) in clients.items():
            sub_frame =     frame[y * seg_h:(y+1) * seg_h, x * seg_w:(x+1) * seg_w]
            # cv2.imshow('Master Video', sub_frame)
            _, buffer = cv2.imencode('.png', sub_frame)
            data = buffer.tobytes()
            client_socket.sendall(struct.pack("!I", len(data)) + data)
        
        time.sleep(1 / fps)
    cap.release()

# Server setup
def start_main_node(video_path, grid_size, start_time, port=6000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("", port))
    server.listen()
    clients = {}
    print("Master waiting for clients...")
    
    while len(clients) < (grid_size[0] * grid_size[1]):
        client_socket, addr = server.accept()
        x, y = map(int, client_socket.recv(1024).decode().split(','))
        clients[client_socket] = (x, y)
        print(f"Client {addr} assigned to {x},{y}")
    
    input("Press Enter to start streaming...")
    stream_video_to_clients(video_path, clients, grid_size, start_time)
    server.close()

start_main_node("video.mp4", (4, 3), 5)
