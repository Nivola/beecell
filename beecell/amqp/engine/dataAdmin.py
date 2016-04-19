'''
Created on Jul 18, 2012

@author: io
'''
from smart.db.dao.measureCollection import MeasureCollectionDAO
from smart.amqp.engine.abstract.ThreadedWorker import ThreadedWorkerEngine
import pymongo
import pickle
import traceback
from smart import util

class DataAdminEngine(ThreadedWorkerEngine):
  '''
  '''
  dashboardLogger = util.DashboardLogger()
  
  def __Consumer_handler__(self, channel, method, header, body):
    '''
    '''
    event = util.EventLogger(self.config.name)
    event.restartTimer()
    #tid = util.transactionIdGenerator()
      
    try:
      ''' get correlation_id '''
      tid = header.correlation_id
      
      ''' get message '''
      self.logger.debug("Get message : %s" % body)
      
      '''
      Deserialize data from message body
      '''
      measureData = pickle.loads(body)
      self.logger.debug("Deserialize data : %s" % measureData)
      
      '''
      Write data on db
      '''
      dbHost = self.config.databaseConfig.host
      dbPort = self.config.databaseConfig.port
      conn = pymongo.Connection(dbHost, dbPort)
      self.logger.debug("Open db connection : %s" % conn)
      db = conn.smart
      collectionDAO = MeasureCollectionDAO(db, self.serviceContext)
      oid = collectionDAO.addMeasureData(measureData)
      conn.close()
      self.logger.debug("Close db connection : %s" % conn)
      self.logger.debug('Store measure data : %s' % oid)
      event.generate(tid, 'OK', 'Store measure data : %s' % oid)
 
      ''' Send data to dashboard '''
      self.logger.debug("Send data to dashboard")
      self.dashboardLogger.sendData(str(measureData))
 
      channel.basic_ack(delivery_tag = method.delivery_tag)
      
    except Exception as ex:
      self.logger.error(traceback.format_exc())
      event.generate(tid, 'KO', ex)