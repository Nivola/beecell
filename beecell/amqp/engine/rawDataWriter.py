'''
Created on Jul 18, 2012

@author: io
'''
from smart.db.dao.rawdata import RawDataDAO
from smart.amqp.engine.abstract.pubSubConsumer import PubSubConsumerEngine
import pymongo
import time
import traceback
from smart import util

class RawDataWriterEngine(PubSubConsumerEngine):
  '''
  '''
  def __Consumer_handler__(self, channel, method, header, body):
    '''
    '''
    event = util.EventLogger(self.config.name)
    event.restartTimer()
    tid = util.transactionIdGenerator()
    
    try:
      '''
      self.debug("Basic.Deliver %s delivery-tag %i - Body: %s" % (
                 header.content_type,
                 method.delivery_tag,
                 body))
      '''
      
      # add new rawdata to db collection smart.rawdata
      dbHost = self.config.databaseConfig.host
      dbPort = self.config.databaseConfig.port
      conn = pymongo.Connection(dbHost, dbPort)
      self.logger.debug("Open db connection : %s" % conn)
      #self.debug("Open db connection : %s" % conn)
      db = conn.smart
      rawdataDAO = RawDataDAO(db)
      oid = rawdataDAO.addRawData(body)
      conn.close()
      self.logger.debug("Close db connection : %s" % conn)
      self.logger.debug('Store rawdata : %s' % oid)
      event.generate(tid, 'OK', 'Store rawdata : %s' % oid)
      
      # send data to validator engine
      validationQueueClient = self.serviceContext.get_object("validationQueueClient")
      validationQueueClient.sendMessage(body, tid)
      self.logger.debug('Send data : %s to queue' % body)
      
      event.generate(tid, 'OK', 'Send data : %s to queue' % body)
    except Exception as ex:
      self.logger.error(traceback.format_exc())
      event.generate(tid, 'KO', ex)