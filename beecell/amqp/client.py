# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte

import pika


class AmqpClient(object):
    """Amqp client"""
    connection_pars = None
    exchange = None
    queue = None

    def __init__(self, connection_pars, exchange, queue):
        """"""
        self.connection_pars = connection_pars
        self.exchange = exchange
        self.queue = queue

    def __del__(self):
        pass

    def sendMessage(self, message, tid):
        """"""
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.connection_pars.host,
                                                                       port=self.connection_pars.port))
        channel = connection.channel()
        channel.queue_declare(queue=self.queue, durable=True)
        channel.basic_publish(exchange='',
                              routing_key=self.queue,
                              body=message,
                              properties=pika.BasicProperties(
                                 correlation_id=tid,
                                 delivery_mode=2, # make message persistent
                              ))
        connection.close()
