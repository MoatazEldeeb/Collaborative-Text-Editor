import socket
import time
import threading
PORT = 5050
SERVER = "192.168.1.102"

ssclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
csclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR = (SERVER, PORT)
csconnected = False

while not csconnected:
    try:
        ssclient.connect(ADDR)
        message = ssclient.recv(1024)
    except Exception as e:
        print(e)
        print("Failed to connect to super server.")
        time.sleep(5)
    else:
        print("Connected to super server, retrieving child server.")
        message = message.decode()
        if(message == "FAILED"):
            ssclient.shutdown(socket.SHUT_RDWR)
            ssclient.close()
            ssclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            time.sleep(5)
            print(message + "\nTrying again...")

            
        else:
                
            message = message.split(":")
            myAddr = message[0]
            myPort = int(message[1])
            SADDR = (myAddr, myPort)
            try:
                csclient.connect(SADDR)
                csclient.send(b'Hello am I connected?')
                messageFromChild = csclient.recv(1024)
            except:
                try:
                    ssclient.shutdown(socket.SHUT_RDWR)
                    ssclient.close()
                    ssclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                except:
                    print("Baby it's okay...")
                else:
                    print("Well it wasn't, but now it is...")
                print("Failed to connect to child server.")
                time.sleep(5)
            else:
                csconnected = True
                print(messageFromChild.decode())
print("Connection successful...")
while True:
    pass



