import socket

PORT = 5060
SERVER = "192.168.1.102"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR = (SERVER, PORT)
server.bind(ADDR)

server.listen()

conn, addr = server.accept()
print("Server connected to a client")
while True:
    print("Receiving...")
    message = conn.recv(1024)
    print(message.decode())
    conn.send(b'Pong!')
    