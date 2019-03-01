# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

from beecell.db.manager import RedisManager
import redis_collections
from beecell.tests.test_util import BeecellTestCase, runtest

tests = [
    'test_redis_ping',
    'test_redis_info',
    'test_redis_size',
    'test_redis_config',
    'test_redis_cleandb',
    'test_redis_inspect',
]


class RedisManagerTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

        self.redis_uri = self.conf(u'redis.single')
        self.manager = RedisManager(self.redis_uri)
        
    def tearDown(self):
        BeecellTestCase.tearDown(self)

    def test_redis_ping(self):
        self.manager.ping()
        
    def test_redis_info(self):
        self.manager.info()
        
    def test_redis_size(self):
        self.manager.size()
        
    def test_redis_config(self):
        self.manager.config(pattern='*mem*')
        
    def test_redis_cleandb(self):
        self.manager.cleandb()
    
    def test_redis_inspect(self):
        keys = self.manager.inspect(pattern='*', debug=False)
        schedule = redis_collections.Dict(key='celery-schedule', redis=self.manager.conn)
        res = schedule.keys()
        self.logger.debug(res)


if __name__ == u'__main__':
    runtest(RedisManagerTestCase, tests)
