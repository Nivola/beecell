'''
Created on Jul 18, 2012

@author: io
'''
import logging
import os
import pika
from springpython.config import XMLConfig
from springpython.context import ApplicationContext
from smart.sensor import util
#pika.log.setup(color=True)

def handle_delivery(channel, method_frame, header_frame, body):
  logger = logging.getLogger("dataValidator")
  
  # Receive the data in 3 frames from RabbitMQ
  logger.info("Basic.Deliver %s delivery-tag %i - Body: %s",
                header_frame.content_type,
                method_frame.delivery_tag,
                body)
  #channel.basic_ack(delivery_tag=method_frame.delivery_tag)
  global appContext
  
  # get sensor metadata class name
  sensorClass = util.simpleDetect(body)
  # create sensor metadata class
  sensor = sensorClass()
  # decode sensor data
  # {'timestamp2': '1342623696061', 'timestamp1': '20120718-170136', 'data': ['39', '-47', '11458'], 'id': 'ABCDE_1'}
  measure = sensor.decode(body)
  logger.info(measure)  
  
  validationProcess1 = appContext.get_object("ValidationProcess1")
  
  data = measure['data'][0]
  datas = [ 0., 0.3, 0.6, 0.9, 1.2, 1.5, 1.8]
  dmin = 0
  dmax = 100
  deltamax = 0.5
  logger.info(validationProcess1.inNull(data))
  logger.info(validationProcess1.fuoriScala(data, dmin, dmax))
  logger.info(validationProcess1.variazione(datas, deltamax))

appContext = None

if __name__ == "__main__":
  # Turn on some logging in order to see what is happening behind the scenes...
  logger = logging.getLogger("dataValidator")
  loggingLevel = logging.DEBUG
  logger.setLevel(loggingLevel)
  #ch = logging.StreamHandler()
  ch = logging.FileHandler("dataValidator.log", mode='a')
  ch.setLevel(loggingLevel)
  formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
  ch.setFormatter(formatter)
  logger.addHandler(ch)

  path = os.path.dirname(__file__)
  appContext = ApplicationContext(XMLConfig(path+"/dataValidator.xml"))
  connection = appContext.get_object("mqConnection")

  try:
    # Open the channel
    channel = connection.channel()

    # Declare the exchange
    exchange = channel.exchange_declare(exchange='rawdata', type='fanout', passive=False, durable=True, auto_delete=False, internal=False, nowait=False, arguments={})

    # Declare the queue
    #channel.queue_declare(queue="test", durable=True, exclusive=False, auto_delete=False)
    result = channel.queue_declare(durable=False, exclusive=True, auto_delete=False)
    queue_name = result.method.queue
    channel.queue_bind(exchange='rawdata', queue=queue_name)

    # We're stuck looping here since this is a blocking adapter
    channel.basic_consume(handle_delivery, queue=queue_name, no_ack=True)
    
    logger.info("Data validator STARTED")
    logger.info("amqp connection : %s", connection)
    logger.info("amqp channel : %s", channel)
    logger.info("amqp exchange : %s", exchange)
    logger.info("amqp queue : %s", result)
    
    channel.start_consuming()
  except Exception as ex:
    # Gracefully close the connection
    connection.close()
    # Loop until we're fully closed, will stop on its own
    #connection.ioloop.start()
    
    print ex