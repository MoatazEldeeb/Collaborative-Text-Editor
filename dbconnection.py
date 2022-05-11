import sqlite3

connect = sqlite3.connect('files.db',check_same_thread=False)

c = connect.cursor()

def getAllFileNames():

    c.execute("SELECT id, name FROM Files")

    path = c.fetchall()
    return path

def getPathOfFile(file):
    c.execute("SELECT * FROM Files WHERE id=:i", {'i':file})
    fileId = c.fetchone()
    print(fileId)
    return fileId[1]

# def getTextOfFile(file):

#     with open(file, "r") as input_file:
#         txt = input_file.read()
#     print(txt)