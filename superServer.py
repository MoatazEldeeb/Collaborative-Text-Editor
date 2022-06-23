# from collections import defaultdict
# from concurrent.futures import thread
# import difflib
# import os
# import socket
# import threading
# import tkinter as tk
# from tkinter.filedialog import askopenfilename, asksaveasfilename
# import json
# import dbconnection

# class CS:
#     def __init__(self, addr, av):
#         self.addr = addr
#         self.av = av
#     def updateAv(self, av):
#         self.av = av

# #for timeouts: https://stackoverflow.com/questions/2719017/how-to-set-timeout-on-pythons-socket-recv-method

# HEADER = 64
# PORT = 5050
# PPORT1 = 6060 # to create ping threads that will keep pinging servers to check if they're alive
# PPORT2 = 6070
# PPORT3 = 6080
# SERVER = "192.168.1.101"
# ADDR = (SERVER, PORT)
# PSRV1 = (SERVER, PPORT1) # to create ping threads that will keep pinging servers to check if they're alive
# PSRV2 = (SERVER, PPORT2)
# PSRV3 = (SERVER, PPORT3)
# TIMEOUTSERVER = 30 # 30 seconds
# FORMAT = 'utf-8'
# DISCONNECT_MSG = '!disconnect'
# REQUEST_C_MSG = '!requestconnect'
# ADDRCS1 = ('192.168.111.1', '5060')     #VM     1
# ADDRCS2 = ('192.168.24.1', '5070')      #VM     2
# ADDRCS3 = ('192.168.1.101', '5080')     #Local  1
# CS1 = CS(ADDRCS1, False)
# CS2 = CS(ADDRCS2, False)
# CS3 = CS(ADDRCS3, False)
# SERVERS = [CS1, CS2, CS3]

# # Thread for ping-pong for CS
# def serverApp(ts, toms): #ts = target server, to = timeout (in ms)
#     tos = toms / 1000 #timeout in seconds
#     # we have both to and toms for ease-of-use for different functions that may require milliseconds or seconds.
#     client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     connected = False
#     # client.settimeout(tos) # seconds to timeout
#     while not connected:
#         print("Trying to connect to {ts} - Please hold...\n(to = {to})\n")
#         client.create_connection()
#     def isAlive(ts, toms):
#         pass





































# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind(ADDR)

# theText = {}
# textCopy = {}
# filePaths ={}
# clients =[]

# #Function to apply differnences to text 
# def applyDiff(text , changes):
#     print("Applying Diff => ", changes)
#     x = list(changes.keys())
#     y= list(changes.values())[0]
#     if "delete" in x:
#         dele =  y[0][1]+ len(y) -1
#         text = text[:y[0][1]] + text[dele+1:]
#         print(text)
#     if "insert" in x:
#         for i in y:
#             text= text[:i[1]] + i[0] + text[i[1]:]
   
#     return text

# #Function to get the diffrence from original text to modified text
# def diff(original, copy):  
#     updates =defaultdict(list)
#     print('{} => {}'.format(original,copy)) 
#     for i,s in enumerate(difflib.ndiff(original, copy)):
#         if s[0]==' ': continue
#         elif s[0]=='-':
#             updates['delete'].append((s[-1],i))
#         elif s[0]=='+':
#             updates['insert'].append((s[-1],i))  
#     return updates

# #Send function protocol
# def send(msg, c):
#     message = msg.encode(FORMAT)
#     msgLength = len(message)
#     sendLength = str(msgLength).encode(FORMAT)
#     sendLength += b' ' * (HEADER - len(sendLength))
#     c.send(sendLength)
#     c.send(message)

# # Threaded funtion (one for every client connection) to handle syncronization
# def handle_client(conn, addr):
#     # global theText,textCopy,filePaths,clients code works without this 
#     print(f"[NEW CONNECTION REQUESTED] {addr} trying to connect...")
#     name = conn.getpeername()
#     print("\n\n\n")
#     print(name)
#     connected = True
#     while connected:
#         msgLength = conn.recv(HEADER).decode(FORMAT)
        
#         if msgLength:
#             msgLength = int(msgLength)
#             msg = conn.recv(msgLength).decode(FORMAT)

#             if msg == DISCONNECT_MSG:
#                 connected = False
#                 print(f"[{addr}] Disconnected")
#                 send("Message Recieved",conn)
#                 # conn.send("Message Recieved".encode(FORMAT))

#             elif msg[:2] == "//":
                
#                 fileId = int(msg[2:])
#                 print("FILE ID",fileId)
#                 filePath=dbconnection.getPathOfFile(fileId)
#                 # filePath = msg
#                 print(f"[{addr}] Opened file: {filePath}")
#                 if filePath in filePaths.values():
#                     filePaths[conn.getpeername()] = filePath
#                     temp = '$'+str(theText[filePath])
#                     send(temp,conn)
#                     # conn.send(temp.encode(FORMAT))
#                 else:
#                     filePaths[conn.getpeername()] = filePath
#                     with open(filePath, "r") as input_file:
#                         theText[filePath] = input_file.read()
#                         print("the text = ",theText[filePath])
#                         textCopy[filePath] = theText[filePath]
#                         temp = '$'+str(theText[filePath])
#                         send(temp,conn)
#                         # conn.send(temp.encode(FORMAT))
                        
#             elif is_json(msg): 
#                 d = json.loads(msg)
#                 textCopy[filePath] = applyDiff(textCopy[filePath],d)
                
                
#                 updates = dict(diff(theText[filePath],textCopy[filePath]))
#                 delta = json.dumps(updates)

#                 theText[filePath] = applyDiff(theText[filePath],d)

                
#                 for c in clients:
#                     fi = filePaths[c.getpeername()]
#                     print("fi ===" ,fi)
#                     for cli,f in filePaths.items():
#                         print("f === ",f)
#                         if (f==fi) and (cli != c.getpeername()) and (conn.getpeername() != c.getpeername()):
#                             send(delta, c)
#                             # c.send(delta.encode(FORMAT))
                   
                            
#                 textCopy[filePath] = theText[filePath]
#             elif msg =="send list of files":
#                 filesList= dbconnection.getAllFileNames()
#                 print(filesList)
#                 filesListJson=json.dumps(filesList)
#                 send((".."+filesListJson),conn)
#                 # conn.send((".."+filesListJson).encode(FORMAT))

#             elif msg == "_SAVE":
                
#                 with open(filePaths[name], "w") as output_file:
#                     output_file.write(theText[filePath])
#                 pass
#             else:
#                 send("Message Recieved",conn)
#                 # conn.send("Message Recieved".encode(FORMAT))
#             print(f"[{addr}] {msg}")

        
            
#     conn.close()

# #function to check if string is json
# def is_json(myjson):
#     try:
#         json.loads(myjson)
#     except ValueError as e:
#         return False
#     return True

# #main function to start server
# def start():
#     global clients
#     server.listen()
#     print(f"[LISTENING] Server is listening on {SERVER}")
    
#     while True:
        
#         conn , addr = server.accept()
#         clients.append(conn)
#         thread = threading.Thread(target=handle_client, args= (conn,addr))
#         thread.start()
#         print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


# print("[STARTING] server is starting")
# start()

