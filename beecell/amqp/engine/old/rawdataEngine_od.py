#!/usr/bin/env python
import pika
import sys

from pika.adapters import BlockingConnection
from smart.sensor import util

pika.log.setup(color=True)


def handle_delivery(channel, method_frame, header_frame, body):
  # Receive the data in 3 frames from RabbitMQ
  pika.log.info("Basic.Deliver %s delivery-tag %i: %s",
                  header_frame.content_type,
                  method_frame.delivery_tag,
                  body)
  sensorClass = util.simpleDetect(body)
  pika.log.info(sensorClass)
  sensor = sensorClass()
  data = sensor.decode(body)
  pika.log.info(data)
  #channel.basic_ack(delivery_tag=method_frame.delivery_tag)

if __name__ == '__main__':
  # Connect to RabbitMQ
  host='spedata6'
  port=5672
  vhost='/'
  credentials = pika.PlainCredentials('guest', 'guest')
  parameters = pika.ConnectionParameters(host=host, port=port, virtual_host=vhost, credentials=credentials, channel_max=0, frame_max=131072, heartbeat=False)
  connection = BlockingConnection(parameters)
  
  # Open the channel
  channel = connection.channel()
  
  # Declare the exchange
  channel.exchange_declare(exchange='rawdata', type='fanout', passive=False, durable=True, auto_delete=False, internal=False, nowait=False, arguments={})
  
  # Declare the queue
  #channel.queue_declare(queue="test", durable=True, exclusive=False, auto_delete=False)
  result = channel.queue_declare(durable=False, exclusive=True, auto_delete=False)
  queue_name = result.method.queue
  channel.queue_bind(exchange='rawdata', queue=queue_name)
  
  # We're stuck looping here since this is a blocking adapter
  channel.basic_consume(handle_delivery, queue=queue_name, no_ack=True)
  channel.start_consuming()

