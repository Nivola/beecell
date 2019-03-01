# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
from beecell.db import MysqlManager
from beecell.tests.test_util import BeecellTestCase, runtest

tests = [
    u'test_ping',
    u'test_get_schemas',
    u'test_get_users',
    u'test_get_tables_names',
    u'test_get_table_description',
    u'test_query_table',
]


class MysqlManagerTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

        db_uri = self.conf(u'mysql.conn')
        self.schema = self.conf(u'mysql.schema')
        self.manager = MysqlManager(1, db_uri+u'/' + self.schema, connect_timeout=10)
        self.manager.create_simple_engine()
        
    def tearDown(self):
        BeecellTestCase.tearDown(self)

    def test_ping(self):
        self.manager.ping()
    
    def test_get_schemas(self):
        self.manager.get_schemas()

    def test_get_users(self):
        self.manager.get_users()
    
    def test_get_tables_names(self):
        tables = self.manager.get_schema_tables(self.schema)
        self.logger.debug(tables)

    def test_get_table_description(self):
        desc = self.manager.get_table_description(u'user')
        self.logger.debug(desc)

    def test_query_table(self):
        res = self.manager.query_table(u'user', where=None, fields="*", 
                                       rows=20, offset=0)
        for item in res:
            self.logger.debug(item)


if __name__ == u'__main__':
    runtest(MysqlManagerTestCase, tests)