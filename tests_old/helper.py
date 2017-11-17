'''
Created on Sep 2, 2013

@author: darkbk
'''
import logging
import unittest
import traceback
import random
import pprint
from beecell.perf import watch_test
from beecell.logger import LoggerHelper

class HelperTestCase(unittest.TestCase):
    logger = logging.getLogger('gibbon.test')

    def setUp(self):
        self.logger.debug('\n########## %s.%s ##########' % 
                          (self.__module__, self.__class__.__name__))
        
    def tearDown(self):
        pass

    @watch_test
    def test_setup_amqp_logger(self):
        try:
            event_id = '1'
            event_type = 'job'
            data = 'data'
            event = Event(event_id, event_type, data)
            self.logger.debug(event)
        except Exception as ex:
            self.logger.error(traceback.format_exc())
            self.fail(ex)

def test_suite():
    tests = [
             'test_setup_amqp_logger',
            ]
    return unittest.TestSuite(map(HelperTestCase, tests))

if __name__ == '__main__':
    import os
    from beecell.test_util import run_test
    
    syspath = os.path.expanduser("~")
    log_file = syspath + '/workspace/gibbon/util/log/test.log'
    run_test([test_suite()], log_file)  