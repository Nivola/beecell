# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

from beecell.db.manager import RedisManager, MysqlManager
import pprint
import redis_collections
from beecell.tests import BeecellTestCase, runtest

tests = [
'test_redis_ping',
#'test_redis_info',
#'test_redis_size',
#'test_redis_config',
#'test_redis_cleandb',
#'test_redis_inspect',
#'test_redis_list',
]

class RedisManagerTestCase(BeecellTestCase):
    """
    """
    def setUp(self):
        BeecellTestCase.setUp(self)
        self.manager = RedisManager(self.redis_uri)
        
    def tearDown(self):
        BeecellTestCase.tearDown(self)

    #
    # redis
    #
    def test_redis_ping(self):
        res = self.manager.ping()
        
    def test_redis_info(self):
        pprint.pprint(self.manager.info())
        
    def test_redis_size(self):
        self.manager.size()
        
    def test_redis_config(self):
        pprint.pprint(self.manager.config(pattern='*mem*'))     
        
    def test_redis_cleandb(self):
        self.manager.cleandb()
    
    def test_redis_inspect(self):
        keys = self.manager.inspect(pattern='*', debug=False)
        #pprint.pprint(keys)
        #pprint.pprint(keys)
        pprint.pprint(self.manager.query(keys, ttl=True))
        #self.manager.delete(pattern='celery-schedule')
        
        schedule = redis_collections.Dict(key='celery-schedule', redis=self.manager.conn)
        print schedule.keys()
        
    def test_redis_list(self):
        keys = self.manager.inspect(pattern=u'prova_list', debug=False)
        pprint.pprint(keys)
        
        conn = self.manager.conn
        conn.lpush(u'prova_list', u'val1')
        conn.lpush(u'prova_list', u'val2')
        print conn.lpop(u'prova_list')
        print conn.lpop(u'prova_list')
        print conn.lpop(u'prova_list')
        
        #keys = self.manager.inspect(pattern=u'prova_list', debug=False)
        #pprint.pprint(keys)        
        
        #self.manager.delete(pattern=u'prova_list')

if __name__ == u'__main__':
    runtest(RedisManagerTestCase, tests)
    