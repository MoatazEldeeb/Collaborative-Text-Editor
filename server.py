from collections import defaultdict
from concurrent.futures import thread
import difflib
import os
import socket
import threading
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import json
import dbconnection

HEADER = 64
PORT = 5060
PPORT   = 6060
SERVER = "192.168.1.102"
PADDR   = (SERVER, PPORT)
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MSG = '!disconnect'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

theText = {}
textCopy = {}
filePaths ={}
clients =[]

def pong():
    pserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    pserver.bind(PADDR)

    pserver.listen()

    conn, addr = pserver.accept()
    print("Server connected to super server")
    while True:
        message = conn.recv(1024)
        print(message.decode())
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

# Threaded funtion (one for every client connection) to handle syncronization
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
                
                fileId = int(msg[2:])
                print("FILE ID",fileId)
                filePath=dbconnection.getPathOfFile(fileId)
                # filePath = msg
                print(f"[{addr}] Opened file: {filePath}")
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
                d = json.loads(msg)
                textCopy[filePath] = applyDiff(textCopy[filePath],d)
                
                
                updates = dict(diff(theText[filePath],textCopy[filePath]))
                delta = json.dumps(updates)

                theText[filePath] = applyDiff(theText[filePath],d)

                
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
                
                with open(filePaths[name], "w") as output_file:
                    output_file.write(theText[filePath])
                pass
            else:
                send("Message Recieved",conn)
                # conn.send("Message Recieved".encode(FORMAT))
            print(f"[{addr}] {msg}")

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
    myPong = threading.Thread(target=pong)
    myPong.start()
    while True:
        
        conn, addr = server.accept()
        clients.append(conn)
        thread = threading.Thread(target=handle_client, args= (conn,addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting")
start()

