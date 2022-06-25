from collections import defaultdict
import ctypes
import socket
import threading
import tkinter as tk
from tkinter import ttk
import difflib
import json
import time
from tkinter.font import BOLD

closTime = False

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MSG = '!disconnect'
SERVER = "192.168.1.102"
ADDR = (SERVER, PORT)
REQUEST_C_MSG = '!requestconnect' 
connected = False
####################################################### FETCHING CHILD SERVER #######################################################
def initConnSup():
    global  client, connected, closTime
    ###
    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
    def raise_exception(self):
        thread_id = self.get_id()
        resu = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if resu > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Failure in raising exception') 
    ###
    ssclient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connected = False
    counter = 0

    while True:
        if closTime:
            break
        if not connected:    
            
            try:
                ssclient.connect(ADDR)
                message = ssclient.recv(1024)
            except Exception as e:
                print(e)
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
                    saddr = (myAddr, myPort)
                    try:
                        client.connect(saddr)
                        # client.send(b'Hello am I connected?')
                        # messageFromChild = client.recv(1024)
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
                        connected = True
                        print("Connected!")
                        counter = 0
                        if connected:

                            ###
                            try:
                                thread.raise_exception()
                                thread.join()
                            except:
                                pass
                            else:
                                pass
                            ###
                            thread = threading.Thread(name="o",target=recievingUpdates,daemon=True, args= ())
    
                            thread.start()
                        # print(messageFromChild.decode())
                        
        else:
            try:
                send("Ping")
            except:
                try:
                    client.shutdown(socket.SHUT_RDWR)
                    client.close()
                    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                except:
                    pass
            else:
                time.sleep(3)
        #     if(counter == 5):
        #         client.shutdown(socket.SHUT_RDWR)
        #         client.close()
        #         client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #         connected = False
        #     else:
        #         try:
        #             # client.send(b'Ping')
        #             send("Ping")
        #             # print(f"{clr}Ping{endc}")
                    
        #             # message = client.recv(1024)
        #             time.sleep(3)
        #         except:
        #             # print(f"{clr}Server [{addr}] crashed{endc}")
        #             counter += 1
                    
        #         else:
        #             # print(message.decode())
        #             counter = 0
        #             connected = True

####################################################### FETCHING CHILD SERVER #######################################################


#Protocol to send message
def send(msg):
    if connected:
        message = msg.encode(FORMAT)
        # msgLength = len(message)
        # sendLength = str(msgLength).encode(FORMAT)
        # sendLength += b' ' * (HEADER - len(sendLength))
        # client.send(sendLength) 
        client.send(message)    #encapsulate this with a try except else, try(send), except(reconnect), else(pass)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect(ADDR)



theText = ""
textCopy = theText
flag = False

#Function to apply differnences to text 
def applyDiff(text , changes):
    enters=0
    letters=0
    print("Applying Diff => ", changes)
    x = list(changes.keys())
    y= list(changes.values())[0]
    if "delete" in x:
        enters = (y.count('\n'))
        letters= len(y) - enters
        dele =  y[0][1]+ len(y) -1
        text = text[:y[0][1]] + text[dele+1:]
        enters = -1* enters
        print(text)
    if "insert" in x:

        enters = (y.count('\n'))
        letters= len(y) - enters
        for i in y:
            text= text[:i[1]] + i[0] + text[i[1]:]
   
    return text,enters,letters

#Function to send the selected file name to server
def fileSelected(file, fileNames):
    
    for f in fileNames:
        if file == f[1]:
            newWindow.destroy()
            send("//"+str(f[0]))
            return
    
# Function to update the state from the recieved message
def update(recieved):
    global textCopy, theText,flag
    if  (recieved== "Message Recieved") | (recieved == "Pong!"):
        print("got: " + recieved)
    
    elif recieved[0]=='$':
        #Recieve File Text
        flag = True
        txt_edit.delete(1.0, tk.END)
        txt_edit.config(state=tk.NORMAL)
        btn_save.config(state=tk.NORMAL)

        text =recieved[1:]
        txt_edit.insert(tk.END, text)
        theText = text
        textCopy = theText
        

        flag = False
    elif is_json(recieved):
        flag =True
        i = txt_edit.index(tk.INSERT)
        i= i.split(".")
        txt_edit.delete(1.0, tk.END)
        diff = json.loads(recieved)
        print("[diff] = ",diff)

        textCopy,enters,letters = applyDiff(textCopy,diff)
        theText,enters,letters = applyDiff(theText,diff)

        lastIndex = (list(diff.values())[0])[-1][1]


        textCopy = theText
        txt_edit.insert(tk.END, theText)
        if lastIndex <= int(i[0])+int(i[1]):
            txt_edit.mark_set("insert", "%d.%d" % (int(i[0])+enters,int(i[1])+letters))
        else :
            txt_edit.mark_set("insert", "%d.%d" % (int(i[0]),int(i[1])))
        flag =False
        
        print("the text: ",theText)
        print("the textCopy: ",textCopy)
    
    elif recieved[:2] == "..":
        #Recieve list of file Names
        fileNames = json.loads(recieved[2:])
        print("fileNames",fileNames)
        names =[]
        for file in fileNames:
            names.append(file[1])
        global newWindow
        newWindow = tk.Toplevel(window)
        newWindow.title("New Window")
    
        newWindow.geometry("200x200")
    
        tk.Label(newWindow,text ="Choose a File").pack()

        variable = tk.StringVar(newWindow)
        variable.set(names[0])
        sel = ttk.Combobox(newWindow, textvariable=variable, values = names)
        sel.pack()
        B = tk.Button(newWindow, text="Select",command= lambda: fileSelected(sel.get(),fileNames)).pack()
    else:
        theText =recieved
        textCopy = theText
        flag =True
        txt_edit.delete(1.0, tk.END)
        txt_edit.insert(tk.END, theText)
        flag=False





