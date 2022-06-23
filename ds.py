import socket
import threading

PPORT   = 6080
PORT    = 5080
SERVER  = "192.168.1.102"
PADDR   = (SERVER, PPORT)
ADDR    = (SERVER,  PORT)

def pong():
    pserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    pserver.bind(ADDR)

    pserver.listen()

    conn, addr = server.accept()
    print("Server connected to a client")
    while True:
        print("Receiving...")
        message = conn.recv(1024)
        print(message.decode())
        conn.send(b'Pong!')
        
myPong = threading.Thread(target=pong)

myPong.start()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDR)

server.listen()

conn, addr = server.accept()
print("Server connected to a client")
while True:
    print("Receiving...")
    message = conn.recv(1024)
    print(message.decode())
    conn.send(b'Pong!')
    
