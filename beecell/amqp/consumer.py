# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte


import logging
import pika
import time
import pickle
from pika.exceptions import AMQPError, AMQPConnectionError


class ConsumerError(Exception):
    pass


class AsyncConsumer(object):
    """This is a consumer that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.
    
    From : https://pika.readthedocs.org/en/0.9.13/examples/asynchronous_consumer_example.html
    
    Example:
        example = AsyncConsumer()
        try:
            example.run()
        except KeyboardInterrupt:
            example.stop()
    """
    logger = logging.getLogger('gibbon.util.amqp')

    def __init__(self, name, amqp_params, callback=None, 
                 auto_reconnect=False, reconnect_after=60):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param str amqp_params: The AMQP connection params. Dict like:
                                {'host':'172.16.0.8', 'port':5672, 'vhost':'/',
                                 'user':'guest', 'pwd':'testlab',
                                 'queue':'gibbon.job', 'durable':False}
        :param callback: callback function
        :param auto_reconnect: set to True if you want portal2 reconnect
                               automatically when connection goes down.
                               [default = False]
        :param reconnect_after: when connection goes down it tries to reconnect 
                                after this time indefinitely [default = 60s]
        """
        self._name = name
        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._amqp_params = amqp_params
        
        self.queue_name = self._amqp_params['queue']
        self.durable = self._amqp_params['durable']
        self.reconnect_after = reconnect_after
        self.auto_reconnect = auto_reconnect
        
        # callback function invoked when a message is received. 
        # def callback(unused_channel, basic_deliver, properties, data)
        self.callback = callback
        
        self.logger.info('Create new async consumer: %s', self._name)

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection
        """
        self.logger.info('%s - Connecting to %s:%s', self._name, self._amqp_params['host'], self._amqp_params['port'])
        credentials = pika.PlainCredentials(self._amqp_params['user'], 
                                            self._amqp_params['pwd'])
        parameters = pika.ConnectionParameters(self._amqp_params['host'], 
                                               self._amqp_params['port'], 
                                               self._amqp_params['vhost'],
                                               credentials,)
        return pika.SelectConnection(parameters=parameters,
                                     on_open_callback=self.on_connection_open,
                                     on_open_error_callback=self.on_connection_error,
                                     on_close_callback=self.on_connection_closed,
                                     stop_ioloop_on_close=False)

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        self.logger.info('%s - Closing connection', self._name)
        self._connection.close()

    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The portal2 provided reply_code if given
        :param str reply_text: The portal2 provided reply_text if given
        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self.logger.warning('%s - Connection closed, reopening in 5 seconds: (%s) %s',
                                self._name, reply_code, reply_text)
            self._connection.add_timeout(self.reconnect_after, self.reconnect)

    def on_connection_error(self, connection):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The portal2 provided reply_code if given
        :param str reply_text: The portal2 provided reply_text if given
        """
        if self.auto_reconnect:
            self.logger.warning('%s - Connection error. Try to reconnect after %ss',
                                self._name, self.reconnect_after)            
            # wait some time
            time.sleep(self.reconnect_after)
            
            # Create a new connection
            self._connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()
        else:
            self.logger.warning('%s - Connection error. ', self._name)            

    def on_connection_open(self, unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection
        """
        self.logger.info('%s - Connection opened', self._name)
        self.logger.info('%s - Creating a new channel', self._name)
        self._connection.channel(on_open_callback=self.on_channel_open)

    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.
        """
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()

        if not self._closing:
            # Create a new connection
            self._connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def on_channel_closed(self, channel, reply_code, reply_text):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed
        """
        self.logger.warning('%s - Channel %i was closed: (%s) %s',
                            self._name, channel, reply_code, reply_text)
        self._connection.close()

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        self.logger.info('%s - Channel opened' % self._name)
        self._channel = channel
        self.logger.info('%s - Adding channel close callback', self._name)
        self._channel.add_on_close_callback(self.on_channel_closed)
        self.logger.info('%s - Declaring queue', self._name)
        self._channel.queue_declare(self.on_queue_declareok, 
                                    queue=self.queue_name,
                                    durable=self.durable,
                                    exclusive=False)

    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue. In this method we will bind 
        the queue and exchange together with the routing key by issuing the 
        Queue.Bind command. When this command is complete, the on_bindok 
        method will be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame
        """
        self.logger.info('%s - Adding consumer cancellation callback', self._name)
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)
        self.logger.info('%s - Bind queue "%s" to channel', self._name, self.queue_name)
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self.queue_name)      

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame
        """
        self.logger.info('%s - Consumer was cancelled remotely, shutting down: %r',  method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param str|unicode body: The message body
        """
        self.logger.debug('%s - Received message #%s from %s. Size: %s',
                          self._name, basic_deliver.delivery_tag, 
                          properties.app_id, len(body))
        
        # call custom callback
        if self.callback:
            self.callback(unused_channel, basic_deliver, properties, body)
            
        self.logger.debug('%s - Acknowledging message %s', self._name, basic_deliver.delivery_tag)
        self._channel.basic_ack(basic_deliver.delivery_tag)

    def on_cancelok(self, unused_frame):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame
        """
        self.logger.info('%s - RabbitMQ acknowledged the cancellation of the consumer', self._name)
        self.logger.info('%s - Closing the channel', self._name)
        self._channel.close()

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.
        """
        try:
            self.logger.info('%s - Starting', self._name)
            self._connection = self.connect()
            self._connection.ioloop.start()
        except AMQPConnectionError:
            err = '%s - Connection to amqp portal2 %s:%s can not be established' % (
                  self._name, self._amqp_params['host'], self._amqp_params['port'])
            self.logger.error(err)
            # try to reconnect when rised excpetion like 'IncompatibleProtocolError'
            self._connection.callbacks.process(0, 
                                               self._connection.ON_CONNECTION_ERROR, 
                                               self._connection, 
                                               self._connection)
            
            raise ConsumerError(err)
        except (AMQPError, Exception) as ex:
            self.logger.error(ex)
            raise ConsumerError(ex)        

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.
        """
        try:
            self.logger.info('%s - Stopping', self._name)
            self._closing = True
            
            if self._channel:
                self.logger.info('%s - Sending a Basic.Cancel command to RabbitMQ', 
                                 self._name)
                self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)
        except (AMQPError, Exception) as ex:
            self.logger.error(ex)
            raise ConsumerError(ex)


