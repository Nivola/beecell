'''
Created on Jul 18, 2012

@author: io
'''
from smart.server.simpleTcpServer import SimpleTCPServer
import threading
import traceback

class ThreadedWorkerEngine(SimpleTCPServer):
  '''
  '''
  mqConnection = None
  consumerThreads = None
  
  def __init__(self, configFile):
    '''
    '''
    SimpleTCPServer.__init__(self, configFile)
    self.mqConnection = None
    self.threadsNum = int(self.config.threadsNum)
    self.consumerThreads = []
    

  def __Consumer_handler__(self, channel, method_frame, header_frame, body):
    '''
    '''
    try:
      self.logger.debug("Basic.Deliver %s delivery-tag %i - Body: %s" % (
                 header_frame.content_type,
                 method_frame.delivery_tag,
                 body))
    except Exception as ex:
      self.logger.error(ex)

  def __Consumer_thread_start__(self):
    '''
    '''
    try:
      # get amqp connection
      self.mqConnection = self.serviceContext.get_object("mqConnection")

      # Open the channel
      channel = self.mqConnection.channel()
  
      # Declare the exchange
      #exchange = channel.exchange_declare(exchange='rawdata', type='fanout', passive=False, durable=True, auto_delete=False, internal=False, nowait=False, arguments={})
  
      # Declare the queue
      #channel.queue_declare(queue="test", durable=True, exclusive=False, auto_delete=False)
      queue = channel.queue_declare(queue=self.config.queueName, durable=True)

      #result = channel.queue_declare(durable=False, exclusive=True, auto_delete=False)
      #queue_name = result.method.queue
      #channel.queue_bind(exchange='rawdata', queue=queue_name)
  
      # We're stuck looping here since this is a blocking adapter
      channel.basic_qos(prefetch_count=1)
      #channel.basic_consume(self.__Consumer_handler__, queue=queue_name, no_ack=True)
      channel.basic_consume(self.__Consumer_handler__, queue=self.config.queueName)
      
      self.logger.debug(" amqp connection : %s" % self.mqConnection)
      self.logger.debug(" amqp channel : %s" % channel)
      #self.logger.debug(" amqp exchange : %s" % exchange)
      self.logger.debug(" amqp queue : %s" % queue)
      
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
    try:
      for i in range(0, self.threadsNum):
        consumerThreads = threading.Thread(target=self.__Consumer_thread_start__,
                                           args = [],
                                           name = "AmqpThread-%s" % i)
        self.consumerThreads.append(consumerThreads)
        consumerThreads.daemon = True
        consumerThreads.start()
        self.logger.debug("Amqp consumer thread[%s] is started" % i)
    except Exception as ex:
      self.logger.error(traceback.format_exc())

  def shutdown(self):
    '''
    '''
    if self.mqConnection != None:
      self.mqConnection.close()
    del self.consumerThreads

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