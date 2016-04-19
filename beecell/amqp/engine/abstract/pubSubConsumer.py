'''
Created on Jul 18, 2012

@author: io
'''
from smart.server.simpleTcpServer import SimpleTCPServer
from pika.adapters import SelectConnection
import threading
import traceback

class PubSubConsumerEngine(SimpleTCPServer):
  '''
  '''
  
  #############################################################################
  # AdminThread
  #############################################################################
  class AmqpThread(threading.Thread):
    '''
    '''
    channel = None
    
    def __init__(self, server, num):
      threading.Thread.__init__(self, group=None, target=None, name=None, args=(), kwargs={})
      self.server = server
      self.num = str(num)
      self.name = "AmqpThread-" + self.num
    
    # Step #2
    def on_connected(self, connection):
      """Called when we are fully connected to RabbitMQ"""
      # Open a channel
      connection.channel(self.on_channel_open)
      self.server.logger.debug("amqp connection : %s" % self.server.mqConnection)
      
    # Step #3
    def on_channel_open(self, new_channel):
      """Called when our channel has opened"""
      # Open the channel
      self.channel = new_channel
      self.server.logger.debug("amqp channel : %s" % self.channel)  
  
      # Declare the exchange
      exchange = self.channel.exchange_declare(exchange=self.server.config.exchangeName, 
                                               type='fanout', 
                                               passive=False, 
                                               durable=True, 
                                               auto_delete=False, 
                                               internal=False, 
                                               nowait=False, 
                                               arguments={}, 
                                               callback=self.on_exchange_declared)

    # Step #4
    def on_exchange_declared(self, frame):      
      self.server.logger.debug("amqp exchange : %s" % frame)
  
      # Declare the queue
      #channel.queue_declare(queue="test", durable=True, exclusive=False, auto_delete=False)
      self.channel.queue_declare(durable=False, 
                                 exclusive=True, 
                                 auto_delete=False, 
                                 callback=self.on_queue_declared)
      
    # Step #5
    def on_queue_declared(self, frame):
      """Called when RabbitMQ has told us our Queue has been declared, frame is the response from RabbitMQ"""
      queue_name = frame.method.queue
      self.server.logger.debug("amqp queue : %s" % frame)
      
      self.channel.queue_bind(exchange=self.server.config.exchangeName, queue=queue_name)
  
      # We're stuck looping here since this is a blocking adapter
      self.channel.basic_consume(self.server.__Consumer_handler__, queue=queue_name, no_ack=True)
    
    def run(self):
      """ Run thread"""
      threading.Thread.run(self)
      try:
        # get amqp connection params
        #self.mqConnection = self.serviceContext.get_object("mqConnection")
        parameters = self.server.serviceContext.get_object("amqpServer_connection_pars")
  
        # Step #1: Connect to RabbitMQ
        self.server.mqConnection = SelectConnection(parameters, self.on_connected)
        self.server.mqConnection.ioloop.start()
        #channel.start_consuming()
      except Exception as ex:
        # Gracefully close the connection
        if self.server.mqConnection != None:
          self.server.mqConnection.close()
        # Loop until we're fully closed, will stop on its own
        #connection.ioloop.start()
        self.server.logger.error(traceback.format_exc())
  
  
  def __init__(self, configFile):
    '''
    '''   
    SimpleTCPServer.__init__(self, configFile)
    self.mqConnection = None
    self.consumerThreads = []

  # Step #6
  def __Consumer_handler__(self, channel, method, header, body):
    '''
    '''
    self.logger.debug("Basic.Deliver %s delivery-tag %i - Body: %s" % (
               header.content_type,
               method.delivery_tag,
               body))

  def __Consumer_start__(self):
    '''
    '''   
    try:
      # get amqp connection params
      self.mqConnection = self.serviceContext.get_object("mqConnection")

      channel = self.mqConnection.channel()

      # Declare the exchange
      exchange = channel.exchange_declare(exchange=self.config.exchangeName, type='fanout', passive=False, durable=True, auto_delete=False, internal=False, nowait=False, arguments={})
  
      # Declare the queue
      #channel.queue_declare(queue="test", durable=True, exclusive=False, auto_delete=False)
      result = channel.queue_declare(durable=False, exclusive=True, auto_delete=False)
      queue_name = result.method.queue
      channel.queue_bind(exchange=self.config.exchangeName, queue=queue_name)
  
      # We're stuck looping here since this is a blocking adapter
      channel.basic_consume(self.__Consumer_handler__, queue=queue_name, no_ack=True)
      
      self.logger.debug("amqp connection : %s" % self.mqConnection)
      self.logger.debug("amqp channel : %s" % channel)
      self.logger.debug("amqp exchange : %s" % exchange)
      self.logger.debug("amqp queue : %s" % result)

      channel.start_consuming()
    except Exception as ex:
      # Gracefully close the connection
      if self.mqConnection != None:
        self.mqConnection.close()
      # Loop until we're fully closed, will stop on its own
      #connection.ioloop.start()
      self.logger.error(traceback.format_exc())

  def startup(self):
    '''
    '''
    '''
    self.consumerThread = threading.Thread(target=self.__Consumer_start__,
                                           args = [],
                                           name = "AmqpThread-1")
    '''
    self.consumerThread = self.AmqpThread(self, 0)  
    self.consumerThread.daemon = True
    self.consumerThread.start()
    self.logger.debug("Amqp consumer is started")

  def shutdown(self):
    '''
    '''
    if self.mqConnection != None:
      self.mqConnection.ioloop.stop()
      self.mqConnection.close()
    del self.consumerThread

  def status(self, req):
    SimpleTCPServer.status(self, req)
    if self.mqConnection != None:
      req.sendall(" amqp connection : %s" % self.mqConnection)
    else:
      req.sendall(' Consumer is down\n')

  def process(self, msg, req):
    if msg == 'amqp_test':
      pass
    else:    
      pass