'''
Created on Jan 23, 2013

@author: darkbk
'''
import sys
import logging.handlers
#from .amqp.handlers import AMQPHandler
from celery.utils.log import ColorFormatter as CeleryColorFormatter
from celery.utils.term import colored

class CustomFormatter(logging.Formatter):
    def __init__(self, default):
        self._default_formatter = default
        
    def format(self, record):
        return self._default_formatter.format(record)
    
class ColorFormatter(CeleryColorFormatter):
    """Logging formatter that adds colors based on severity."""

    #: Loglevel -> Color mapping.
    COLORS = colored().names
    colors = {
        u'DEBUG': COLORS[u'blue'], 
        u'WARNING': COLORS[u'yellow'],
        u'WARN': COLORS[u'yellow'],
        u'ERROR': COLORS[u'red'], 
        u'CRITICAL': COLORS[u'magenta']
    }  

class LoggerHelper(object):
    '''
    @staticmethod
    def setup_amqp_logger(logger, logging_level, amqp_params):
        """Setup logger to an amqp exchange
        
        :param str amqp_params: The AMQP connection params. Dict like: 
                                {'host':'172.16.0.8', 'port':5672, 'vhost':'/', 
                                'user':'guest', 'pwd':'testlab', 
                                'exchange':'message', 'durable':False}
        :return: None
        """
        ch1 = AMQPHandler(host=amqp_params['host'],
                          port=amqp_params['port'], 
                          userid=amqp_params['user'],
                          password=amqp_params['pwd'],
                          virtual_host=amqp_params['vhost'],
                          exchange=amqp_params['exchange'],
                          level=logging_level)
        ch1.setLevel(logging_level)
        #Formatter = logging.Formatter("%(asctime)s|%(process)d:%(thread)d|%(message)s")
        Formatter = logging.Formatter("%(message)s")
        ch1.setFormatter(Formatter)
        logger.addHandler(ch1)
        logger.setLevel(logging_level)
        logger.propagate = False'''
    
    @staticmethod
    def setup_socket_handler(logger, logging_level, host, port):
        '''Setup logger 'portal2' to a socket portal2
        This logger requires first an active socket portal2
        '''
        #rootLogger = logging.getLogger('')
        #severLogger.setLevel(logging_level)
        socketHandler = logging.handlers.SocketHandler(host, port)
        # don't bother with a Formatter, since a socket handler sends the event as
        # an unfrmtted pickle
        logger.addHandler(socketHandler)
        
        #severLogger.info('Started logger portal2')
        '''
        logger1.debug('Quick zephyrs blow, vexing daft Jim.')
        logger1.info('How quickly daft jumping zebras vex.')
        logger2.warning('Jail zesty vixen who grabbed pay from quack.')
        logger2.error('The five boxing wizards jump quickly.')
        '''
    
    @staticmethod
    def setup_simple_handler(logger, logging_level, frmt=None):
        if frmt is None:
            frmt = "[%(asctime)s: %(levelname)s/%(process)s:%(thread)s] " \
                   "%(name)s:%(funcName)s:%(lineno)d - %(message)s"
        ch1 = logging.StreamHandler(sys.stdout)
        ch1.setLevel(logging_level)
        Formatter = logging.Formatter(frmt)
        ch1.setFormatter(Formatter)
        logger.addHandler(ch1)
        logger.setLevel(logging_level)
        logger.propagate = False        
    
    @staticmethod
    def setup_file_handler(logger, logging_level, file_name, frmt=None):
        if frmt is None:
            frmt = "[%(asctime)s: %(levelname)s/%(process)s:%(thread)s] " \
                   "%(name)s:%(funcName)s:%(lineno)d - %(message)s"
        ch1 = logging.FileHandler(file_name, mode='a')
        ch1.setLevel(logging_level)
        Formatter = logging.Formatter(frmt)
        ch1.setFormatter(Formatter)
        logger.addHandler(ch1)
        logger.setLevel(logging_level)
        logger.propagate = False
        
    @staticmethod
    def setup_rotatingfile_handler(logger, logging_level, file_name, 
                                   maxBytes=104857600, backupCount=10, 
                                   frmt=None):
        if frmt is None:
            frmt = "[%(asctime)s: %(levelname)s/%(process)s:%(thread)s] " \
                   "%(name)s:%(funcName)s:%(lineno)d - %(message)s"
        ch1 = logging.handlers.RotatingFileHandler(file_name, mode='a', 
                                                   maxBytes=maxBytes, 
                                                   backupCount=backupCount)
        ch1.setLevel(logging_level)
        Formatter = logging.Formatter(frmt)
        ch1.setFormatter(Formatter)
        logger.addHandler(ch1)
        logger.setLevel(logging_level)
        logger.propagate = False

    @staticmethod
    def setup_timedrotatingfile_handler(logger, logging_level, file_name, 
                                        when='D', interval=1, backupCount=10, 
                                        frmt=None):
        if frmt is None:
            frmt = "[%(asctime)s: %(levelname)s/%(process)s:%(thread)s] " \
                   "%(name)s:%(funcName)s:%(lineno)d - %(message)s"
        ch1 = logging.handlers.TimedRotatingFileHandler(file_name,
                                                        when=when, 
                                                        interval=interval,
                                                        backupCount=backupCount)
        ch1.setLevel(logging_level)
        Formatter = logging.Formatter(frmt)
        ch1.setFormatter(Formatter)
        logger.addHandler(ch1)
        logger.setLevel(logging_level)
        logger.propagate = False
        
    #
    # new methods. Correct the problem with loggers that use the same file. Use 
    # rotatingfile_handler passing all the logger.
    #
    @staticmethod
    def memory_handler(loggers, logging_level, target, frmt=None,
                       formatter=ColorFormatter):
        if frmt is None:
            frmt = "[%(asctime)s: %(levelname)s/%(process)s:%(thread)s] " \
                   "%(name)s:%(funcName)s:%(lineno)d - %(message)s"

        handler = logging.handlers.MemoryHandler(capacity=1000, target=target)
        handler.setLevel(logging_level)
        if formatter is None:
            handler.setFormatter(logging.Formatter(frmt))
        else:
            handler.setFormatter(formatter(frmt))
            
        for logger in loggers:
            #Formatter = logging.Formatter(frmt)
            #ch1.setFormatter(Formatter)
            logger.addHandler(handler)
            logger.setLevel(logging_level)
            logger.propagate = False
    
    @staticmethod
    def simple_handler(loggers, logging_level, frmt=None, formatter=ColorFormatter):
        if frmt is None:
            frmt = "[%(asctime)s: %(levelname)s/%(process)s:%(thread)s] " \
                   "%(name)s:%(funcName)s:%(lineno)d - %(message)s"

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging_level)
        if formatter is None:
            handler.setFormatter(logging.Formatter(frmt))
        else:
            handler.setFormatter(formatter(frmt))

        for logger in loggers:
            #Formatter = logging.Formatter(frmt)
            #ch1.setFormatter(Formatter)
            logger.addHandler(handler)
            logger.setLevel(logging_level)
            logger.propagate = False  
    
    @staticmethod
    def rotatingfile_handler(loggers, logging_level, file_name, 
                             maxBytes=104857600, backupCount=10, frmt=None,
                             formatter=ColorFormatter):
        if frmt is None:
            frmt = "[%(asctime)s: %(levelname)s/%(process)s:%(thread)s] " \
                   "%(name)s:%(funcName)s:%(lineno)d - %(message)s"
        handler = logging.handlers.RotatingFileHandler(file_name, mode=u'a', 
                                                       maxBytes=maxBytes, 
                                                       backupCount=backupCount)
        handler.setLevel(logging_level)
        if formatter is None:
            handler.setFormatter(logging.Formatter(frmt))
        else:
            handler.setFormatter(formatter(frmt))
        
        for logger in loggers:
            #logger.setFormatter(CustomFormatter)
            logger.addHandler(handler)
            logger.setLevel(logging_level)
            logger.propagate = False
            
    @staticmethod
    def file_handler(loggers, logging_level, file_name, frmt=None, 
                     formatter=ColorFormatter):
        if frmt is None:
            frmt = "[%(asctime)s: %(levelname)s/%(process)s:%(thread)s] " \
                   "%(name)s:%(funcName)s:%(lineno)d - %(message)s"
        handler = logging.FileHandler(file_name, mode=u'a')
        handler.setLevel(logging_level)
        if formatter is None:
            handler.setFormatter(logging.Formatter(frmt))
        else:
            handler.setFormatter(formatter(frmt))        
        
        for logger in loggers:
            #logger.setFormatter(CustomFormatter)
            logger.addHandler(handler)
            logger.setLevel(logging_level)
            logger.propagate = False