from collections import defaultdict
import difflib
import pickle
import socket
import threading
from tkinter.filedialog import askopenfilename, asksaveasfilename
import json
import dbconnection # we need to add this to ss

HEADER = 64
PORT = 5060
PPORT   = 6060
SERVER = "192.168.1.102"
SSERVER = "192.168.1.102"
SSPORT = 5050
PADDR   = (SERVER, PPORT)
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MSG = '!disconnect'
CHILD_UPD_LINK = '!childstream'
CHILD_REC_MSG = '!childupdate'

###
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
SSADDR = (SSERVER, SSPORT)
###
connForUpdates = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
recvForUpdates = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
class fileObj:
    def __init__(self, data):
        self.data = data
        self.upd = False
    def uData(self, data):
        self.data = data
        self.upd = True
###


###
theText = {}
textCopy = {}
filePaths ={}
clients =[]


### THREAD MANAGER ###
# class Session:
#     def __init__(self, curr):
#         self.curr = curr
#     def incSession(self):
#         self.curr += 1
#     def getSession(self):
#         return self.session
#     def copy(self):
#         return Session(self.curr)
# servSession = Session(0)
### THREAD MANAGER ###


# def reqUpdSS(id):
#     message = "//" + str(id)
#     send(message, connForUpdates)

# def givUpdSS(text, id):
#     message = "$$." + str(id) + "." + text
#     send(message, connForUpdates)

def recvUpdFromSS():
    global theText,textCopy,filePaths,clients

    while True:
        fileId = recvForUpdates.recv(1024).decode()
        try:
            fileId = int(fileId)
        except:
            print("this shouldn't be here")
            print(fileId)
            continue
        else:
            pass # this is not finished, all code should be here
        filePath = dbconnection.getPathOfFile(fileId)
        item = recvForUpdates.recv(4096)
        item = json.loads(item)
        if filePath in filePaths.values():
            theText[filePath] = applyDiff(textCopy[filePath], item)
            textCopy[filePath] = theText[filePath]
            for c in clients:
                fi = filePath
                print("fi ===" ,fi)
                for f in filePaths.values():
                    print("f === ",f)
                    if (f==fi):
                        send(item, c)
                        # c.send(delta.encode(FORMAT))

        # if filePath in filePaths.values():
        #     pass
        #     for c in clients:
        #         send(item, c)
        # else:

        #     with open(filePath, "w") as output_file:
        #         theText[filePath] = applyDiff(theText[filePath], item) # SHOULD BE LATER
        #         textCopy[filePath] = theText[filePath]
        #         temp = '$'+str(theText[filePath])
        #         send(temp,conn)
                
                            # c.send(delta.encode(FORMAT))
                # conn.send(temp.encode(FORMAT))
        
        applyDiff()

def updateServerText(fileId, diff):
    msgToSend = "$$" + str(fileId)
    connForUpdates.send(msgToSend.encode())
    message = connForUpdates.recv(1024).decode()
    print(message) # should be !Confirm
    connForUpdates.send(diff.encode())


def checkServerFile(fileId):
    msgToSend = "//" + str(fileId)
    print(f"[PRINTING CONNECTION]\n{connForUpdates}\n[PRINTING CONNECTION]")
    connForUpdates.send(msgToSend.encode())
    connForUpdates.settimeout(0.5)
    while True:
        
        try:
            item = connForUpdates.recv(4096)
        except:
            break
        else:
            item += item
    print(f"Pickling items into an object \n[{item}]")
    item = pickle.loads(item)
    print(f"Finished pickling items \n[{item}]")

    if(item.upd):
        return (True, item.data)
    else:
        return (False, None)
        


def pong():
    pserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    pserver.bind(PADDR)

    pserver.listen()
    conn, addr = pserver.accept()
    connForUpdates.connect(SSADDR)
    connForUpdates.send(CHILD_REC_MSG.encode())
    message = connForUpdates.recv(1024)
    print(message.decode()) # should be !Confirmed_CS_Req
    sndmsg = SERVER + ":" + str(PPORT)
    connForUpdates.send(sndmsg.encode())
    message = connForUpdates.recv(1024)
    print(message.decode()) # should be !Confirmed_CS_Req

    
    # connForUpdates.connect(SSADDR)
    # connForUpdates.send(CHILD_REC_MSG.encode())
    

 
    print("Trying to connect...")
    recvForUpdates.connect(SSADDR)
    threading.Thread(target=recvUpdFromSS).start()
    print("Connected?")
    
    print("Server connected to super server")
    while (True): #(True if session hasn't changed)
        try:
            print("Waiting for ping")
            message = conn.recv(1024)
        except Exception as e:
            print("FAILED: " + message.decode() + "\n" + f"[EXCEPTION] {e} [EXCEPTION]")
            pass
        else:
            print(message.decode() + "Sending Pong!")
            conn.send(b'Pong!')



#Function to apply differnences to text 
def applyDiff(text , changes):
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

#Function to get the diffrence from original text to modified text
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

