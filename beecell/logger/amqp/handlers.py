import logging
import pika
import pickle
from pika.exceptions import AMQPError, AMQPConnectionError

class AMQPHandlerError(Exception): pass

class AMQPHandler(logging.Handler):
    """Provides a gateway between the Python logging system and the AMQP
    message queuing system.
    
    When use this handler exception like pika.exceptions.AMQPError could be raised.
    """
    
    logger = logging.getLogger("gibbon.util.amqp")
    
    def __init__(self, 
                 host="localhost",
                 port=5672,
                 userid="guest",
                 password="guest",
                 virtual_host="/",
                 exchange="pylogging",
                 level=logging.NOTSET):
        logging.Handler.__init__(self, level=level)
        
        self.connection = None
        self.channel = None
        self.host = host
        self.port = port
        self.userid = userid
        self.password = password
        self.virtual_host = virtual_host
        self.exchange = exchange

    def _reconnect(self):
        """Reconnect to the AMQP portal2 if needed.

        After closing the connections to make sure things are cleaned up,
        we reconnect to the AMQP portal2 and reinstantiate the exchange. This
        makes sure that we always have the exchange."""
        # First, we need to clean up any residual connections
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()

        credentials = pika.PlainCredentials(self.userid, self.password)
        parameters = pika.ConnectionParameters(self.host,
                                               self.port, 
                                               self.virtual_host, 
                                               credentials,
                                               heartbeat_interval=30,
                                               connection_attempts=5,
                                               retry_delay=2,
                                               socket_timeout=30)
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        # Declare the exchange. This will simply NOOP if the exchange already exists.
        self.channel.exchange_declare(exchange=self.exchange, type='topic')
        self.channel.confirm_delivery()

    def emit(self, record):
        """Send the log message to the AMQP exchange.

        After making sure we are connected, we format the message and send it.
        The routing key is defined as the logger_name.levelname. This means that
        for example, if you do ``logging.getLogger("test")``, then issue a DEBUG
        message that the routing key will be ``test.DEBUG``."""
        try:
            '''
            if not (self.connection and self.channel):
                self._reconnect()
    
            msg = self.format(record)
            data = pickle.dumps(msg)
            routing_key = record.name
            res = self.channel.basic_publish(exchange=self.exchange,
                                             routing_key=routing_key,
                                             mandatory=True,
                                             #immediate=True,
                                             body=data)
            '''
            credentials = pika.PlainCredentials(self.userid, self.password)
            parameters = pika.ConnectionParameters(self.host,
                                                   self.port, 
                                                   self.virtual_host, 
                                                   credentials)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            self.channel.exchange_declare(exchange=self.exchange, type='topic')
            self.channel.confirm_delivery()
            msg = self.format(record)
            data = pickle.dumps(msg)
            routing_key = record.name
            res = self.channel.basic_publish(exchange=self.exchange,
                                             routing_key=routing_key,
                                             mandatory=True,
                                             #immediate=True,
                                             body=data)
            self.channel.close()
            self.connection.close()            
            
        except AMQPConnectionError as ex:
            err = 'Connection to amqp portal2 %s:%s can not be established' % (
                  self.host, self.port)
            self.logger.error(err)
            raise AMQPHandlerError(err)
        except AMQPError as ex:
            self.logger.error(ex)
            raise AMQPHandlerError(ex)

        if not res:
            err = 'Message "%s" can not be delivered to exchange "%s"' % (
                  msg, self.exchange)
            self.logger.error(err)
            raise AMQPHandlerError(err)
        else:
            self.logger.debug('Message "%s" is delivered to exchange "%s"  with routing key "%s"' % (
                              msg, self.exchange, routing_key))            
            