import socket
import threading
PORT = 5060
SERVER = "192.168.1.102"
threads = []
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR = (SERVER, PORT)
server.bind(ADDR)

server.listen()

# print(PORT.to_bytes())
# print(SERVER.encode())


def handler(conn):
    while True:
        print("Receiving...")
        message = conn.recv(1024)
        print(message.decode())
        
        conn.send(str(5060).encode())

while True:
    conn, addr = server.accept()

    print("Server connected to a client")
    newThread = threading.Thread(target=handler, args=(conn,))
    newThread.start()
    threads.append(newThread)

    