#Send function protocol
def send(msg, c):
    message = msg.encode(FORMAT)
    # msgLength = len(message)
    # sendLength = str(msgLength).encode(FORMAT)
    # sendLength += b' ' * (HEADER - len(sendLength))
    # c.send(sendLength)
    c.send(message)

# Threaded funtion (one for every client connection) to handle synchronization
def handle_client(conn, addr):
    global theText,textCopy,filePaths,clients
    print(f"[NEW CONNECTION] {addr} connected.")
    name = conn.getpeername()
    print("\n\n\n")
    print(name)
    connected = True
    while connected:
        # msgLength = conn.recv(HEADER).decode(FORMAT)
        msg = conn.recv(1024).decode(FORMAT)
        
        # if msgLength:
        if msg:
            # msgLength = int(msgLength)
            # msg = conn.recv(msgLength).decode(FORMAT)

            if msg == DISCONNECT_MSG:
                connected = False
                print(f"[{addr}] Disconnected")
                send("Message Recieved",conn)
                # conn.send("Message Recieved".encode(FORMAT))

            elif msg[:2] == "//":
                
                # modify this function to work like this:
                # take the fileId, send it to the super server.
                # ask super server if there's currently opened unsaved text for fileID
                # if yes (This automatically covers for if text is here, because it automatically gets sent to ss)
                    # copy text from super server, and give it to client, save it here (cache)
                # if no
                    # read text from saved file locally, and send it to super server

                fileId = int(msg[2:])
                print("FILE ID",fileId) # what does this print? (prints id in integers of 1 to k representing file in db)
                # checkForText(fileId) # -> undefined function yet, will go to ss to check for text
                filePath=dbconnection.getPathOfFile(fileId)
                # filePath = msg
                print(f"[{addr}] Opened file: {filePath}")
                checkServerFile(fileId) # IMPORTANT TO STOP HERE
                if filePath in filePaths.values():
                    filePaths[conn.getpeername()] = filePath
                    temp = '$'+str(theText[filePath])
                    send(temp,conn)
                    # conn.send(temp.encode(FORMAT))
                else:
                    filePaths[conn.getpeername()] = filePath
                    with open(filePath, "r") as input_file:
                        theText[filePath] = input_file.read()
                        print("the text = ",theText[filePath])
                        textCopy[filePath] = theText[filePath]
                        temp = '$'+str(theText[filePath])
                        send(temp,conn)
                        # conn.send(temp.encode(FORMAT))
            elif (msg=="Ping"):
                print(msg)
                send('Pong!', conn)
            
            elif is_json(msg): 
                noExcept = True

                d = json.loads(msg)
                try:
                    textCopy[filePath] = applyDiff(textCopy[filePath],d)
                except Exception as e:
                    # print(f"[EXCEPTION PRINTING] {e} [EXCPETION PRINTING]")
                    print(f"[EXCEPTION] Trying to write into server without specifying file first [EXCEPTION]")
                    noExcept = False
                else:
                    pass
                if(noExcept):
                    updateServerText(fileId, msg)
                    updates = dict(diff(theText[filePath],textCopy[filePath]))
                    delta = json.dumps(updates)

                    theText[filePath] = applyDiff(theText[filePath],d)
                    fileId=dbconnection.getIdOfFile(filePath)
                    print("[FILE ID PRINTING]\n" , fileId , "\n[FILE ID PRINTING]")

                    # updateSS(theText[filePath], fileId, )
                    # send the text with fileId to super server so super server can update other servers

                    
                    for c in clients:
                        fi = filePaths[c.getpeername()]
                        print("fi ===" ,fi)
                        for cli,f in filePaths.items():
                            print("f === ",f)
                            if (f==fi) and (cli != c.getpeername()) and (conn.getpeername() != c.getpeername()):
                                send(delta, c)
                                # c.send(delta.encode(FORMAT))
                    
                                
                    textCopy[filePath] = theText[filePath]
            elif msg =="send list of files":
                filesList= dbconnection.getAllFileNames()
                print(filesList)
                filesListJson=json.dumps(filesList)
                send((".."+filesListJson),conn)
                # conn.send((".."+filesListJson).encode(FORMAT))

            elif msg == "_SAVE":
                try:

                    with open(filePaths[name], "w") as output_file:
                        output_file.write(theText[filePath])
                except Exception as e:
                    # print(f"[EXCEPTION PRINTING] {e} [EXCEPTION PRINTING]")
                    pass
                pass
            else:
                send("Message Recieved",conn)
                # conn.send("Message Recieved".encode(FORMAT))
            print(f"[{addr}] {msg}")
    print("\nDisconnecting")
    clients.remove(conn)    # remove client from list of clients!
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()


#function to check if string is json
def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True

#main function to start server
def start():
    global clients
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    myPong = threading.Thread(target=pong, daemon=True)
    myPong.start()
    while True:
        
        conn, addr = server.accept() 
        clients.append(conn)
        thread = threading.Thread(target=handle_client, daemon=True, args= (conn,addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting")
start()

