'''
Created on Jul 18, 2012

@author: io
'''
from smart.amqp.dao.rawdata import RawDataDAO
from smart.db.dao.sensor import GenericSensorDAO
from smart.db.dao.measureCollection import MeasureCollectionDAO
from smart.db.dto.measureData import MeasureData
from smart.amqp.engine.abstract.ThreadedWorker import ThreadedWorkerEngine
import pymongo
import pickle
import traceback
from smart import util

class DataValidatorEngine(ThreadedWorkerEngine):
  '''
  '''
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
      get sensor id from messages in the queue
      '''
      sid = RawDataDAO.getSensorId(body)    
      self.logger.debug("Sensor id from message : %s" % sid)
      
      '''
      get sensor metadata from db
      '''
      dbHost = self.config.databaseConfig.host
      dbPort = self.config.databaseConfig.port
      conn = pymongo.Connection(dbHost, dbPort)
      self.logger.debug("Open db connection : %s" % conn)
      db = conn.smart    
      sensorDAO = GenericSensorDAO(db, self.serviceContext)
      sensorObj = sensorDAO.getSensor(sid)
      self.logger.debug("Close db connection : %s" % conn)
      conn.close()
      self.logger.debug("Get sensor '%s' metadata from db" % sensorObj)    
      
      '''
      decode sensor data
      {'timestamp2': '1342623696061', 'timestamp1': '20120718-170136', 'data': ['39', '-47', '11458'], 'id': 'ABCDE_1'}    
      '''
      sensor_datas = sensorObj.decodeRawdata(body)
      self.logger.debug('Decode message :%s' % sensor_datas)
      event.generate(tid, 'OK', 'Decode message :%s' % sensor_datas)
      
      '''
      validate sensor datas
      '''
      # validate measure from sensor
      index = 0
      ress = []
      for item in sensorObj.getMeasures():
        measureId = item.oid
        data = sensor_datas['data'][measureId]
        res = item.validate(data)
        index += 1
        ress.append(res)
        self.logger.debug('Sensor [%s], Measure [%s, %s], Data : %s > Validation : %s' % (sensorObj.sid, item.oid, item.name, data, res))
        event.generate(tid, 'OK', 'Sensor [%s], Measure [%s, %s], Data : %s > Validation : %s' % (sensorObj.sid, item.oid, item.name, data, res))
      
      '''
      correct sensor datas
      '''      
      
      '''
      send good data to admindataq queue
      '''
      index = 0
      for item in sensorObj.getMeasures():
        measureId = item.oid
        
        # get measure collectionId
        conn = pymongo.Connection(dbHost, dbPort)
        self.logger.debug("Open db connection : %s" % conn)
        db = conn.smart    
        collectionDAO = MeasureCollectionDAO(db, self.serviceContext)
        cid = collectionDAO.getCollectionByMeasure(sid, measureId).oid
        self.logger.debug("Close db connection : %s" % conn)
        conn.close()
        self.logger.debug("Measure collection id : %s" % cid)         
        
        # create MeasureData DTO
        data = sensor_datas['data'][measureId]
        timestamp = sensor_datas['timestamp']
        measureData = MeasureData(None, cid, timestamp, data)
        
        # serialize data
        measureDataSerial = pickle.dumps(measureData)
        
        # send measureData to admindataq queue
        admindataQueueClient = self.serviceContext.get_object("AdmindataQueueClient")
        admindataQueueClient.sendMessage(measureDataSerial, tid)
        self.logger.debug('Send measure data to queue')
        event.generate(tid, 'OK', 'Send measure data to queue')

      channel.basic_ack(delivery_tag = method.delivery_tag)
    except Exception as ex:
      self.logger.error(traceback.format_exc())
      event.generate(tid, 'KO', ex) 