'''
Created on Nov 14, 2012

@author: io
'''
import concurrence
import threading
from concurrence import dispatch, Tasklet
from concurrence.io import BufferedStream, Socket
import random
import string
import os

def transactionIdGenerator(length = 20):
  '''
  Generate random string to use as transaction id
  return : random string
  '''
  chars = string.ascii_letters + string.digits
  random.seed = (os.urandom(1024)) 
  return ''.join(random.choice(chars) for i in range(length))

def handler(client_socket):
    """writes the familiar greeting to client"""
    cur_thread = threading.current_thread()
    stream = BufferedStream(client_socket)
    writer = stream.writer    
    writer.write_bytes("HTTP/1.0 200 OK\r\n")
    writer.write_bytes("Content-Length: 12\r\n")    
    writer.write_bytes("\r\n")
    writer.write_bytes("[%s:%s] - " % (cur_thread, Tasklet.current()))
    writer.flush()
    stream.close()
       
def server():
    """accepts connections on a socket, and dispatches
    new tasks for handling the incoming requests"""
    server_socket = Socket.new()
    server_socket.bind(('localhost', 8000))
    server_socket.listen()

    while True:
        #taskid = transactionIdGenerator(5)
        taskid = 1
        client_socket = server_socket.accept()
        Tasklet.new(handler, name = 'task-%s' % taskid)(client_socket)

if __name__ == '__main__':
    dispatch(server)