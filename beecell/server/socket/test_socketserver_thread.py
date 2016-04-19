'''
Created on Nov 14, 2012

@author: io
'''
import socket
import threading
import SocketServer

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

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    # Ctrl-C will cleanly kill all spawned threads
    daemon_threads = True
    # much faster rebinding
    allow_reuse_address = True

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

    server_obj = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
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
    