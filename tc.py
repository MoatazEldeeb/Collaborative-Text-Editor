import socket
import threading
PORT = 5050
SERVER = "192.168.1.102"
threads = []
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR = (SERVER, PORT)
client.connect(ADDR)

message = client.recv(1024)
message = message.decode()
if(message == "FAILED"):
    print(message)
    while True:
        pass
else:
        
    message = message.split(":")
    myAddr = message[0]
    myPort = int(message[1])
    SADDR = (myAddr, myPort)
    print(SADDR)
    while True:
        pass
