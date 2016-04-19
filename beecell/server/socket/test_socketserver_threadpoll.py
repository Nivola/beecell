'''
Created on Nov 14, 2012

@author: io
'''
import socket
import threading
import SocketServer
from SocketServer import ThreadingMixIn
from Queue import Queue
import threading, socket


class ThreadPoolMixIn(ThreadingMixIn):
    '''
    use a thread pool instead of a new thread on every request
    code from : http://code.activestate.com/recipes/574454-thread-pool-mixin-class-for-use-with-socketservert/
    '''
    allow_reuse_address = True  # seems to fix socket.error on portal2 restart
    numThreads = None
    
    def __init__(self, numThreads): 
        ''' Sets up the threadPool and "fills" it with the threads. '''
        self.numThreads = numThreads
        
        self.requests = Queue(self.numThreads)
        
        for n in range(self.numThreads):
          t = threading.Thread(target = self.process_request_thread)
          t.setDaemon(True)
          t.start()

    def process_request(self, request, client_address): 
       ''' Simply collect requests and put them on the queue for the workers. ''' 
       self.requests.put((request, client_address))

    def process_request_thread(self): 
      ''' Obtains request and client_address from the queue instead of directly from a call '''

      # The thread starts and stays on this loop.
      # The method call hangs waiting until something is inserted into self.requests
      #  and .get() unblocks
      while True:
        ThreadingMixIn.process_request_thread(self, *self.requests.get())
        # http://docs.python.org/tut/node6.html#SECTION006740000000000000000

    '''    
    def handle_request(self):
        
        simply collect requests and put them on the queue for the workers.
        
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        if self.verify_request(request, client_address):
            self.requests.put((request, client_address))
    '''

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024)
        cur_thread = threading.current_thread()
        #response = "{}: {}".format(cur_thread.name, data)
        response = []
        response.append("HTTP/1.0 200 OK\r\n")
        response.append("Content-Length: 12\r\n")    
        response.append("\r\n")
        response.append("[%s] - " % (cur_thread))        
        self.request.sendall(''.join(response))

class ThreadedTCPServer(ThreadPoolMixIn, SocketServer.TCPServer):
    pass
  
  
class ThreadingPoolTCPServer(ThreadPoolMixIn, SocketServer.TCPServer): 
    """Calls the __init__ from both super."""
    def __init__(self, server_address, RequestHandlerClass, numThreads, bind_and_activate=True): 
        ThreadPoolMixIn.__init__(self, numThreads)
        SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)


def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()

def server():
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 8000
    numThreads = 100

    server_obj = ThreadingPoolTCPServer((HOST, PORT), ThreadedTCPRequestHandler, numThreads)
    ip, port = server_obj.server_address

    # Start a thread with the portal2 -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server_obj.serve_forever)
    # Exit the portal2 thread when the main thread terminates
    #server_thread.daemon = True
    server_thread.start()
    
    print "Server loop running in thread:", server_thread.name
    
    return server_obj

if __name__ == "__main__":
    server_obj = server()
    '''
    ip, port = "localhost", 8000
    client(ip, port, "Hello World 1")
    client(ip, port, "Hello World 2")
    client(ip, port, "Hello World 3")
    client(ip, port, "Hello World 3")
    client(ip, port, "Hello World 3")
    client(ip, port, "Hello World 3")
    client(ip, port, "Hello World 3")
    '''
    #server_obj.shutdown()
    