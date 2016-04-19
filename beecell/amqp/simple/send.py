#!/usr/bin/env python
import pika

#pika.adapters.base_connection
host = '10.102.47.205'
port = 5672
vhost = '/'
user = 'guest'
pwd = 'testlab'
queue = 'mysql_statement'
durable = False
message = 'hello'
id = '1'

credentials = pika.PlainCredentials(user, pwd)
parameters = pika.ConnectionParameters(host, port, vhost, credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel.queue_declare(queue=queue, durable=durable)
channel.basic_publish(exchange='',
                      routing_key=queue,
                      body=message,
                      #properties=pika.BasicProperties(
                      #   correlation_id = id,
                      #   delivery_mode = 2, # make message persistent
                      #)
                     )

print " [x] Sent 'Hello World!'"
connection.close()
