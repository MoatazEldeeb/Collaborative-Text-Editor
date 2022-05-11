import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import difflib
from collections import defaultdict
import json
import dbconnection

theText = ""
textCopy = theText


def open_file():
    global window
    """Open a file for editing."""
    # [(1, 'test')]
    files = dbconnection.getAllFileNames()

    h = dbconnection.getPathOfFile(1)
    print(h)
    fileNames =[]
    for file in files:
        fileNames.append(file[1])

    newWindow = tk.Toplevel(window)
    newWindow.title("New Window")
 
    newWindow.geometry("200x200")
 
    tk.Label(newWindow,text ="Choose a File").pack()

    variable = tk.StringVar(newWindow)
    variable.set(fileNames[0])
    sel = ttk.Combobox(newWindow, textvariable=variable, values = fileNames)
    sel.pack()

    # B = tk.Button(newWindow, text="Select",command= fileSelected).pack()

    # for file in files:
    #     B = tk.Button(newWindow, text=file[1], width=50,).pack()

    # global theText, textCopy
    # filepath = askopenfilename(
    # filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    # )
    # if not filepath:
    #     return
    # txt_edit.delete(1.0, tk.END)
    # with open(filepath, "r") as input_file:
    #     text = input_file.read()
    #     txt_edit.insert(tk.END, text)
    #     theText = text
    #     textCopy = theText
    # window.title(f"Thecleverprogrammer - {filepath}")


    
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
    global theText, textCopy
    if theText:
        theText = event.widget.get("1.0", "end-1c")
        updates = dict(diff(textCopy,theText))
        textCopy = theText
        st = json.dumps(updates)
        print(updates)
       
        

        # pickled = pickle.dumps(updates)
        
    # print(repr(event.widget.get("1.0", "end-1c")))
    # print(txt_edit.index(tk.INSERT))
    # print(txt_edit.comm)



window = tk.Tk()
window.title("Thecleverprogrammer")
window.rowconfigure(0, minsize=800, weight=1)
window.columnconfigure(1, minsize=800, weight=1)
txt_edit = CustomText(window)
txt_edit.bind("<<TextModified>>", onModification)
fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
btn_open = tk.Button(fr_buttons, text="Open", command=open_file)
btn_save = tk.Button(fr_buttons, text="Save As...", command=save_file)
btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
btn_save.grid(row=1, column=0, sticky="ew", padx=5)
fr_buttons.grid(row=0, column=0, sticky="ns")
txt_edit.grid(row=0, column=1, sticky="nsew")
window.mainloop()