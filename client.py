from distutils import text_file
import socket
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MSG = '!disconnect'
SERVER = "192.168.1.104"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

theText = ""
textCopy = ""

def send(msg):
    message = msg.encode(FORMAT)
    msgLength = len(message)
    sendLength = str(msgLength).encode(FORMAT)
    sendLength += b' ' * (HEADER - len(sendLength))
    client.send(sendLength)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

def open_file():
    """Open a file for editing."""
    filepath = askopenfilename(
    filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if not filepath:
        return
    txt_edit.delete(1.0, tk.END)
    with open(filepath, "r") as input_file:
        text = input_file.read()
        theText = text
        textCopy = theText
        txt_edit.insert(tk.END, text)
    window.title(f"Thecleverprogrammer - {filepath}")
    send(filepath)
    txt_edit.config(state=tk.NORMAL)
    
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

def onModification(event):
    send(event.widget.get("1.0", "end-1c"))
    send(txt_edit.index(tk.INSERT))
    send(txt_edit.comm)

def on_closing():
    send(DISCONNECT_MSG)
    window.destroy()
    

window = tk.Tk()
window.title("Thecleverprogrammer")
window.rowconfigure(0, minsize=800, weight=1)
window.columnconfigure(1, minsize=800, weight=1)
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
window.mainloop()

