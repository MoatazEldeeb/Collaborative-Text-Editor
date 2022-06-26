from asyncio.windows_utils import pipe
import time
import socket
import threading
import queue as q
import pickle
import json
import os
import difflib
from collections import defaultdict
from xmlrpc.client import TRANSPORT_ERROR

cs1q = q.Queue()
cs2q = q.Queue()
cs3q = q.Queue()
qList = [cs1q, cs2q, cs3q]

### Creating a pipeline for servers ###
pipeline = q.Queue()
pipeline.put(0)
pipeline.put(1)
pipeline.put(2)
### Creating a pipeline for servers ###

###
class fileObj:
    def __init__(self, data):
        self.data = data
        self.upd = False
    def uData(self, data):
        self.data = data
        self.upd = True

file1Obj = fileObj("")
file2Obj = fileObj("")

upText = [file1Obj, file2Obj] # a list of two texts (for the two files currently, can be modified later to apply to dynamic file creation with database)
# on first open lel ss

###DIFF###
def diff(original, copy):  
    updates =defaultdict(list)
    print('{} => {}'.format(original,copy)) 
    for i,s in enumerate(difflib.ndiff(original, copy)):
        if s[0]==' ': continue
        elif s[0]=='-':
            updates['delete'].append((s[-1],i))
        elif s[0]=='+':
            updates['insert'].append((s[-1],i))  
    return updates

#Function to apply differnences to text 
def applyDiff(og , changes):
    text = og.data
    print("Applying Diff => ", changes)
    x = list(changes.keys())
    y= list(changes.values())[0]
    if "delete" in x:
        dele =  y[0][1]+ len(y) -1
        text = text[:y[0][1]] + text[dele+1:]
        print(text)
    if "insert" in x:
        for i in y:
            text= text[:i[1]] + i[0] + text[i[1]:]
   
    return text

###DIFF###





# cs func
    # check for text of test1.txt at super server
        # if text exists = take text
        # if no text exists, read local, send text to ss
# on mod
# cs send to ss with counter
# ss save mod with time on corresponding ids
# every file saved has a unique id
# for example, test.txt = 0(+1)
# test1.txt = 1(+1)
###

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
ADDRCS2 = ('192.168.24.128', 6070)     #SERVER 2
ADDRCS3 = ('192.168.1.102', 6080)     #SERVER 3
# SALIST = (ADDRCS1, ADDRCS2, ADDRCS3)
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
REQUEST_C_MSG = '!requestconnect' 
CHILD_REC_MSG = '!childupdate'
CHILD_UPD_LINK = '!childstream'
CHILD_CONF = '!Confirmed_CS_Req'

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
                    print(f"{clr}[CONNECTING TO {addr}]{endc}")
                    client.connect(addr)
                    # print(client)
                except Exception as e:
                    if(counter < 10):
                        print(f"{clr}[TRIES = {counter}] Connection failed, trying again...\n{endc}")
                        pass
                    else:
                        
                        print(f"{clr}[TRIES = {counter}] Connection failed, max tries occured, Trying again in 30 seconds...\n{endc}")
                        cn = False
                        
                        return cn
                else:
                    print(f"{clr}Connection succesful!{endc}")
                    cn = True
                    return cn
        else:
            
            try:
                client.send(b'Ping')
                print(f"{clr}Ping{endc}")
                client.settimeout(3.0)
                message = client.recv(1024).decode()
                

            except:
                print(f"{clr}Server [{addr}] crashed{endc}")

                return False
            else:
                print(message)
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


########################################################### CHILD SERVER SYNC ###########################################################

# while server.av = connected
#       listen(//{fileId})
#  connection.send(pickle.dumps(upText[fileId]))


def cs_feed(client, addr, server, queue):
    print("STARTING CS_FEED THREAD")
    while(server.av == True):
        try:
            fileId = queue.get(True, 10)
        except:
            continue
        else:

            print(f"Sending [{fileId}] to [{addr}]")
            client.send(str(fileId).encode())
            item = queue.get(True)
            item = json.dumps(item)
            
            print(f"Sending [{item}] to [{addr}]")
            client.send(item.encode())
    print("ENDING CS_FEED THREAD")

