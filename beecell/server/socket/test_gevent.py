'''
Created on Nov 14, 2012

@author: io
'''
#!/usr/bin/env python
"""Simple portal2 that listens on port 6000 and echos back every input to the client.

Connect to it with:
telnet localhost 6000

Terminate the connection by terminating telnet (typically Ctrl-] and then 'quit').
"""
from gevent.server import StreamServer
import gevent
import threading
import time

# this handler will be run for each incoming connection in a dedicated greenlet
def handler(socket, address):
    cur_thread = threading.current_thread()
    
    print ('[%s:%s] - New connection from :%s' % (cur_thread, gevent.getcurrent(), address))
    socket.send("HTTP/1.0 200 OK\r\n")
    socket.send("Content-Length: 12\r\n")    
    socket.send("\r\n")
    gevent.sleep(1)
    socket.send("[%s:%s] - " % (cur_thread, gevent.getcurrent()))
    #socket.sendall

if __name__ == '__main__':
    # to make the portal2 use SSL, pass certfile and keyfile arguments to the constructor
    print ("[%s:%s] - " % (threading.current_thread(), gevent.getcurrent()))
    server = StreamServer(('localhost', 8000), handler)
    # to start the portal2 asynchronously, use its start() method;
    # we use blocking serve_forever() here because we have no other jobs
    print ('Starting echo portal2 on port 8000')
    print ("[%s:%s] - " % (threading.current_thread(), gevent.getcurrent()))
    server.serve_forever()


