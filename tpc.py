import socket, pickle

class ProcessData:
    data = ""
    upd = True/False
    

HOST = '172.20.10.8'
PORT = 50007
# Create a socket connection.
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# Create an instance of ProcessData() to send to server.
variable = ProcessData()
# Pickle the object and send it to the server
data_string = pickle.dumps(variable)
s.send(data_string)

s.close()
print ('Data Sent to Server')