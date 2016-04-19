'''
Created on Nov 15, 2012

@author: io
'''
import socket
import time

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()
        
if __name__ == "__main__":
    start = time.clock()
    ip, port = "localhost", 8000
    client(ip, port, "Hello World 1")
    client(ip, port, "Hello World 2")
    client(ip, port, "Hello World 3")
    client(ip, port, "Hello World 3")
    client(ip, port, "Hello World 3")
    client(ip, port, "Hello World 3")
    client(ip, port, "Hello World 3")
    stop = time.clock() - start
    print stop