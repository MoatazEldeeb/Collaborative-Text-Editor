from concurrent.futures import thread
import os
import socket
import threading
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MSG = '!disconnect'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

theText = ""
textCopy = ""

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    filePath = ""
    connected = True
    while connected:
        msgLength = conn.recv(HEADER).decode(FORMAT)
        if msgLength:
            msgLength = int(msgLength)
            msg = conn.recv(msgLength).decode(FORMAT)
            isFile = os.path.isfile(msg)
            if msg == DISCONNECT_MSG:
                connected = False
                print(f"[{addr}] Disconnected")

            elif isFile:
                print(f"[{addr}] Opened file: {msg}")
                filePath = msg

            else: 
                print(f"[{addr}] {msg}")
                
            conn.send("Message Recieved".encode(FORMAT))
    
    conn.close()



def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    
    while True:
        conn , addr = server.accept()
        thread = threading.Thread(target=handle_client, args= (conn,addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting")
start()

