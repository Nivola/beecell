'''
Created on Dec 9, 2013

@author: darkbk
'''
import gibbonutil.server.gevent_ssl
import cProfile
import logging
import unittest
from gibbonutil.logger import LoggerHelper

def run_test(suite, test_log_file):
    #setting logger
    logger = logging.getLogger('gibbon.test')
    LoggerHelper.setup_file_handler(logger, logging.DEBUG, test_log_file)
    
    # create an istance of portal2 logger
    severLogger = logging.getLogger('gibbon.portal')
    LoggerHelper.setup_file_handler(severLogger, logging.DEBUG, test_log_file)
    
    severLogger = logging.getLogger('gibbon.cloud')
    LoggerHelper.setup_file_handler(severLogger, logging.DEBUG, test_log_file)

    severLogger = logging.getLogger('gibbon.cloud.virt')
    LoggerHelper.setup_file_handler(severLogger, logging.DEBUG, test_log_file)

    severLogger = logging.getLogger('gibbon.amqp')
    LoggerHelper.setup_file_handler(severLogger, logging.DEBUG, test_log_file)    

    severLogger = logging.getLogger('gibbon.util')
    LoggerHelper.setup_file_handler(severLogger, logging.DEBUG, test_log_file)   

    severLogger = logging.getLogger('sqlalchemy.engine')
    LoggerHelper.setup_file_handler(severLogger, logging.DEBUG, test_log_file)

    severLogger = logging.getLogger('sqlalchemy.pool')
    LoggerHelper.setup_file_handler(severLogger, logging.DEBUG, test_log_file)

    severLogger = logging.getLogger('pika')
    LoggerHelper.setup_file_handler(severLogger, logging.INFO, test_log_file)
    
    # create an istance of watch logger
    #watchLogger = logging.getLogger('watch')
    #LoggerHelper.setup_file_handler(watchLogger, logging.INFO, watchLogFileName, format='%(asctime)s - %(message)s')    
    
    # run test suite
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)

#if __name__ == '__main__':
# start profile over test suite
#cProfile.run('run_test()', 'log/test.profile')
#p = pstats.Stats('log/test.profile')