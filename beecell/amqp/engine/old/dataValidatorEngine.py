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
from smart.amqp.dao.rawdata import RawDataDAO
from smart.db.dao.sensor import GenericSensorDAO
import pymongo

class DataValidator(SimpleTCPServer):
  '''
  '''
  service_exporter = []
  path = os.path.dirname(__file__)
  mqConnection = None
  serviceContext = None
  consumerThread = None
  
  dbHost = None
  dbPort = None

  def __getSidFromBody__(self, body):
    '''
    get sensor id from messages in the queue
    '''
    return RawDataDAO.getSensorId(body)

  def __getSensorMetadata__(self, sid):
    '''
    get sensor metadata from db
    '''
    conn = pymongo.Connection(self.dbHost, self.dbPort)
    db = conn.smart    
    sensorDAO = GenericSensorDAO(db)
    sensorObj = sensorDAO.getSensor(sid)
    conn.close()
    return sensorObj

  def __validateDataFromMessage__(self, sensorObj, sensor_datas):  
    # validate measure from sensor
    index = 0
    ress = []
    for item in sensorObj.getMeasures():
      data = sensor_datas['data'][index]
      res = item.validate(data)
      index += 1
      ress.append(res)
      self.debug('Sensor [%s] - Measure [%s, %s] - Data : %s --> Validation : %s' % (sensorObj.sid, item.oid, item.name, data, res))
    
    return ress

  def __Consumer_handler__(self, channel, method_frame, header_frame, body):
    '''
    '''
    # Receive the data in 3 frames from RabbitMQ
    '''
    self.debug("Basic.Deliver %s delivery-tag %i - Body: %s" % (
               header_frame.content_type,
               method_frame.delivery_tag,
               body))
    '''
    #channel.basic_ack(delivery_tag=method_frame.delivery_tag)
    
    sid = self.__getSidFromBody__(body)
    self.debug("Sensor id from message : %s" % sid)
    sensorObj = self.__getSensorMetadata__(sid)
    
    '''
    decode sensor data
    {'timestamp2': '1342623696061', 'timestamp1': '20120718-170136', 'data': ['39', '-47', '11458'], 'id': 'ABCDE_1'}    
    '''
    sensor_datas = sensorObj.decodeRawdata(body)
    self.debug('Current message  :%s' % sensor_datas)
    
    '''
    validate sensor datas
    '''
    ress = self.__validateDataFromMessage__(sensorObj, sensor_datas)
    
    '''
    send good data to validdata queue
    '''

    '''
    send worng data to wrongdata queue0cfhlmnops
    '''
    
    '''
    #uri = "PYRO:ValidationProcess1@%s:%s" % (self.host, self.pyroPort)
    #validationProcess1 = Pyro4.Proxy(uri)
    validationProcess1 = self.serviceContext.get_object("ValidationProcess1") 
    
    data = measure['data'][0]
    datas = [ 0., 0.3, 0.6, 0.9, 1.2, 1.5, 1.8]
    dmin = 0
    dmax = 100
    deltamax = 0.5
    self.debug(validationProcess1.isNull(data))
    self.debug(validationProcess1.fuoriScala(data, dmin, dmax))
    self.debug(validationProcess1.variazione(datas, deltamax))
    '''

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
      
      self.debug("Data validator STARTED")
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
  server = DataValidator(host, port, name)
  server.dbHost = dbHost
  server.dbPort = int(dbPort)
  server.startup()