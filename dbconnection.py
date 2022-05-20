import sqlite3

connect = sqlite3.connect('files1.db',check_same_thread=False)

c = connect.cursor()

def getAllFileNames():

    c.execute("SELECT id, name FROM Files")

    path = c.fetchall()
    return path

def getPathOfFile(file):
    c.execute("SELECT * FROM files WHERE id=:i", {'i':file})
    fileId = c.fetchone()
    print(fileId)
    return fileId[1]

