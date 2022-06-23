import socket
import time
import threading
PORT = 5050
SERVER = "192.168.1.102"

ssclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
csclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ADDR = (SERVER, PORT)
connected = False

# at first run it keeps trying to connect until it succeeds.
# open a thread to ping the server
# after it connects it retrieves the data from the server and continues as normal (normal code)
# if the pinging thread fails to retrieve a pong from the server it terminates the connection safely (shutdown, close)
# then attempts to re-init the connection again using initConnSup()
# meanwhile when the server is off (after first conn) user CAN type, but all that is typed will be ignored and,
# automatically deleted when a new connection is made. (we should make a label for when it's connected and when it's not)

def pingServer():
    global csclient
    counter = 0
    while True:
        if(counter == 5):
            csclient.shutdown(socket.SHUT_RDWR)
            csclient.close()
            csclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            return False
        try:
            csclient.send(b'Ping')
            # print(f"{clr}Ping{endc}")
            csclient.settimeout(3.0)
            message = csclient.recv(1024)
        except:
            # print(f"{clr}Server [{addr}] crashed{endc}")
            counter += 1
        else:
            # print(message.decode())
            counter = 0
            return True
####################################################### FETCHING CHILD SERVER #######################################################
def initConnSup():
    global ssclient, csclient
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
                        pass
                    else:
                        pass
                    print("Failed to connect to child server.")
                    time.sleep(5)
                else:
                    csconnected = True
                    print(messageFromChild.decode())
                    return csconnected
####################################################### FETCHING CHILD SERVER #######################################################

connected = initConnSup()
print("Connection successful...")
csclient.send(b'Hello again from outside of the world')

while True:
    csclient.send(b'Hello world')
    message = csclient.recv(1024)
    time.sleep(5)