def cs_sync_handler(client, addr, server, myId):
    endc = bcolors.ENDC                                                     # this handles updating the SS
    # client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # client.settimeout(5.0)
    # client.connect(server.addr)
    print("CS_SYNC_HANDLER STARTING LOOP")
    while(server.av == True):
        try:
            msg = client.recv(1024) # wait forever for message from server
        except:
            continue
        else:
            
            message = msg.decode()
            print(f"[PRINTING MESSAGE RECEIVED IN CS_SYNC_HANDLER] [{message}] [PRINTING MESSAGE RECEIVED IN CS_SYNC_HANDLER]")
            if(message == ""):
                break
            if(message[:2] == "//"):
                fileId = int(message[2:]) # fileId = whatever is after the // turned into an int
                reqFile = upText[fileId-1]
                client.send(pickle.dumps(reqFile))

                print(pickle.dumps(reqFile))
                print(pickle.loads(pickle.dumps(reqFile)))
            elif(message[:2] == "$$"):
                
                
                fileId = int(message[2])
                client.send(CHILD_CONF.encode())

                item = client.recv(4096)
                item = json.loads(item)

                upText[fileId-1].uData(applyDiff(upText[fileId-1],item))
                print(f"update file[{fileId}]")
                for j in range(3):
                    print(f"Going for qList[{j}]")
                    if(j != myId):
                        if(SERVERS[j].av):
                            print(f"Inserting [{fileId}] & [{item}] into qList[{j}]")
                            qList[j].put(fileId)
                            qList[j].put(item)
    print("CS_SYNC_HANDLER ENDING LOOP")
                
########################################################### CHILD SERVER SYNC ###########################################################


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


############################################################# THREAD CODE ##############################################################
t1 = threading.Thread(target=cs_handler, args=(CS1,bcolors.OKBLUE,), daemon= True)
t2 = threading.Thread(target=cs_handler, args=(CS2,bcolors.OKCYAN,), daemon= True)
t3 = threading.Thread(target=cs_handler, args=(CS3,bcolors.HEADER,), daemon= True)
sst = threading.Thread(target=server_status, daemon= True)

t1.start()
t2.start()
t3.start()
sst.start()
############################################################# THREAD CODE ##############################################################


####################################################### CLIENT CONNECTION HANDLER ######################################################
# This is handled by the main thread, since this is the main function of the super server.
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()

while True:
    clientSocket, clientAddr = server.accept()
    #Check if client is local or not
    # set counter to 0
    ### CHECK IF IT'S A CLIENT OR A CHILD SERVER REQUESTING A CONNECTION ###
    message = clientSocket.recv(1024).decode()
    if(message == CHILD_REC_MSG):
        print("client is a child server...")
        clientSocket.send(CHILD_CONF.encode()) 
        message = clientSocket.recv(1024).decode() # should be XYZ.XYZ.XYZ.XYZ:ABCD
        message = message.split(":")
        mIP = message[0]
        mPort = int(message[1])
        mAddr = (mIP, mPort)
        for i in range(3):
            if (mAddr == SERVERS[i].addr) :
                print(f"[mAddr] = {mAddr}\n[server addr] = {SERVERS[i].addr}")
                clientSocket.send(CHILD_CONF.encode())
                threading.Thread(target=cs_sync_handler, args=(clientSocket, clientAddr, SERVERS[i], i), daemon= True).start()
                print("\nWaiting for connection...\n")
                clientSocket2, clientAddr2 = server.accept()
                threading.Thread(target=cs_feed, args=(clientSocket2, clientAddr2, SERVERS[i], qList[i]), daemon= True).start()
            else:
                clientSocket.send(b'FAILED:No server found...')
        

    elif(message == REQUEST_C_MSG):
        ### CHECK IF IT'S A CLIENT OR A CHILD SERVER REQUESTING A CONNECTION ###
        clientHandled = False

        claddr1 = clientAddr[0].split(".")[0]
        claddr2 = clientAddr[0].split(".")[1] 
        if((claddr1 == "192") & (claddr2 == "168")):    # client is local
            print("client is local...")
            # check the pipeline to see which server's turn is up
            # remove server from the front of the queue and insert it at the back
            for i in range(3):
                
                turnOf = pipeline.get()
                pipeline.put(turnOf)
                currServer = SERVERS[turnOf]
                if(currServer.av ): # check the server's availability
                    if(quickCheck(currServer)):
                        print(f"Sending server[{currServer}] to client[{clientAddr}]...")
                        clientSocket.send(currServer.getAddrInBytes()) # if available give server local ip and port
                        
                        print(f"Sending [{currServer.getAddrInBytes()}] to [{clientAddr}]")
                        clientHandled = True

            if(not clientHandled):              # if counter = 3 (you looped over all servers)
                clientSocket.send(b'FAILED')    # disconnect client (server maintenance)
        
        else:                                       # client is not local
            print("client is external...")
            # check the pipeline to see which server's turn is up
            # remove server from the front of the queue and insert it at the back
            for i in range(3):
                
                turnOf = pipeline.get()
                pipeline.put(turnOf)
                currServer = SERVERS[turnOf]
                if(currServer.av): # check the server's availability
                    if(quickCheck(currServer)):
                        addrInBytes = (EXTERNALIP + ":" + str(currServer.getPort()-1000)).encode()
                        print(f"Sending [{addrInBytes}] to [{clientAddr}]")
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