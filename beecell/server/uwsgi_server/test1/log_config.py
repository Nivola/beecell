'''
Created on Mar 10, 2013

@author: io
'''
import logging
from gibbon.logger.config import setup_file_handler
from gibbon.util.server.wsgi_server.test1.varaibles import serverLogFileName

# create an istance of portal2 logger
loggingLevel = logging.DEBUG
severLogger = logging.getLogger('test1')
severLogger.setLevel(loggingLevel)
# run function to configure handler for serer logger
'''
host = 'localhost'
port = logging.handlers.DEFAULT_TCP_LOGGING_PORT
setup_socket_handler(severLogger, loggingLevel, host, port)
'''
setup_file_handler(severLogger, loggingLevel, serverLogFileName)