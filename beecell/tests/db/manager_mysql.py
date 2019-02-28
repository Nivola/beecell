# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

from beecell.db.manager import RedisManager, MysqlManager
from beecell.tests import BeecellTestCase, runtest

tests = [
u'test_ping',
u'test_get_schemas',
u'test_get_users',
u'test_get_tables_names',
u'test_get_table_description',
u'test_query_table',

#u'test_temporary_table',
]

class MysqlManagerTestCase(BeecellTestCase):
    """
    """
    def setUp(self):
        BeecellTestCase.setUp(self)

        db_uri = self.mysql[u'root']
        schema = self.mysql[u'schemas'][0]
        self.schema = u'auth'
        self.manager = MysqlManager(1, db_uri+u'/'+self.schema)
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
        #res = self.manager.get_tables_names()
        #self.logger.debug(res)
        #for item in res:
        #    table_obj = self.manager.get_schema_tables(item)
        #    self.logger.debug("%s: %s" % (item, table_obj))

    def test_get_table_description(self):
        desc = self.manager.get_table_description(u'user')
        self.logger.debug(desc)    

    def test_query_table(self):
        res = self.manager.query_table(u'user', where=None, fields="*", 
                                       rows=20, offset=0)
        for item in res:
            self.logger.debug(item)
            
    def test_temporary_table(self):
        session = self.manager.get_session()
        conn = session.connection()
        # show engine type
        #sql = u'SHOW ENGINES'
        #result = conn.execute(sql)
        #for item in result:
        #    self.logger.info(item)
        # create temporary table
        sql = u'create temporary table perms (tag varchar(100) primary key) engine=MEMORY default charset latin1'
        result = conn.execute(sql)
        self.logger.info(result)
        # insert data
        values = []
        for i in xrange(0, 1000):
            values.append(u'(\'tag-%s\')' % i)
        sql = u'INSERT INTO perms (tag) values %s;' % u','.join(values)
        result = conn.execute(sql)
        self.logger.info(result)    
        # query data
        result = conn.execute(u'SELECT count(tag) FROM perms')
        #result = conn.execute(u'SELECT tag FROM perms')
        for item in result:
            self.logger.info(item)
        self.manager.release_session(session)


if __name__ == u'__main__':
    runtest(MysqlManagerTestCase, tests)
    