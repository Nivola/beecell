# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2024 CSI-Piemonte


import pika

connection = pika.BlockingConnection(pika.ConnectionParameters(host="spedata6", port=5672))
channel = connection.channel()

channel.exchange_declare(exchange="dashboard.logs", type="topic", durable=True, auto_delete=False)

result = channel.queue_declare(exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange="dashboard.logs", queue=queue_name)

print(" [*] Waiting for logs. To exit press CTRL+C")


def callback(ch, method, properties, body):
    print(" [x] %r" % (body,))


channel.basic_consume(callback, queue=queue_name, no_ack=True)

channel.start_consuming()
