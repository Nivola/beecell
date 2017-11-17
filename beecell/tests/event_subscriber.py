'''
Created on Feb 10, 2014

@author: darkbk
'''
import sys
import os
import logging
import traceback

sys.path.append(os.path.expanduser("~/workspace/gibbon/src"))
sys.path.append(os.path.expanduser("~/workspace/gibbon/tests"))

from beecell.logger import LoggerHelper
from beecell.amqp import AsyncSubscriber, ConsumerError

syspath = os.path.expanduser("~")
log_file = syspath + '/workspace/gibbon/util/log/test.log'

logger = logging.getLogger('pika')
LoggerHelper.setup_simple_handler(logger, logging.INFO)

logger = logging.getLogger('gibbon.amqp')
LoggerHelper.setup_simple_handler(logger, logging.DEBUG)

#logger.info('start')
#sys.stdout.write('start')

# create and start amqp sumbscriber on event exchange
amqp_params = {'host':'172.16.0.8', 'port':5672, 'vhost':'/',
               'user':'guest', 'pwd':'testlab',
               'exchange':{'name':'gibbon.event', 'type':'topic'},
               'routing_key':'gibbon.jobevent', 'durable':False}
def callback(unused_channel, basic_deliver, properties, data):
    pass
    
subscriber = AsyncSubscriber(amqp_params, 
                             auto_reconnect=True, 
                             reconnect_after=10,
                             callback=callback)
subscriber.auto_reconnection = True
try:
    subscriber.run()
except ConsumerError as ex:
    logger.error('Connection to amqp portal2 can not be established')