from asyncio.windows_utils import pipe
import time
import socket
import threading
import queue as q
import os

### Creating a pipeline for servers ###
pipeline = q.Queue()
pipeline.put(0)
pipeline.put(1)
pipeline.put(2)
### Creating a pipeline for servers ###

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

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
    # Returns address as "xyz.xyz.xyz.xyz:abcd" encoded in bytes (b'ourstring')
    def getAddrInBytes(self):
        result = self.addr[0] + ":" + str((self.addr[1]-1000))
        return result.encode()
    def getPort(self):
        return self.addr[1]

ADDRCS1 = ('192.168.1.102', 6060)     #SERVER 1
ADDRCS2 = ('192.168.1.102', 6070)     #SERVER 2
ADDRCS3 = ('192.168.1.102', 6080)     #SERVER 3
CS1 = CS(ADDRCS1, False)
CS2 = CS(ADDRCS2, False)
CS3 = CS(ADDRCS3, False)
SERVERS = [CS1, CS2, CS3]

#### SUPER SERVER ADDR ###
PORT = 5050
SERVER = "192.168.1.102"
ADDR = (SERVER, PORT)
EXTERNALIP = "41.45.195.172"
#### SUPER SERVER ADDR ###


def quickCheck(server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(server.addr)
    except:
        return False
    else: 
        return True

#This should be called every 15 seconds to update the availability of its set server.
######################################################### CHILD SERVER HANDLER #########################################################
def cs_handler(server, clr):
    endc = bcolors.ENDC
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
                    # print(f"{clr}[CONNECTING TO {addr}]{endc}")
                    client.connect(addr)
                    # print(client)

                except Exception as e:
                    if(counter < 10):
                        # print(f"{clr}[TRIES = {counter}] Connection failed, trying again...\n{endc}")
                        pass
                    else:
                        
                        # print(f"{clr}[TRIES = {counter}] Connection failed, max tries occured, Trying again in 30 seconds...\n{endc}")
                        cn = False
                        
                        return cn
                else:
                    # print(f"{clr}Connection succesful!{endc}")
                    cn = True
                    return cn
        else:
            
            try:
                client.send(b'Ping')
                # print(f"{clr}Ping{endc}")
                client.settimeout(3.0)
                message = client.recv(1024)
            except:
                # print(f"{clr}Server [{addr}] crashed{endc}")

                return False
            else:
                # print(message.decode())
                return True

    while True:
        connected = tryConnect(myAddr, myAv, counter)
        if((not connected) & myAv):
            print(f"Server[{myAddr}] offline: {myAv}")
            client.shutdown(socket.SHUT_RDWR)
            client.close()
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(30)
        server.updateAv(connected)
        myAv = connected
        time.sleep(15)
######################################################### CHILD SERVER HANDLER #########################################################

############################################################# SERVER STATUS ############################################################
def server_status():
    while True:
        time.sleep(5)
        clr1 = bcolors.OKGREEN if CS1.av else bcolors.FAIL
        clr2 = bcolors.OKGREEN if CS2.av else bcolors.FAIL
        clr3 = bcolors.OKGREEN if CS3.av else bcolors.FAIL
        # _ = os.system('cls')
        print(f"{bcolors.OKBLUE}Server[{CS1.addr}] is:{bcolors.ENDC}{clr1} {CS1.getLife()}{bcolors.ENDC}\n")
        print(f"{bcolors.OKCYAN}Server[{CS2.addr}] is:{bcolors.ENDC}{clr2} {CS2.getLife()}{bcolors.ENDC}\n")
        print(f"{bcolors.HEADER}Server[{CS3.addr}] is:{bcolors.ENDC}{clr3} {CS3.getLife()}{bcolors.ENDC}\n")
############################################################# SERVER STATUS ############################################################


t1 = threading.Thread(target=cs_handler, args=(CS1,bcolors.OKBLUE,))
t2 = threading.Thread(target=cs_handler, args=(CS2,bcolors.OKCYAN,))
t3 = threading.Thread(target=cs_handler, args=(CS3,bcolors.HEADER,))
sst = threading.Thread(target=server_status)

t1.start()
t2.start()
t3.start()
sst.start()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()

####################################################### CLIENT CONNECTION HANDLER ######################################################
# This is handled by the main thread, since this is the main function of the super server.
while True:
    clientSocket, clientAddr = server.accept()
    #Check if client is local or not
    # set counter to 0
    clientHandled = False
    claddr1 = clientAddr[0].split(".")[0]
    claddr2 = clientAddr[0].split(".")[1]
    if((claddr1 == "192") & (claddr2 == "168")):    # client is local
        # check the pipeline to see which server's turn is up
        # remove server from the front of the queue and insert it at the back
        for i in range(3):
            print("client is local...")
            turnOf = pipeline.get()
            pipeline.put(turnOf)
            currServer = SERVERS[turnOf]
            if(currServer.av ): # check the server's availability
                if(quickCheck(currServer)):
                    print(f"Sending server[{currServer}] to client[{clientAddr}]...")
                    clientSocket.send(currServer.getAddrInBytes()) # if available give server local ip and port
                    clientHandled = True

        if(not clientHandled):              # if counter = 3 (you looped over all servers)
            clientSocket.send(b'FAILED')    # disconnect client (server maintenance)
    
    else:                                       # client is not local
        # check the pipeline to see which server's turn is up
        # remove server from the front of the queue and insert it at the back
        for i in range(3):
            
            turnOf = pipeline.get()
            pipeline.put(turnOf)
            currServer = SERVERS[turnOf]
            if(currServer.av): # check the server's availability
                if(quickCheck(currServer)):
                    addrInBytes = (EXTERNALIP + ":" + str(currServer.getPort())).encode()
                    clientSocket.send(addrInBytes) # if available give server external ip and port
                    clientHandled = True

        if(not clientHandled):              # if counter = 3 (you looped over all servers)
            clientSocket.send(b'FAILED')    # disconnect client (server maintenance)
####################################################### CLIENT CONNECTION HANDLER ######################################################

    


# bg="#242424", fg="#FFFFFF", insertbackground="#CCCCCC"

# print(addr[0].split(".")[0] + "\n" + addr[0].split(".")[1])
# above code will print out the first two parts of the connecting client
# we use that to determine if the connecting client is local or not
# if local we return the normal address of the server (locally)
# if not then we return the hardcoded external ip address of the router, and the port of the server