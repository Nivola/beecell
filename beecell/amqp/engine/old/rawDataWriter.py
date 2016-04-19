'''
Created on Jul 18, 2012

@author: io
'''
import logging
import os, sys
from springpython.config import XMLConfig
from springpython.context import ApplicationContext
from smart.server.simpleTcpServer import SimpleTCPServer
from springpython.remoting.pyro import PyroServiceExporter
import Pyro4
import threading
from smart.sensor import util
from smart.util import setupLogger
from smart.db.dao.rawdata import RawDataDAO
from smart.db.dao.sensor import GenericSensorDAO
import pymongo
import time

class RawDataWriter(SimpleTCPServer):
  '''
  '''
  service_exporter = []
  path = os.path.dirname(__file__)
  mqConnection = None
  serviceContext = None
  consumerThread = None
  
  dbHost = None
  dbPort = None

  def __Consumer_handler__(self, channel, method_frame, header_frame, body):
    '''
    '''
    # Receive the data in 3 frames from RabbitMQ
    start = time.time()
    self.debug("Basic.Deliver %s delivery-tag %i - Body: %s" % (
               header_frame.content_type,
               method_frame.delivery_tag,
               body))
    
    # add new rawdata to db collection smart.rawdata
    conn = pymongo.Connection(self.dbHost, self.dbPort)
    db = conn.smart
    rawdataDAO = RawDataDAO(db)
    oid = rawdataDAO.addRawData(body)
    conn.close()
    stop = time.time() - start
    self.debug('New rawdata record : %s [%s]' % (oid, stop))

  def __Consumer_start__(self):
    path = os.path.dirname(__file__)
    self.serviceContext = ApplicationContext(XMLConfig(path+"/dataValidator.xml"))
    self.mqConnection = self.serviceContext.get_object("mqConnection")    
    
    try:
      # Open the channel
      channel = self.mqConnection.channel()
  
      # Declare the exchange
      exchange = channel.exchange_declare(exchange='rawdata', type='fanout', passive=False, durable=True, auto_delete=False, internal=False, nowait=False, arguments={})
  
      # Declare the queue
      #channel.queue_declare(queue="test", durable=True, exclusive=False, auto_delete=False)
      result = channel.queue_declare(durable=False, exclusive=True, auto_delete=False)
      queue_name = result.method.queue
      channel.queue_bind(exchange='rawdata', queue=queue_name)
  
      # We're stuck looping here since this is a blocking adapter
      channel.basic_consume(self.__Consumer_handler__, queue=queue_name, no_ack=True)
      
      self.debug("Raw Data Writer STARTED")
      self.debug("amqp connection : %s" % self.mqConnection)
      self.debug("amqp channel : %s" % channel)
      self.debug("amqp exchange : %s" % exchange)
      self.debug("amqp queue : %s" % result)
      
      channel.start_consuming()
    except Exception as ex:
      # Gracefully close the connection
      self.mqConnection.close()
      # Loop until we're fully closed, will stop on its own
      #connection.ioloop.start()
      self.error(ex)

  def __Consumer_status__(self, req):
    if self.mqConnection != None:
      req.sendall(" amqp connection : %s" % self.mqConnection)
    else:
      req.sendall(' Consumer is down\n')

  def __Consumer_stop__(self):
    if self.mqConnection != None:
      self.mqConnection.close()

  def process(self, msg, req):
    if msg == 'amqp_start':
      self.consumerThread = threading.Thread(target=self.__Consumer_start__,
                                      args = [],
                                      name = "AmqpThread-1")
      self.consumerThread.daemon = True
      self.consumerThread.start()
      req.sendall(" Amqp consumer is started\n")
    elif msg == 'amqp_stop':
      self.__Consumer_stop__()
      del self.consumerThread
      req.sendall(" Amqp consumer  is stopped\n")
    elif msg == 'amqp_test':
      pass
    else:    
      pass

  def status(self, req):
    SimpleTCPServer.status(self, req)
    self.__Consumer_status__(req)

def main(syspath, host, port, name, dbHost, dbPort):
  logHandler = ["smart.server.SimpleTCPServer"] #, "springpython"
  setupLogger(logHandler)

  server = None

  # Create the server, binding to localhost on port 9999
  server = RawDataWriter(host, port, name)
  server.dbHost = dbHost
  server.dbPort = int(dbPort)
  server.startup()