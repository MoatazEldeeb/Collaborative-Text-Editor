import time
import socket
import threading

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

ADDRCS1 = ('192.168.1.102', 5060)     #SERVER 1
ADDRCS2 = ('192.168.1.102', 5070)     #SERVER 2
ADDRCS3 = ('192.168.1.102', 5080)     #SERVER 3
CS1 = CS(ADDRCS1, False)
CS2 = CS(ADDRCS2, False)
CS3 = CS(ADDRCS3, False)
SERVERS = [CS1, CS2, CS3]

PORT = 5050

SERVER = "192.168.1.102"
ADDR = (SERVER, PORT)


#This should be called every 60 seconds to update the availability of its set server.
def ourThread(server, clr):
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

                except Exception as e:
                    if(counter < 10):
                        print(f"{clr}[TRIES = {counter}] Connection failed, trying again...\n{endc}")
                    else:
                        
                        print(f"{clr}[TRIES = {counter}] Connection failed, max tries occured, Trying again in 1 minute...\n{endc}")
                        cn = False
                        
                        return cn
                else:
                    print(f"{clr}Connection succesful!{endc}")
                    cn = True
                    return cn
        else:
            client.send(b'Ping')
            print(f"{clr}Ping{endc}")
            client.settimeout(3.0)
            try:
                message = client.recv(1024)
            except:
                print(f"{clr}Server [{addr}] crashed{endc}")

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



t1 = threading.Thread(target=ourThread, args=(CS1,bcolors.OKBLUE,))
t2 = threading.Thread(target=ourThread, args=(CS2,bcolors.OKCYAN))
t3 = threading.Thread(target=ourThread, args=(CS3,bcolors.OKGREEN))

t1.start()
t2.start()
t3.start()

while True:
    time.sleep(5)
    clr1 = bcolors.OKBLUE if CS1.av else bcolors.WARNING
    clr2 = bcolors.OKCYAN if CS2.av else bcolors.WARNING
    clr3 = bcolors.OKGREEN if CS3.av else bcolors.WARNING
    
    print(f"{bcolors.OKBLUE}Server[{CS1.addr}] is:{bcolors.ENDC}{clr1} {CS1.getLife()}{bcolors.ENDC}\n")
    print(f"{bcolors.OKCYAN}Server[{CS2.addr}] is:{bcolors.ENDC}{clr2} {CS2.getLife()}{bcolors.ENDC}\n")
    print(f"{bcolors.OKGREEN}Server[{CS3.addr}] is:{bcolors.ENDC}{clr3} {CS3.getLife()}{bcolors.ENDC}\n")
    


# bg="#242424", fg="#FFFFFF", insertbackground="#CCCCCC"

# print(addr[0].split(".")[0] + "\n" + addr[0].split(".")[1])
# above code will print out the first two parts of the connecting client
# we use that to determine if the connecting client is local or not
# if local we return the normal address of the server (locally)
# if not then we return the hardcoded external ip address of the router, and the port of the server