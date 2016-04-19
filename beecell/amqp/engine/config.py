'''
Created on Jul 18, 2012

@author: io
'''
from smart.server.config import SimpleTcpServerConfig

class BaseConsumerConfig(SimpleTcpServerConfig):
  '''
  '''
  queueName = None
  exchangeName = None

  def setQueueName(self, queueName):
    self.queueName = queueName

  def getQueueName(self):
    return self.queueName
  
  def setExchangeName(self, exchangeName):
    self.exchangeName = exchangeName

  def getExchangeName(self):
    return self.exchangeName