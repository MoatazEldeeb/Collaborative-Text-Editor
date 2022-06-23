import time
import socket
import threading

class CS:
    def __init__(self, addr, av):
        self.addr = addr
        self.av = av
    def updateAv(self, av):
        self.av = av
    def getLife(self):
        if(self.av):
            return ("online")
        else:
            return ("offline")

ADDRCS1 = ('192.168.111.1', 5060)     #VM     1
ADDRCS2 = ('192.168.24.1', 5070)      #VM     2
ADDRCS3 = ('192.168.1.102', 5080)     #Local  1
CS1 = CS(ADDRCS1, False)
CS2 = CS(ADDRCS2, False)
CS3 = CS(ADDRCS3, False)
SERVERS = [CS1, CS2, CS3]

PORT = 5050

SERVER = "192.168.1.102"
ADDR = (SERVER, PORT)


#This should be called every 60 seconds to update the availability of its set server.
def ourThread(server):
    myAddr = server.addr
    myAv = server.av
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(30)

    counter = 0
    def tryConnect(addr, cn, counter):
        
        if(not cn):
            while True:
                counter += 1
                try:
                    print(f"[CONNECTING TO {addr}]")
                    client.connect(addr)

                except Exception as e:
                    if(counter < 10):
                        print(f"[TRIES = {counter}] Connection failed, trying again...\n")
                    else:
                        
                        print(f"[TRIES = {counter}] Connection failed, max tries occured, Trying again in 1 minute...\n")
                        cn = False
                        
                        return cn
                else:
                    print("Connection succesful!")
                    cn = True
                    return cn
        else:
            client.send(b'Ping')
            print("Ping")
            client.settimeout(3.0)
            try:
                message = client.recv(1024)
            except:
                print(f"Server [{addr}] crashed")

                return False
            else:
                print(message.decode())
                return True

    while True:
        connected = tryConnect(myAddr, myAv, counter)
        if((not connected) & myAv):
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(30)
        server.updateAv(connected)
        myAv = connected
        time.sleep(10)

   
        
    client.close()



t1 = threading.Thread(target=ourThread, args=(CS3,))
# t2 = threading.Thread(target=ourThread, args=(CS3,))
t1.start()
# t2.start()
print("Hello")
while True:
    print(f"Server is: {CS3.getLife()}\n")
    time.sleep(5)


# bg="#242424", fg="#FFFFFF", insertbackground="#CCCCCC"