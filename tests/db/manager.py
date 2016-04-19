'''
Created on Sep 2, 2013

@author: darkbk
'''
import unittest
from gibbonutil.auth import extract
from gibbonutil.db.manager import RedisManager, MysqlManager
from tests.test_util import run_test, UtilTestCase
import pprint

class RedisManagerTestCase(UtilTestCase):
    """
    """
    def setUp(self):
        UtilTestCase.setUp(self)
        redis_uri = '10.102.160.12;6379;1'
        self.manager = RedisManager(redis_uri)
        self.mysql_manager = MysqlManager(1, self.db_uri)
        self.mysql_manager.create_pool_engine()
        
    def tearDown(self):
        UtilTestCase.tearDown(self)

    #
    # redis
    #
    def test_redis_ping(self):
        self.manager.ping()
        
    def test_redis_info(self):
        pprint.pprint(self.manager.info())
        
    def test_redis_size(self):
        self.manager.size()
        
    def test_redis_config(self):
        pprint.pprint(self.manager.config(pattern='*mem*'))     
        
    def test_redis_cleandb(self):
        self.manager.cleandb()
    
    def test_redis_inspect(self):
        keys = self.manager.inspect(pattern='*celery-schedule*', debug=False)
        #pprint.pprint(keys)
        pprint.pprint(self.manager.query(keys))
        self.manager.delete(pattern='celery-schedule')     

    #
    # mysql
    #
    def test_mysql_ping(self):
        self.mysql_manager.ping()
        
    def test_get_tables_names(self):
        res = self.mysql_manager.get_tables_names()
        self.logger.debug(res)
        for item in res:
            table_obj = self.mysql_manager.get_table_description(item)
            self.logger.debug("%s: %s" % (item, table_obj))

    def test_count_table_rows(self):
        res = self.mysql_manager.count_table_rows('configuration')
    
    def test_query_table(self):
        res = self.mysql_manager.query_table('task')
        for item in res:
            self.logger.debug(item)

def test_suite():
    tests = [
             #'test_redis_ping',
             #'test_redis_info',
             #'test_redis_size',
             #'test_redis_config',
             #'test_redis_cleandb',
             'test_redis_inspect',
             
             #'test_mysql_ping',
             #'test_get_tables_names',
             #'test_count_table_rows',
             #'test_query_table',
            ]
    return unittest.TestSuite(map(RedisManagerTestCase, tests))

if __name__ == '__main__':
    run_test([test_suite()])