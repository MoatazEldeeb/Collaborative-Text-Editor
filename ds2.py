import socket
import threading

threads = []

PPORT   = 6070
PORT    = 5070
SERVER  = "192.168.1.102"
PADDR   = (SERVER, PPORT)
ADDR    = (SERVER,  PORT)

def pong():
    pserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    pserver.bind(PADDR)

    pserver.listen()

    conn, addr = pserver.accept()
    print("Server connected to super server")
    while True:
        message = conn.recv(1024)
        print(message.decode())
        conn.send(b'Pong!')
        
def client_handler(conn, addr):
    print("Server connected to a client")
    while True:
        print("Receiving...")
        message = conn.recv(1024)
        print(message.decode())
        conn.send(b'Pong from client!')
        
myPong = threading.Thread(target=pong)

myPong.start()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind(ADDR)

server.listen()

while True:
    conn, addr = server.accept()
    myT = threading.Thread(target=client_handler, args=(conn,addr,))
    myT.start()
    threads.append(myT)