class AsyncSubscriber(object):
    """This is a subscriber that will handle unexpected interactions
    with RabbitMQ such as channel and connection closures.

    If RabbitMQ closes the connection, it will reopen it. You should
    look at the output, as there are limited reasons why the connection may
    be closed, which usually are tied to permission related issues or
    socket timeouts.

    If the channel is closed, it will indicate a problem with one of the
    commands that were issued and that should surface in the output as well.
    
    From : https://pika.readthedocs.org/en/0.9.13/examples/asynchronous_consumer_example.html
    
    Example:
        example = ExampleConsumer('amqp://guest:guest@localhost:5672/%2F')
        try:
            example.run()
        except KeyboardInterrupt:
            example.stop()
    """
    logger = logging.getLogger('gibbon.util.amqp')

    def __init__(self, name, amqp_params, callback=None, 
                 auto_reconnect=False, reconnect_after=60):
        """Create a new instance of the consumer class, passing in the AMQP
        URL used to connect to RabbitMQ.

        :param str amqp_params: The AMQP connection params. Dict like:
                                {'host':'172.16.0.8', 'port':5672, 'vhost':'/',
                                 'user':'guest', 'pwd':'testlab',
                                 'exchange':{'name':'message', 'type':'fanout'},
                                 'routing_key':'example.text', 'durable':False}
        :param callback: callback function
        :param auto_reconnect: set to True if you want portal2 reconnect
                               automatically when connection goes down.
                               [default = False]
        :param reconnect_after: when connection goes down it tries to reconnect 
                                after this time indefinitely [default = 60s]
        """
        self._name = name
        self._connection = None
        self._channel = None
        self._queue_name = None
        self._closing = False
        self._consumer_tag = None
        self._amqp_params = amqp_params
        
        self.exchange_name = self._amqp_params['exchange']['name']
        self.exchange_type = self._amqp_params['exchange']['type']
        self.routing_key = self._amqp_params['routing_key']
        self.durable = self._amqp_params['durable']
        self.reconnect_after = reconnect_after
        self.auto_reconnect = auto_reconnect
        
        # callback function invoked when a message is received. 
        # def callback(unused_channel, basic_deliver, properties, data)
        self.callback = callback
        
        self.logger.info('Create new async subscriber: %s', self._name)

    def connect(self):
        """This method connects to RabbitMQ, returning the connection handle.
        When the connection is established, the on_connection_open method
        will be invoked by pika.

        :rtype: pika.SelectConnection
        """
        self.logger.info('%s - Connecting to %s:%s', self._name,
                                                     self._amqp_params['host'], 
                                                     self._amqp_params['port'])
        credentials = pika.PlainCredentials(self._amqp_params['user'], 
                                            self._amqp_params['pwd'])
        parameters = pika.ConnectionParameters(self._amqp_params['host'], 
                                               self._amqp_params['port'], 
                                               self._amqp_params['vhost'],
                                               credentials,)
        return pika.SelectConnection(parameters=parameters,
                                     on_open_callback=self.on_connection_open,
                                     on_open_error_callback=self.on_connection_error,
                                     on_close_callback=self.on_connection_closed,
                                     stop_ioloop_on_close=False)

    def close_connection(self):
        """This method closes the connection to RabbitMQ."""
        self.logger.info('%s - Closing connection', self._name)
        self._connection.close()

    def on_connection_closed(self, connection, reply_code, reply_text):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The portal2 provided reply_code if given
        :param str reply_text: The portal2 provided reply_text if given
        """
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self.logger.warning('%s - Connection closed, reopening in 5 seconds: (%s) %s',
                                self._name, reply_code, reply_text)
            self._connection.add_timeout(self.reconnect_after, self.reconnect)

    def on_connection_error(self, connection):
        """This method is invoked by pika when the connection to RabbitMQ is
        closed unexpectedly. Since it is unexpected, we will reconnect to
        RabbitMQ if it disconnects.

        :param pika.connection.Connection connection: The closed connection obj
        :param int reply_code: The portal2 provided reply_code if given
        :param str reply_text: The portal2 provided reply_text if given
        """
        if self.auto_reconnect:
            self.logger.warning('%s - Connection error. Try to reconnect after %ss',
                                self._name, self.reconnect_after)             
            # wait some time
            time.sleep(self.reconnect_after)
            
            # Create a new connection
            self._connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()
        else:
            self.logger.warning('%s - Connection error. ', self._name)            
                         
    def on_connection_open(self, unused_connection):
        """This method is called by pika once the connection to RabbitMQ has
        been established. It passes the handle to the connection object in
        case we need it, but in this case, we'll just mark it unused.

        :type unused_connection: pika.SelectConnection
        """
        self.logger.info('%s - Connection opened', self._name)
        self.logger.info('%s - Creating a new channel', self._name)
        self._connection.channel(on_open_callback=self.on_channel_open)        

    def reconnect(self):
        """Will be invoked by the IOLoop timer if the connection is
        closed. See the on_connection_closed method.
        """
        # This is the old connection IOLoop instance, stop its ioloop
        self._connection.ioloop.stop()

        if not self._closing:
            # Create a new connection
            self._connection = self.connect()

            # There is now a new connection, needs a new ioloop to run
            self._connection.ioloop.start()

    def on_channel_closed(self, channel, reply_code, reply_text):
        """Invoked by pika when RabbitMQ unexpectedly closes the channel.
        Channels are usually closed if you attempt to do something that
        violates the protocol, such as re-declare an exchange or queue with
        different parameters. In this case, we'll close the connection
        to shutdown the object.

        :param pika.channel.Channel: The closed channel
        :param int reply_code: The numeric reason the channel was closed
        :param str reply_text: The text reason the channel was closed
        """
        self.logger.warning('%s - Channel %i was closed: (%s) %s',
                            self._name, channel, reply_code, reply_text)
        self._connection.close()

    def on_channel_open(self, channel):
        """This method is invoked by pika when the channel has been opened.
        The channel object is passed in so we can make use of it.

        Since the channel is now open, we'll declare the exchange to use.

        :param pika.channel.Channel channel: The channel object

        """
        self.logger.info('%s - Channel opened', self._name)
        self._channel = channel
        self.logger.info('%s - Adding channel close callback', self._name)
        self._channel.add_on_close_callback(self.on_channel_closed)
        self.logger.info('%s - Declaring exchange %s', self._name, self.exchange_name)
        self._channel.exchange_declare(self.on_exchange_declareok,
                                       self.exchange_name,
                                       self.exchange_type)

    def on_exchange_declareok(self, unused_frame):
        """Invoked by pika when RabbitMQ has finished the Exchange.Declare command.

        :param pika.Frame.Method unused_frame: Exchange.DeclareOk response frame
        """
        self.logger.info('%s - Exchange declared', self._name)
        self.logger.info('%s - Declaring queue', self._name)
        self._channel.queue_declare(self.on_queue_declareok, 
                                    auto_delete=True,
                                    durable=self.durable,
                                    exclusive=True)

    def on_queue_declareok(self, method_frame):
        """Method invoked by pika when the Queue. In this method we will bind 
        the queue and exchange together with the routing key by issuing the 
        Queue.Bind command. When this command is complete, the on_bindok 
        method will be invoked by pika.

        :param pika.frame.Method method_frame: The Queue.DeclareOk frame
        """
        self._queue_name = method_frame.method.queue
        self.logger.info('%s - Binding exchange "%s" to queue "%s" with routing-key "%s"', 
                         self._name, 
                         self.exchange_name, 
                         self._queue_name, 
                         self.routing_key)
        self._channel.queue_bind(callback=self.on_bindok, 
                                 queue=self._queue_name,
                                 exchange=self.exchange_name, 
                                 routing_key=self.routing_key)

    def on_consumer_cancelled(self, method_frame):
        """Invoked by pika when RabbitMQ sends a Basic.Cancel for a consumer
        receiving messages.

        :param pika.frame.Method method_frame: The Basic.Cancel frame
        """
        self.logger.info('%s - Consumer was cancelled remotely, shutting down: %r',
                         self._name, method_frame)
        if self._channel:
            self._channel.close()

    def on_message(self, unused_channel, basic_deliver, properties, body):
        """Invoked by pika when a message is delivered from RabbitMQ. The
        channel is passed for your convenience. The basic_deliver object that
        is passed in carries the exchange, routing key, delivery tag and
        a redelivered flag for the message. The properties passed in is an
        instance of BasicProperties with the message properties and the body
        is the message that was sent.

        :param pika.channel.Channel unused_channel: The channel object
        :param pika.Spec.Basic.Deliver: basic_deliver method
        :param pika.Spec.BasicProperties: properties
        :param str|unicode body: The message body
        """
        data = pickle.loads(body)
        self.logger.debug('%s - Received message #%s from %s: %s', 
                          self._name,
                          basic_deliver.delivery_tag, 
                          properties.app_id, data)
        
        # call custom callback
        if self.callback:
            self.callback(unused_channel, basic_deliver, properties, data)

        delivery_tag = basic_deliver.delivery_tag
        self.logger.debug('%s - Acknowledging message %s', self._name, delivery_tag)
        self._channel.basic_ack(delivery_tag)

    def on_cancelok(self, unused_frame):
        """This method is invoked by pika when RabbitMQ acknowledges the
        cancellation of a consumer. At this point we will close the channel.
        This will invoke the on_channel_closed method once the channel has been
        closed, which will in-turn close the connection.

        :param pika.frame.Method unused_frame: The Basic.CancelOk frame
        """
        self.logger.info('%s - Closing the channel', self._name)
        self._channel.close()

    def on_bindok(self, unused_frame):
        """Invoked by pika when the Queue.Bind method has completed. At this
        point we will start consuming messages by calling start_consuming
        which will invoke the needed commands to start the process.

        :param pika.frame.Method unused_frame: The Queue.BindOk response frame
        """
        self.logger.info('%s - Queue bound', self._name)
        self.logger.info('%s - Adding consumer cancellation callback', self._name)
        self._channel.add_on_cancel_callback(self.on_consumer_cancelled)           
        self.logger.info('%s - Issuing consumer related commands', self._name)
        self._consumer_tag = self._channel.basic_consume(self.on_message,
                                                         self._queue_name)

    def run(self):
        """Run the example consumer by connecting to RabbitMQ and then
        starting the IOLoop to block and allow the SelectConnection to operate.
        """
        try:
            self.logger.info('%s - Starting', self._name)
            self._connection = self.connect()
            self._connection.ioloop.start()
        except AMQPConnectionError as ex:
            err = '%s - Connection to amqp portal2 %s:%s can not be established: %s' % (
                  self._name, self._amqp_params['host'], self._amqp_params['port'], ex)
            self.logger.error(err)
            
            # try to reconnect when rised excpetion like 'IncompatibleProtocolError'
            self._connection.callbacks.process(0, 
                                               self._connection.ON_CONNECTION_ERROR, 
                                               self._connection, 
                                               self._connection)            
            
            raise ConsumerError(err)
        except (AMQPError, Exception) as ex:
            self.logger.error(ex)
            raise ConsumerError(ex)        

    def stop(self):
        """Cleanly shutdown the connection to RabbitMQ by stopping the consumer
        with RabbitMQ. When RabbitMQ confirms the cancellation, on_cancelok
        will be invoked by pika, which will then closing the channel and
        connection. The IOLoop is started again because this method is invoked
        when CTRL-C is pressed raising a KeyboardInterrupt exception. This
        exception stops the IOLoop which needs to be running for pika to
        communicate with RabbitMQ. All of the commands issued prior to starting
        the IOLoop will be buffered but not processed.
        """
        try:
            self.logger.info('%s - Stopping', self._name)
            self._closing = True
            if self._channel:
                self.logger.info('%s - Sending a Basic.Cancel command to RabbitMQ', 
                                 self._name)
                self._channel.basic_cancel(self.on_cancelok, self._consumer_tag)
        except (AMQPError, Exception) as ex:
            self.logger.error(ex)
            raise ConsumerError(ex)
