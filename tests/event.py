'''
Created on Sep 2, 2013

@author: darkbk
'''
import logging
import unittest
import traceback
import random
import pprint
from gibbonutil.perf import watch_test
from gibbonutil.logger import Event, JobEvent, LoggerHelper, AMQPHandlerError

class EventTestCase(unittest.TestCase):
    logger = logging.getLogger('gibbon.test')

    def setUp(self):
        self.logger.debug('\n########## %s.%s ##########' % 
                          (self.__module__, self.__class__.__name__))
        
        self.logging_level = logging.DEBUG
        self.amqp_params = {'host':'172.16.0.8', 'port':5672, 'vhost':'/',
                            'user':'guest', 'pwd':'testlab', 
                            'exchange':'gibbon.event', 'durable':False} 
        
    def tearDown(self):
        pass

    @watch_test
    def test_init(self):
        try:
            event_id = '1'
            event_type = 'job'
            data = 'data'
            event = Event(event_id, event_type, data)
            self.logger.debug(event)
        except Exception as ex:
            self.logger.error(traceback.format_exc())
            self.fail(ex)
            
    @watch_test
    def test_json(self):
        try:
            event_id = '1'
            event_type = 'job'
            data = 'data'
            event = Event(event_id, event_type, data).json()
            self.logger.debug(event)
        except Exception as ex:
            self.logger.error(traceback.format_exc())
            self.fail(ex)

    @watch_test
    def test_publish(self):
        try:
            """
            configure simple logger
            logger = logging.getLogger('gibbon.event')
            logging_level = logging.DEBUG
            file_name =  os.path.expanduser("~") + \
                         '/workspace/gibbon/util/log/test.log'
            LoggerHelper.setup_file_handler(logger, logging_level, file_name)
            """
            """configure amqp logger"""
            event_logger = logging.getLogger('gibbon.event')
            LoggerHelper.setup_amqp_logger(event_logger, 
                                           self.logging_level, 
                                           self.amqp_params)
            event_logger = logging.getLogger('gibbon.jobevent')
            LoggerHelper.setup_amqp_logger(event_logger, 
                                           self.logging_level, 
                                           self.amqp_params) 
            # typically this logger use an amqp handler
            # catch AMQPError to manage amqp error like close connection
            #Event('1', 'eee', 'data').publish()
            #Event('2', 'eee', 'data').publish()
            #Event('3', 'eee', 'data').publish()
            JobEvent('3', 0).publish()           
        except AMQPHandlerError as ex:
            self.fail(ex)
        except Exception as ex:
            self.fail(ex)

def test_suite():
    tests = [
             'test_init',
             'test_json',
             'test_publish',
            ]
    return unittest.TestSuite(map(EventTestCase, tests))

if __name__ == '__main__':
    import os
    from gibbonutil.test_util import run_test
    syspath = os.path.expanduser("~")
    log_file = syspath + '/workspace/gibbon/util/log/test.log'
    
    run_test([test_suite()], log_file)    