#Function to check if string is json
def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True

#function to be called when open file button is clicked
def open_file():
    """Open a file for editing."""
    
    send("send list of files")
    txt_edit.config(state=tk.NORMAL)
    print("List of threads=>> ",len(threading.enumerate()))
    
    # if connected:
    #     thread = threading.Thread(name="o",target=recievingUpdates, args= ())
    #     thread.start()
    
#Function to be called when save file button is clicked.
#Saved text file will be saved in server side database.
def save_file():
    """Save the current file as a new file."""
    global flag

    send("_SAVE")
    flag = True
    txt_edit.delete(1.0, tk.END)
    txt_edit.config(state=tk.DISABLED)
    btn_save.config(state=tk.DISABLED)
    flag = False

    
#Class to handle Text area
class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        """A text widget that report on internal widget commands"""
        tk.Text.__init__(self, *args, **kwargs)
        self.comm=""
        # create a proxy for the underlying widget
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)

    def _proxy(self, command, *args):
            # avoid error when copying
            
        if command == 'get' and (args[0] == 'sel.first' and args[1] == 'sel.last') and not txt_edit.tag_ranges('sel'): return

        # avoid error when deleting
        if command == 'delete' and (args[0] == 'sel.first' and args[1] == 'sel.last') and not txt_edit.tag_ranges('sel'): return

        cmd = (self._orig, command) + args
        result = self.tk.call(cmd)
        

        if command in ("insert", "delete", "replace"):
            self.comm = command

            self.event_generate("<<TextModified>>")

        return result

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

#Function to be invoked when text area changed
def onModification(event):
    global theText, textCopy, flag
    if flag ==False:
        print("theText: ",theText)
        print("textCopy: " , textCopy)
        theText = event.widget.get("1.0", "end-1c")
        if not theText ==textCopy:
            
            updates = dict(diff(textCopy,theText))
            textCopy = theText
            st = json.dumps(updates)

            send(st)

    # print(repr(event.widget.get("1.0", "end-1c")))
    # print(txt_edit.index(tk.INSERT))
    # print(txt_edit.comm)
        
#Function to  recieve from server while connected
def recievingUpdates():
    ###
    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id
    def raise_exception(self):
        thread_id = self.get_id()
        resu = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if resu > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Failure in raising exception') 
    ###
    global connected, client
    client.settimeout(5.0)
    while connected:
        # msgLength = int(client.recv(HEADER).decode(FORMAT))
        # print(msgLength)
        try:
            msg = client.recv(1024).decode(FORMAT)
        except:
            try:
                client.shutdown(socket.SHUT_RDWR)
                client.close()
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            except:
                pass
            connected = False
        else:
            print("got this inside recv updates: " + msg)
            update(msg)

#Function called when closing
def on_closing():
    global connected, closTime
    send(DISCONNECT_MSG)
    connected =False
    closTime = True
    window.destroy()
    

connThread = threading.Thread(target=initConnSup, daemon=True) # thread that handles connection and modifies global variable connected
connThread.start()

def on_enter(e):
    e.widget['background'] = "#075ea1"

def on_leave(e):
    e.widget['background'] = 'SystemButtonFace'

window = tk.Tk()
window.title("Team 28 - Client")
window.rowconfigure(0, minsize=600, weight=1)
window.columnconfigure(1, minsize=200, weight=1)
window.protocol("WM_DELETE_WINDOW", on_closing)
window.geometry("800x600")
window.minsize(800, 600)
window.resizable(True, True)

txt_edit = CustomText(window, bg="#242424", fg="#FFFFFF", insertbackground="#DDDDDD", wrap= tk.WORD, font=("Consolas", 13), state=tk.DISABLED)
txt_edit.bind("<<TextModified>>", onModification)
scrollb = tk.Scrollbar(window, orient=tk.VERTICAL)
txt_edit.config(yscrollcommand=scrollb.set)
scrollb.config(command=txt_edit.yview)

fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=10, bg="#000000")
lab_team = tk.Label (fr_buttons, text="Team 28", fg="#075ea1", bg="#000000", font=("Times New Roman", 25, tk.UNDERLINE))
lab_open = tk.Label (fr_buttons, bg="#000000",fg="#FFFFFF", text="Press to select a file to edit", font=("Times New Roman", 14))
lab_save = tk.Label (fr_buttons, bg="#000000",fg="#FFFFFF", text="Press to save a copy locally", font=("Times New Roman", 14))
pixelVirtual = tk.PhotoImage(width=1, height=1)
btn_save = tk.Button(fr_buttons, text="Save", command=save_file, width=90, compound="c", image=pixelVirtual, bg="#a6a6a6")
btn_open = tk.Button(fr_buttons, text="Open", command=open_file, width=90, compound="c", image=pixelVirtual, bg="#a6a6a6")

btn_save.bind("<Enter>", on_enter)
btn_save.bind("<Leave>", on_leave)

lab_team.grid(row=0,column=0, sticky="ew", padx=5, pady=10)
lab_open.grid(row=1,column=0, sticky="ew", padx=5, pady=(50,20))
btn_open.grid(row=2, column=0, padx=5, pady=10)
lab_save.grid(row=3,column=0, sticky="ew", padx=5, pady=(50,20))
btn_save.grid(row=4, column=0, padx=5, pady=0)

fr_buttons.grid(row=0, column=0, sticky="ns")
txt_edit.grid(row=0, column=1, sticky= "nsew")
scrollb.grid(row=0, column=2, sticky=tk.NS)



window.mainloop()

