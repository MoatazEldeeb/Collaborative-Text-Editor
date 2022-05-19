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
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MSG = '!disconnect'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

theText = {}
textCopy = {}
filePaths ={}
clients =[]

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
    

def handle_client(conn, addr):
    global theText,textCopy,filePaths,clients
    print(f"[NEW CONNECTION] {addr} connected.")
    name = conn.getpeername()
    connected = True
    while connected:
        msgLength = conn.recv(HEADER).decode(FORMAT)
        
        if msgLength:
            msgLength = int(msgLength)
            msg = conn.recv(msgLength).decode(FORMAT)

            if msg == DISCONNECT_MSG:
                connected = False
                print(f"[{addr}] Disconnected")
                conn.send("Message Recieved".encode(FORMAT))

            elif msg[:2] == "//":
                
                fileId = int(msg[2:])
                print("FILE ID",fileId)
                filePath=dbconnection.getPathOfFile(fileId)
                # filePath = msg
                print(f"[{addr}] Opened file: {filePath}")
                if filePath in filePaths.values():
                    temp = '$'+str(theText[filePath])
                    conn.send(temp.encode(FORMAT))
                else:
                    filePaths[name] = filePath
                    with open(filePath, "r") as input_file:
                        theText[filePath] = input_file.read()
                        print("the text = ",theText[filePath])
                        textCopy[filePath] = theText[filePath]
                        temp = '$'+str(theText[filePath])
                        conn.send(temp.encode(FORMAT))
                        
            elif is_json(msg): 
                d = json.loads(msg)
                textCopy[filePath] = applyDiff(textCopy[filePath],d)
                
                theText[filePath] = applyDiff(theText[filePath],d)

                updates = dict(diff(textCopy[filePath],theText[filePath]))
              

                for c in clients:
                    for f in filePaths.values():
                        
                        if f==filePath and not c.getpeername() == conn.getpeername():
                            c.send(('$'+textCopy[filePath]).encode(FORMAT))
                
                        
                            
                textCopy[filePath] = theText[filePath]
            elif msg =="send list of files":
                filesList= dbconnection.getAllFileNames()
                print(filesList)
                filesListJson=json.dumps(filesList)
                conn.send((".."+filesListJson).encode(FORMAT))

            elif msg == "_SAVE":
                
                with open(filePaths[name], "w") as output_file:
                    output_file.write(theText[filePath])
                pass
            else:
                conn.send("Message Recieved".encode(FORMAT))
            print(f"[{addr}] {msg}")

        
            
    conn.close()

def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True

def start():
    global clients
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    
    while True:
        
        conn , addr = server.accept()
        clients.append(conn)
        thread = threading.Thread(target=handle_client, args= (conn,addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting")
start()

