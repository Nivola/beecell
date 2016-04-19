#!/usr/bin/env python
import pika
import pickle

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
channel.queue_declare(queue=queue)

print ' [*] Waiting for messages. To exit press CTRL+C'

def callback(ch, method, properties, body):
    item = pickle.loads(body)
    print "%-15s %-8s state: %-15s db: %-10s user: %-10s host: %-40s cmd: %-10s info: %s [%s]" % (
           item['timestamp'], item['id'], item['state'], item['db'], item['user'], 
           item['host'], item['command'], item['info'], item['time'])

channel.basic_consume(callback,
                      queue=queue,
                      no_ack=True)

channel.start_consuming()