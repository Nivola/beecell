'''
Created on Aug 31, 2012

@author: io
'''
class SimpleTcpServerConfig(object):
  '''
  '''
  name = None
  host = None
  port = None
  threadNum = None
  databaseConfig = None
  
  def __init__(self, name, host, port):
    self.name = name
    self.host = host
    self.port = int(port)
    
  def setThreadsNum(self, threadsNum):
    self.threadsNum = int(threadsNum)

  def getThreadsNum(self):
    return self.threadsNum

  def setDatabaseConfig(self, dbConfig):
    self.databaseConfig = dbConfig

  def getDatabaseConfig(self):
    return self.databaseConfig
 