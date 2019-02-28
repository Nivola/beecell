# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

import pika
import pickle
import logging

logger = logging.getLogger('gibbon.util.amqp')


def open_amqp_channel(queue_conn, queue):
    """ """
    credentials = pika.PlainCredentials(queue_conn['user'], queue_conn['pwd'])
    parameters = pika.ConnectionParameters(queue_conn['host'], 
                                           queue_conn['port'], 
                                           queue_conn['vhost'], 
                                           credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    
    return channel


def open_amqp_exchange(queue_conn, exchange):
    """ """
    credentials = pika.PlainCredentials(queue_conn['user'], queue_conn['pwd'])
    parameters = pika.ConnectionParameters(queue_conn['host'], 
                                           queue_conn['port'], 
                                           queue_conn['vhost'], 
                                           credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, type='fanout')
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange, queue=queue_name)    
     
    return (channel, queue_name)


def subscriber(queue_conn, exchange, callback):
    """Base amqp sumbscriber."""
    credentials = pika.PlainCredentials(queue_conn['user'], queue_conn['pwd'])
    parameters = pika.ConnectionParameters(queue_conn['host'], 
                                           queue_conn['port'], 
                                           queue_conn['vhost'], 
                                           credentials)
    connection = pika.BlockingConnection(parameters)
    logger.debug('Open amqp connection - host: %s, port: %s, vhost: %s, user: %s' % (
        queue_conn['host'], queue_conn['port'], 
        queue_conn['vhost'], queue_conn['user']))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, type='fanout')
    result = channel.queue_declare(exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=exchange, queue=queue_name)
    channel.basic_consume(callback, queue=queue_name, no_ack=True)
    logger.debug("Start amqp subscriber over exchange: %s" % exchange)
    channel.start_consuming()


def consumer(queue_conn, queue, callback):
    """Base amqp consumer."""
    credentials = pika.PlainCredentials(queue_conn['user'], queue_conn['pwd'])
    parameters = pika.ConnectionParameters(queue_conn['host'], 
                                           queue_conn['port'], 
                                           queue_conn['vhost'], 
                                           credentials)
    connection = pika.BlockingConnection(parameters)
    logger.debug('Open amqp connection - host: %s, port: %s, vhost: %s, user: %s' % (
        queue_conn['host'], queue_conn['port'], 
        queue_conn['vhost'], queue_conn['user']))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_consume(callback, queue=queue, no_ack=True)
    logger.debug("Start amqp consumer over queue: %s" % queue)
    channel.start_consuming()


def queue_publisher(queue_conn, queue, message):
    """Base amqp queue publisher."""
    # pickle message
    data = message
    credentials = pika.PlainCredentials(queue_conn['user'], queue_conn['pwd'])
    parameters = pika.ConnectionParameters(queue_conn['host'], 
                                           queue_conn['port'], 
                                           queue_conn['vhost'], 
                                           credentials,
                                           heartbeat_interval=30,
                                           connection_attempts=5,
                                           retry_delay=2,
                                           socket_timeout=30)
    connection = pika.BlockingConnection(parameters)
    logger.debug("Opened connection: %s" % (connection))
    channel = connection.channel()
    channel.queue_declare(queue=queue, durable=queue_conn['durable'])
    channel.basic_publish(exchange='',
                          routing_key=queue,
                          body=data,
                          properties=pika.BasicProperties(delivery_mode=2))
    
    logger.debug("Sent message to queue %s" % (queue))
    connection.close()
    logger.debug("Closed connection: %s" % (connection))


def exchange_publisher(queue_conn, exchange, message):
    """Base amqp exchange publisher."""
    # pickle message
    data = pickle.dumps(message)
    
    credentials = pika.PlainCredentials(queue_conn['user'], queue_conn['pwd'])
    parameters = pika.ConnectionParameters(queue_conn['host'], 
                                           queue_conn['port'], 
                                           queue_conn['vhost'], 
                                           credentials,
                                           heartbeat_interval=30,
                                           connection_attempts=5,
                                           retry_delay=2,
                                           socket_timeout=30)
    connection = pika.BlockingConnection(parameters)
    logger.debug("Opened connection: %s" % (connection))
    channel = connection.channel()
    channel.exchange_declare(exchange=exchange, type='fanout')
    channel.basic_publish(exchange=exchange,
                          routing_key='',
                          body=data)
    logger.debug("Sent message to exchange %s" % (exchange))
    connection.close()
    logger.debug("Closed connection: %s" % (connection))
