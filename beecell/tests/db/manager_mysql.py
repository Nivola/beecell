# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

from beecell.db import MysqlManager
from beecell.tests.test_util import BeecellTestCase, runtest

tests = [
    'test_ping',
    'test_get_schemas',
    'test_get_users',
    'test_get_tables_names',
    'test_get_table_description',
    'test_query_table',
]


class MysqlManagerTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

        db_uri = self.conf('mysql.conn')
        self.schema = self.conf('mysql.schema')
        self.manager = MysqlManager(1, db_uri+'/' + self.schema, connect_timeout=10)
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
        desc = self.manager.get_table_description('user')
        self.logger.debug(desc)

    def test_query_table(self):
        res = self.manager.query_table('user', where=None, fields="*", rows=20, offset=0)
        for item in res:
            self.logger.debug(item)


if __name__ == '__main__':
    runtest(MysqlManagerTestCase, tests)