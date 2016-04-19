'''
Created on Jul 19, 2012

@author: io
'''
import SocketServer, threading
import logging
import multiprocessing
from smart import util
from springpython.config import XMLConfig
from springpython.context import ApplicationContext

class SimpleTCPServer(SocketServer.TCPServer):
    '''
    '''
    logger = logging.getLogger("smart.portal2.SimpleTCPServer")
    #event = logging.getLogger("event")
    #event = None
    
    poll_interval = None
    mainProcess = None
    mainThread = None
    adminThread = None  
    serviceContext = None
    config = None
    
    #############################################################################
    # RequestHandler
    #############################################################################  
    class RequestHandler(SocketServer.BaseRequestHandler):
        '''
        '''
        def handle(self):
            msg = self.request.recv(1024)
            self.server.logger.debug("Command received : %s" % (msg))
            '''
            if msg == 'start':
              self.request.sendall("Server %s start in progress\n" % self.portal2.name)
              self.portal2.logger.logger.debug("Server %s start in progress" % self.portal2.name)
              self.portal2.start(self.request)
            '''
            if msg == 'status':
                #elf.request.sendall("Server %s status\n" % self.portal2.name)
                self.server.__status__(self.request)
              
            elif msg == 'shutdown':
                stop_thread = threading.Thread(target=self.server.__shutdown__,
                                                args = [],
                                                name = "AdminThread-2")
                stop_thread.daemon = True
                stop_thread.start()
                self.request.sendall("Server '%s' is stopped" % self.server.config.name)
            else:    
                self.server.process(msg, self.request)
    
    #############################################################################
    # AdminThread
    #############################################################################
    class AdminThread(threading.Thread):
        '''
        '''
        def __init__(self, server):
            threading.Thread.__init__(self, group=None, target=None, name=None, args=(), kwargs={})
            self.server = server
            self.name = "AdminThread-1"
        
        def run(self):
            threading.Thread.run(self)
            self.server.startup()
            self.server.logger.debug("Admin Server started on %s:%s" % (self.server.config.host, self.server.config.port))
            self.server.serve_forever()
            self.server.logger.debug("Admin Server stopped on %s:%s" % (self.server.config.host, self.server.config.port))
            self.server.logger.debug("Server '%s' is stopped" % self.server.config.name)
    
    #############################################################################
    # Class methods
    #############################################################################  
    def __init__(self, configFile):
        self.allow_reuse_address = True
        
        self.serviceContext = ApplicationContext(XMLConfig(configFile))
        self.config = self.serviceContext.get_object("mainConfiguration")
        
        SocketServer.TCPServer.__init__(self, (self.config.host, self.config.port), self.RequestHandler)
        
        self.poll_interval = 0.5
        self.mainProcess = multiprocessing.current_process()
        self.mainThread = threading.current_thread()    
        self.adminThread = None
    
        '''
        def logEvent(self, tid, status, msg, elapsed):
          self.event.info("%s - %s:%s - %s - %s - %s" % (self.config.name,
                                                         self.mainProcess.name,
                                                         threading.current_thread().name, 
                                                         tid,
                                                         status,
                                                         msg,
                                                         elapsed))
        '''
    
    def serve_forever(self, poll_interval=0.5):
        #self.start()  
        SocketServer.TCPServer.serve_forever(self, poll_interval)
    
    def start(self):
        self.logger.debug("Starting portal2 '%s'" % self.config.name)
        self.adminThread = self.AdminThread(self)
        #self.adminThread.daemon = True
        #self.logger.debug("Admin thread: %s" % self.adminThread)
        self.adminThread.start()
      
    def __shutdown__(self):
        self.logger.debug("Stopping portal2 '%s'" % self.config.name)
        self.shutdown()
        #SocketServer.TCPServer.server_close(self)
        SocketServer.TCPServer.shutdown(self)
        #SocketServer.TCPServer.server_close(self)
        #self.adminThtread.join()
        #del self.adminThtread
    
    def __status__(self, req):
        """
        should be overridden
        return - 
        """
        req.sendall('Main process : %s - %s\n' % (self.mainProcess.name, self.mainProcess.pid))
        req.sendall('Main thread : %s - %s\n' % (self.mainThread.name, self.mainThread.ident))
        req.sendall('Active threads count : %s\n' % threading.active_count())
        req.sendall('Active threads:\n')
        req.sendall('\tname\t\tid\t\tdaemon\talive\n')
        for item in threading.enumerate():
          req.sendall('\t%s\t%s\t%s\t%s\n' % (item.name, item.ident, item.isDaemon(), item.isAlive()))
        req.sendall('Internal services status:\n')
        self.status()
    
    def startup(self):
        """
        should be overridden
        return - if returns a not None object, it will be sent back 
                 to the client.
        """
        raise NotImplemented
    
    def shutdown(self):
        """
        should be overridden
        return - if returns a not None object, it will be sent back 
                 to the client.
        """
        raise NotImplemented
    
    def status(self, req):
        """
        should be overridden
        process a message
        msg    - string containing a received message
        return - if returns a not None object, it will be sent back 
                 to the client.
        """
        raise NotImplemented
    
    def process(self, msg, req):
        """
        should be overridden
        process a message
        msg    - string containing a received message
        return - if returns a not None object, it will be sent back 
                 to the client.
        """
        raise NotImplemented
    
    class ThreadedTCPServer(SimpleTCPServer, SocketServer.TCPServer):
        '''
        '''
        def __init__(self, (host, port), RequestHandler):
            SimpleTCPServer.__init__(self, (host, port), RequestHandler)
        
        def serve_forever(self, poll_interval=0.5):
            '''
            self.mainThtread = threading.Thread(target=TCPServer.serve_forever,
                                                args = [self, self.poll_interval],
                                                name = "PyServer-" + self.name)
            self.logger.logger.debug("Main thread: %s" % self.mainThtread)
            #self.mainThtread.daemon = True
            self.mainThtread.start()
            '''
            SimpleTCPServer.serve_forever(self, poll_interval) 