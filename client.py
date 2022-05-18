from collections import defaultdict
from distutils import text_file
import socket
import sys
import threading
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import difflib
import json

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MSG = '!disconnect'
SERVER = "172.20.10.3"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

theText = ""
textCopy = theText
flag = False

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

def fileSelected(file, fileNames):
    
    for f in fileNames:
        if file == f[1]:
            newWindow.destroy()
            send("//"+str(f[0]))
            return
    
def update(recieved):
    global textCopy, theText,flag
    if  recieved== "Message Recieved":
        print(recieved)
    
    elif recieved[0]=='$':
        #Recieve File Text
        flag = True
        txt_edit.delete(1.0, tk.END)
        txt_edit.config(state=tk.NORMAL)

        text =recieved[1:]
        txt_edit.insert(tk.END, text)
        theText = text
        textCopy = theText
        

        flag = False

    elif is_json(recieved):
        flag =True
        txt_edit.delete(1.0, tk.END)
        diff = json.loads(recieved)

        textCopy = applyDiff(textCopy,diff)
        theText = applyDiff(theText,diff)

        textCopy = theText
        
        txt_edit.insert(tk.END, theText)
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




def send(msg):
    message = msg.encode(FORMAT)
    msgLength = len(message)
    sendLength = str(msgLength).encode(FORMAT)
    sendLength += b' ' * (HEADER - len(sendLength))
    client.send(sendLength)
    client.send(message)


def sendd(msg):
    global textCopy, theText
    message = msg.encode(FORMAT)
    msgLength = len(message)
    sendLength = str(msgLength).encode(FORMAT)
    sendLength += b' ' * (HEADER - len(sendLength))
    client.send(sendLength)
    client.send(message)
    print("Waiting for acK")
    recieved = client.recv(2048).decode(FORMAT)
    print("acKed")
    
    if recieved[0]=='$':
        return recieved[1:]
    # if  recieved== "Message Recieved":
    #     print(recieved)
    

    # elif is_json(recieved):
    #     diff = json.loads(recieved)
    #     textCopy = applyDiff(textCopy,diff)
    #     theText = applyDiff(theText,diff)

def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True

def open_file():
    """Open a file for editing."""
    global theText,textCopy,flag
    # flag = True
    # filepath = askopenfilename(
    # filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    # )
    # if not filepath:
    #     return
    # txt_edit.delete(1.0, tk.END)
    # txt_edit.config(state=tk.NORMAL)
    
    send("send list of files")
    
    # text = sendd(filepath)
    thread = threading.Thread(target=recievingUpdates, args= ())
    thread.start()
    # text = input_file.read()
    # txt_edit.insert(tk.END, text)
    # theText = text
    # textCopy = theText
    # flag = False
    
    
    
    
def save_file():
    """Save the current file as a new file."""
    filepath = asksaveasfilename(
    defaultextension="txt",
    filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    with open(filepath, "w") as output_file:
        text = txt_edit.get(1.0, tk.END)
        output_file.write(text)
    window.title(f"Thecleverprogrammer - {filepath}")

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
        

def recievingUpdates():
    global connected
    
    while connected:
        msg = client.recv(2048).decode(FORMAT)
        print(msg)
        update(msg)



def on_closing():
    global connected
    send(DISCONNECT_MSG)
    connected =False
    window.destroy()
    

window = tk.Tk()
window.title("Thecleverprogrammer")
window.rowconfigure(0, minsize=300, weight=1)
window.columnconfigure(1, minsize=300, weight=1)
window.protocol("WM_DELETE_WINDOW", on_closing)

txt_edit = CustomText(window)
txt_edit.bind("<<TextModified>>", onModification)
txt_edit.config(state=tk.DISABLED)

fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
btn_open = tk.Button(fr_buttons, text="Open", command=open_file)
btn_save = tk.Button(fr_buttons, text="Save As...", command=save_file)
btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_save.grid(row=1, column=0, sticky="ew", padx=5)
fr_buttons.grid(row=0, column=0, sticky="ns")

txt_edit.grid(row=0, column=1, sticky="nsew")

connected =True


window.mainloop()
