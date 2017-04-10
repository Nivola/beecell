'''
Created on Apr 24, 2014

@author: darkbk
'''
import logging
import redis
import os
import ujson as json
from sqlalchemy import create_engine, exc, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import Pool
from datetime import datetime

class SqlManagerError(Exception): pass
class RedisManagerError(Exception): pass
class MysqlManagerError(Exception): pass

class ConnectionManager(object):
    """Abstract Connection manager
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__module__+ \
                                        '.'+self.__class__.__name__)

    def get_session(self):
        """Open a database session.
        
        :return: session object
        """
        return NotImplemented
        
    def release_session(self, session):
        """Close active database session.
        
        :param session: active session to close
        """        
        return NotImplemented

class RedisManager(ConnectionManager):
    """Manager for redis instance.
    
    :param: redis_uri: redis connection uri. Ex ``redis://localhost:6379/1``
    """
    
    def __init__(self, redis_uri, timeout=2):
        ConnectionManager.__init__(self)
        
        if redis_uri.find('redis') >= 0:
            redis_uri = redis_uri.lstrip('redis://')
            host, port = redis_uri.split(':')
            port, db = port.split('/')
        else:
            host, port, db = redis_uri.split(";")
        self.server = redis.StrictRedis(host=host, port=int(port), db=int(db),
                                        password=None, socket_timeout=timeout, 
                                        connection_pool=None)
        self.logger.debug('Setup redis: %s' % self.conn)
    
    @property
    def conn(self):
        return self.server
    
    def ping(self):
        try:
            res = self.server.ping()
            self.logger.debug('Ping redis %s: %s' % (self.conn, res))
            return res
        except redis.exceptions.ConnectionError as ex:
            self.logger.error(ex)
            return False
    
    def shutdown(self):
        res = self.server.shutdown()
        self.logger.debug('Shutdown redis %s: %s' % (self.conn, res))
        return res        
    
    def info(self):
        res = self.server.info()
        return res

    def config(self, pattern='*'):
        """Get server configuration.
        
        :param pattern: configuration search pattern [default='*']
        :return: list of configurations
        """        
        res = self.server.config_get(pattern=pattern)
        return res

    def size(self):
        res = self.server.dbsize()
        self.logger.debug('Db size redis %s: %s' % (self.conn, res))
        return res

    def cleandb(self):
        res = self.server.flushdb()
        self.logger.debug('Clean redis %s: %s' % (self.conn, res))
        return res
    
    def inspect(self, pattern='*', debug=False):
        """Inspect keys in current db.
        
        :param pattern: key search pattern [default='*']
        :return: list of tuple (key, type, ttl)
        """
        #pipe = self.server.pipeline(transaction=False)
        keys = self.server.keys(pattern)

        data = []
        for key in keys:
            if debug is True:
                data.append((key, self.server.type(key), self.server.ttl(key), 
                             self.server.debug_object(key)))
            else:
                data.append((key, self.server.type(key), self.server.ttl(key)))
        return data
    
    def delete(self, pattern='*'):
        """Delete keys by pattern in current db.
        
        :param pattern: key search pattern [default='*']
        :return: list of tuple (key, type, ttl)
        """
        #pipe = self.server.pipeline(transaction=True)
        keys = self.server.keys(pattern)
        if len(keys) > 0:
            res = self.server.delete(*keys)
            #pipe.execute()
            return res
        return None
    
    def query(self, keys, ttl=False):
        """Query key list value.
        
        :param ttl: if True return for every key (value, ttl)
        :param keys: keys list from inspect
        :return: lists of keys with value
        """
        data = {}
        for key in keys:
            ktype = key[1]
            kname = key[0]
            kttl = key[2]
            
            def get_value(kvalue, kttl):
                if ttl is True:
                    return (kvalue, kttl)
                else: 
                    return kvalue
            
            if ktype == 'hash':
                data[kname] = get_value(self.server.hgetall(kname), kttl)
            elif ktype == 'list':
                items = []
                for index in xrange(0, self.server.llen(kname)):
                    items.append(self.server.lindex(kname, index))
                data[kname] = get_value(items, kttl)
            elif ktype == 'string':
                data[kname] = get_value(self.server.get(kname), kttl)
            elif ktype == 'set':
                items = []
                for item in self.server.sscan_iter(kname):
                    items.append(item)
                data[kname] = get_value(items, kttl)
            else:
                try:
                    data[kname] = get_value(self.server.get(kname), kttl)
                except:
                    data[kname] = None
        return data


'''
@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
        logging.getLogger('gibbon.util.db').debug('Ping connection OK')
    except:
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        # connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        logging.getLogger('gibbon.util.db').error('Invalidate connection')
        raise exc.DisconnectionError()
    cursor.close()
'''

class SqlManager(ConnectionManager):
    """
    :param sql_id: sql manager id
    :param db_uri: database connection string. 
                   Ex mysql+pymysql://<user>:<pwd>@<host>:<port>/<db>
    :param connect_timeout: connection timeout in seconds [default=5]
    """    
    
    def __init__(self, sql_id, db_uri, connect_timeout=5):
        ConnectionManager.__init__(self)
        
        self.logger1 = logging.getLogger('sqlalchemy.pool')
        
        self.id = sql_id
        self.db_uri = db_uri
        self.connect_timeout = connect_timeout
        
        # engine
        self.engine = None
        self.db_session = None
        
        self.ping_query = "SELECT 1"
        
    def create_simple_engine(self):
        """Create an engine with basic configuration and no connection pool """
        if not self.engine:
            args = {'connect_timeout': self.connect_timeout}
            self.engine = create_engine(self.db_uri, connect_args=args)
            self.logger1.debug('New simple engine : %s' % self.engine)
            self.db_session = sessionmaker(bind=self.engine, 
                                           autocommit=False, 
                                           autoflush=False)
            self.logger1.debug('New db session %s over engine %s' % (
                              self.db_session, self.engine))            
        else:
            raise SqlManagerError('Engine already configured')            
    
    def create_pool_engine(self, pool_size=10, 
                                 max_overflow=10, 
                                 pool_recycle=3600,
                                 pool_timeout=30):
        """Create an engine with connection pool
        :param pool_size: [optional] [default=]
        :param max_overflow: [optional] [default=]
        :param pool_recycle: [optional] [default=]
        """
        if not self.engine:
            args = {'connect_timeout': self.connect_timeout}
            self.engine = create_engine(self.db_uri,
                                        pool_size=pool_size,
                                        max_overflow=max_overflow,
                                        pool_recycle=pool_recycle,
                                        pool_timeout=pool_timeout,
                                        connect_args=args)
            self.logger1.debug('New connection pool engine : %s' % self.engine)
            
            self.db_session = sessionmaker(bind=self.engine, 
                                           autocommit=False, 
                                           autoflush=False,
                                           expire_on_commit=False)
            self.logger1.debug('New db session %s over engine %s' % (
                              self.db_session, self.engine))
        else:
            raise SqlManagerError('Engine already configured')
        
        @event.listens_for(self.engine, "connect")
        def connect(dbapi_connection, connection_record):
            connection_record.info['pid'] = os.getpid()
        
        @event.listens_for(self.engine, "checkout")
        def checkout(dbapi_connection, connection_record, connection_proxy):
            pid = os.getpid()
            if connection_record.info['pid'] != pid:
                connection_record.connection = connection_proxy.connection = None
                error = "Connection record belongs to pid %s, "\
                        "attempting to check out in pid %s" % \
                        (connection_record.info['pid'], pid)
                self.logger1.error(error)
                raise exc.DisconnectionError(error)
                
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute(self.ping_query)
                self.logger1.debug('Ping connection OK')
            except:
                # optional - dispose the whole pool
                # instead of invalidating one at a time
                # connection_proxy._pool.dispose()
        
                # raise DisconnectionError - pool will try
                # connecting again up to three times before raising.
                connection_record.connection = connection_proxy.connection = None
                self.logger1.error('Invalidate connection')
                raise exc.DisconnectionError('Connection ping fails')
            cursor.close()             

    def get_engine(self):
        return self.engine
    
    def ping(self):
        """Ping dbms engine"""
        connection = None
        try:
            connection = self.engine.connect()
            connection.execute(self.ping_query)
            self.logger.debug('Ping dbms %s: OK' % self.engine)
            return True
        except Exception as ex:
            self.logger.error('Ping dbms %s: KO - %s' % (self.engine, ex))
            return False
        finally:
            if connection is not None:
                connection.close()
                
    
    def invalidate_connection_pool(self):
        self.engine.dispose()
        
    def get_tables_names(self):
        """Get list of tables name """
        tables = self.engine.table_names()
        self.logger.debug("Get table list: %s" % tables)
        return tables
    
    def get_table_description(self, table_name):
        """Describe a table.
        
        :param table_name: name of the table
        :return: list of columns description (name, type, default, is index, 
                                              is nullable, is primary key,
                                              is unique)
        """
        from sqlalchemy import Table, MetaData
        metadata = MetaData()
        table_obj = Table(table_name, metadata, autoload=True, 
                          autoload_with=self.engine)
        self.logger.debug("Get description for table %s" % (table_name))
        return [(c.name, str(c.type), c.default, c.index, c.nullable, 
                 c.primary_key, c.unique) for c in table_obj.columns]
    
    def count_table_rows(self, table_name, where=None):
        """Count table rows
        
        :param table_name: name of the table to query [optional]
        :param where: query filter [optional]
        :return: rows count
        :raise SqlManagerError:
        """
        query = "SELECT COUNT(*) FROM %s" % (table_name)
        if where is not None:
            query = "%s WHERE %s" % (query, where)
        
        try:
            # get total number of table rows
            connection = self.engine.connect()
            result = connection.execute(query)
            count = result.fetchone()[0]
            self.logger.debug("Table %s rows count: %s" % (table_name, count))
            connection.close()
            
            return count
        except Exception as ex:
            err = 'Mysql query %s error: %s' % (query, ex)
            self.logger.error(err)
            raise SqlManagerError(err)
    
    def query_table(self, table_name, where=None, fields="*", 
                          rows=100, offset=0):
        """Query a table
        
        :param table_name: name of the table to query [optional]
        :param where: query filter [optional]
        :param fields: list of fields to include in table qeury [optional]
        :param rows: number of rows to fetch [default=100]
        :param offset: row fecth offset [default=0]
        :return: query rows
        :raise SqlManagerError:
        """
        if fields is not None:
            fields = ",".join(fields)
        
        query = "SELECT %s FROM %s ORDER BY id" % (fields, table_name)
        if where is not None:
            query = "%s WHERE %s" % (query, where)
        
        query = "%s LIMIT %s OFFSET %s" % (query, rows, offset)    
        
        # get columns name
        col_names = [c[0] for c in self.get_table_description(table_name)]
        
        try:
            rows = []
            # query tables
            connection = self.engine.connect()
            result = connection.execute(query)
            for row in result:
                cols = {}
                i = 0
                for col in row:
                    if type(col) is datetime:
                        col = str(col)
                    if type(col) is str and col.find('"') > -1:
                        col = str(json.loads(col))
                    cols[col_names[i]] = col
                    i += 1
                rows.append(cols)
            connection.close()
            self.logger.debug("Execute query %s: %s" % (query, len(rows)))
            return rows
        except Exception as ex:
            err = 'Mysql query %s error: %s' % (query, ex)
            self.logger.error(err)
            raise SqlManagerError(err)
    
    def get_connection(self):
        try:
            if self.engine:
                conn = self.engine.connect()
                return conn
            raise SqlManagerError("There isn't active db session to use. \
                                     Session can not be opened.")  
        except exc.DBAPIError, e:
            # an exception is raised, Connection is invalidated. Connection 
            # pool will be refresh
            if e.connection_invalidated:
                self.logger1.warning("Connection was invalidated!")
                #raise SqlManagerError("Connection was invalidated! Try to reconnect")
                self.engine.connect()
    
    def release_connection(self, conn):
        conn.close()
        #self.logger1.debug("Release connection %s to poll %s." % (conn, self.engine))
        
    def get_session(self):
        """Open a database session.
        
        return session object
        """
        try:
            if self.db_session:
                session = self.db_session()
                # workaround when use sqlalchemy and flask-sqlalchemy
                # session._model_changes = {}
                self.logger1.debug("Open session: %s" % (session))
                return session
            raise SqlManagerError("There isn't active db session to use. \
                                     Session can not be opened.")
        except (exc.DBAPIError, Exception), e:
            self.logger1.error(e)
            # an exception is raised, Connection is invalidated. Connection 
            # pool will be refresh
            #if e.connection_invalidated:
            #    self.logger1.warning("Connection was invalidated! Try to reconnect")
            #    self.engine.connect()
            raise SqlManagerError(e)
            
    def release_session(self, session):        
        """Close active database session.
        
        :param session: active session to close
        """
        if session is not None:
            session.close()
            self.logger1.debug("Release session: %s" % (session))

class MysqlManager(SqlManager):
    def __init__(self, mysql_id, db_uri, connect_timeout=5):
        """
        :param mysql_id: mysql manager id
        :param db_uri: database connection string. 
                       Ex mysql+pymysql://<user>:<pwd>@<host>:<port>/<db>
        :param connect_timeout: connection timeout in seconds [default=5]
        """
        SqlManager.__init__(self, mysql_id, db_uri, connect_timeout)
        
        self.ping_query = "SELECT 1"
        
class PostgresManager(SqlManager):
    def __init__(self, mysql_id, db_uri, connect_timeout=5):
        """
        :param mysql_id: mysql manager id
        :param db_uri: database connection string. 
                       Ex mysql+pymysql://<user>:<pwd>@<host>:<port>/<db>
        :param connect_timeout: connection timeout in seconds [default=5]
        """
        SqlManager.__init__(self, mysql_id, db_uri, connect_timeout)
        
        self.ping_query = "SELECT 1"        