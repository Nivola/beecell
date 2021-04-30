# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte

import logging
from sshtunnel import SSHTunnelForwarder
from time import sleep
import redis
import os
import ujson as json
from redis.sentinel import Sentinel
from sqlalchemy import create_engine, exc, event, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from beecell.simple import truncate


class SqlManagerError(Exception):
    pass


class RedisManagerError(Exception):
    pass


class MysqlManagerError(Exception):
    pass


class ConnectionManager(object):
    """Abstract Connection manager
    """
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__module__+ '.' + self.__class__.__name__)

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

    :param str redis_uri: redis connection uri.
    :param int timeout: redis connection timeout [default=2]
    :param list sentinels: list of (sentinel ip, sentinel port)
    :param str sentinel_name: sentinel group name
    :param str sentinel_pwd: sentinel password
    :return: RedisManager instance

    :Example:

    - redis_uri:
        - ``redis://localhost:6379/1``
        - ``localhost:6379:1``
        - ``redis-cluster://localhost:6379,localhost:6380``
    """
    def __init__(self, redis_uri, timeout=2, max_connections=200, sentinels=None, sentinel_name=None,
                 sentinel_pwd=None, db=0, pwd=None):
        ConnectionManager.__init__(self)
        
        self.is_single = False
        self.is_cluster = False
        self.is_sentinel = False
        self.sentinel_name = sentinel_name
        self.server = None
        self.socket_timeout = 0.1
        self.db = db
        self.pwd = pwd
        self.max_connections = max_connections
        self.timeout = timeout
        self.hosts = []

        # redis sentinels
        if sentinels is not None:
            self.is_sentinel = True
            if sentinel_name is None:
                raise RedisManagerError('sentinel group name must be specified')
            if sentinel_pwd is None:
                raise RedisManagerError('sentinel password must be specified')
            sentinel_kwargs = {'password': sentinel_pwd}
            self.sentinel = Sentinel(sentinels, socket_timeout=self.socket_timeout, sentinel_kwargs=sentinel_kwargs)
            self.sentinel_name = sentinel_name

        # single redis node
        elif redis_uri.find('redis') >= 0:
            self.is_single = True            
            pwd = None
            if redis_uri.find('@') > 0:
                redis_uri = redis_uri.replace('redis://:', '')
                pwd, redis_uri = redis_uri.split('@')
            else:
                redis_uri = redis_uri.replace('redis://', '')
            host, port = redis_uri.split(':')
            self.hosts = [redis_uri]
            port, db = port.split('/')
            self.server = redis.StrictRedis(host=host, port=int(port), db=int(db), password=pwd,
                                            socket_timeout=timeout, retry_on_timeout=False, connection_pool=None,
                                            max_connections=max_connections)

        # single redis node
        else:
            self.is_single = True
            host, port, db = redis_uri.split(';')
            self.hosts = ['%s:%s' % (host, port)]
            self.server = redis.StrictRedis(host=host, port=int(port), db=int(db), password=None,
                                            socket_timeout=timeout, retry_on_timeout=False, connection_pool=None,
                                            max_connections=max_connections)
    
    @property
    def conn(self):
        if self.is_sentinel is True:
            self.server = self.sentinel.master_for(self.sentinel_name, socket_timeout=self.socket_timeout,
                                                   db=int(self.db), password=self.pwd, retry_on_timeout=False,
                                                   connection_pool=None, max_connections=self.max_connections)
        return self.server

    def ping(self):
        try:
            res = self.conn.ping()
            if self.is_cluster is True and res == {}:
                res = {host: False for host in self.hosts}
            self.logger.debug('Ping redis %s: %s' % (self.conn, res))
            return res
        except redis.exceptions.ConnectionError as ex:
            self.logger.error(ex)
            return False

    def sentinel_ping(self):
        try:
            res = []
            for conn in self.sentinel.sentinels:
                conn_args = conn.connection_pool.connection_kwargs
                res.append(('%s:%s' % (conn_args['host'], conn_args['port']), conn.ping()))
                self.logger.debug('Ping redis sentinel %s: %s' % (conn, res))
            return res
        except redis.exceptions.ConnectionError as ex:
            self.logger.error(ex)
            return False

    def sentinel_discover(self):
        res = {'master': None, 'slave': None}
        if self.is_sentinel is True:
            res['master'] = self.sentinel.discover_master(self.sentinel_name)
            res['slave'] = self.sentinel.discover_slaves(self.sentinel_name)
        return res

    def sentinel_status(self):
        '''
        "role": "master",
        "connected_slaves": 1,
        "min_slaves_good_slaves": 1,
        "slave0": {
            "ip": "10.138.144.114",
            "port": 6379,
            "state": "online",
            "offset": 83359,
            "lag": 1
        },
        "master_failover_state": "no-failover",


        :return:
        '''
        resp = {}
        if self.conn is not None:
            info = self.info()
            min_replicas_to_write = int(self.conn.config_get(pattern='min-replicas-to-write')
                                        .get('min-replicas-to-write', 0))
            min_slaves_good_slaves = int(info.get('min_slaves_good_slaves'))
            status = False
            if min_slaves_good_slaves >= min_replicas_to_write:
                status = True
            master = self.sentinel.discover_master(self.sentinel_name)
            master = {'ip': master[0], 'port': master[1]}
            connected_slaves = info.get('connected_slaves')
            slaves = []
            for i in range(int(connected_slaves)):
                slaves.append(info.get('slave%s' % i))
            resp = {
                'status': status,
                'master': master,
                'slaves': slaves,
                'connected_slaves': info.get('connected_slaves'),
                'min_slaves_good_slaves': min_slaves_good_slaves,
                'master_failover_state': info.get('master_failover_state'),
                'master_repl_offset': info.get('master_repl_offset'),
            }
        return resp

    def shutdown(self):
        res = self.conn.shutdown()
        self.logger.debug('Shutdown redis %s: %s' % (self.conn, res))
        return res        
    
    def info(self):
        res = self.conn.info()
        self.logger.debug('Get redis %s info: %s' % (self.conn, res))
        return res

    def config(self, pattern='*'):
        """Get server configuration.
        
        :param pattern: configuration search pattern [default='*']
        :return: list of configurations
        """        
        res = self.conn.config_get(pattern=pattern)
        return res

    def size(self):
        res = self.conn.dbsize()
        self.logger.debug('Db size redis %s: %s' % (self.conn, res))
        return res

    def cleandb(self):
        res = self.conn.flushdb()
        self.logger.debug('Clean redis %s: %s' % (self.conn, res))
        return res
    
    def inspect(self, pattern='*', debug=False):
        """Inspect keys in current db.
        
        :param pattern: key search pattern [default='*']
        :return: list of tuple (key, type, ttl)
        """
        keys = self.conn.keys(pattern)
        # self.conn.scan()

        data = []
        for key in keys:
            if debug is True:
                data.append((key, self.conn.type(key), self.conn.ttl(key), self.conn.debug_object(key)))
            else:
                data.append((key, self.conn.type(key), self.conn.ttl(key)))
        return data

    def scan(self, pattern='*', cursor=0, count=10):
        """Scan keys in current db.

        :param pattern: key search pattern [default='*']
        :param cursor: start cursor position [default=0]
        :param count: keys max number returned [default=10]
        :return: list of tuple (key, type, ttl)
        """
        keys = self.conn.scan(cursor=cursor, match=pattern, count=count)
        return keys
    
    def delete(self, pattern='*'):
        """Delete keys by pattern in current db.
        
        :param pattern: key search pattern [default='*']
        :return: list of tuple (key, type, ttl)
        """
        keys = self.conn.keys(pattern)
        if len(keys) > 0:
            res = self.conn.delete(*keys)
            return res
        return None

    def delete_key(self, key):
        """Delete keys by pattern in current db.

        :param key: redis key
        :return: None
        """
        self.conn.delete(key)
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
                data[kname] = get_value(self.conn.hgetall(kname), kttl)
            elif ktype == 'list':
                items = []
                for index in range(0, self.conn.llen(kname)):
                    items.append(self.conn.lindex(kname, index))
                data[kname] = get_value(items, kttl)
            elif ktype == 'string':
                data[kname] = get_value(self.conn.get(kname), kttl)
            elif ktype == 'set':
                items = []
                for item in self.conn.sscan_iter(kname):
                    items.append(item)
                data[kname] = get_value(items, kttl)
            else:
                try:
                    data[kname] = get_value(self.conn.get(kname), kttl)
                except:
                    data[kname] = None
        return data

    def get(self, key):
        """Query key value.

        :param key: key to get
        :return: lists of keys with value
        """
        return self.conn.get(key)

    def ttl(self, key):
        """Query key ttl.

        :param keys: key to get
        :return: lists of keys with value
        """
        return self.conn.ttl(key)

    def gets(self, keys):
        """Query key list value.

        :param ttl: if True return for every key (value, ttl)
        :param keys: keys list from inspect
        :return: lists of keys with value
        """
        return self.conn.mget(keys)

    def set(self, key, value):
        """Set key value.

        :param key: key to insert
        :param value: value to insert
        :return:
        """
        return self.conn.set(key, value)

    def get_with_ttl(self, key, max_retry=3, delay=0.01):
        """Get task from redis

        :param task_id: redis key
        :param max_retry: max get retry if value is None [default=3]
        :param delay: time to wait between two retry [default=0.01]
        :return: value
        :raise RedisManagerError: if key was not found
        """
        def get_data(key):
            task_data = self.conn.get(key)
            task_ttl = self.conn.ttl(key)
            return task_data, task_ttl

        retry = 0
        while retry < max_retry:
            task_data, task_ttl = get_data(key)
            if task_data is not None:
                return task_data, task_ttl
            sleep(delay)
            retry += 1

        err = 'Key %s not found' % key
        raise RedisManagerError(err)


class SqlManager(ConnectionManager):
    """
    :param sql_id: sql manager id
    :param db_uri: database connection string. Ex. mysql+pymysql://<user>:<pwd>@<host>:<port>/<db>
    :param connect_timeout: connection timeout in seconds [default=5]
    """
    def __init__(self, sql_id, db_uri, connect_timeout=5):
        ConnectionManager.__init__(self)
        
        self.logger1 = logging.getLogger('sqlalchemy.pool')
        
        self.id = sql_id
        self.db_uri = db_uri
        self.orig_db_uri = db_uri
        self.connect_timeout = connect_timeout
        
        # engine
        self.engine = None
        self.db_session = None

        # ssh tunnel
        self.tunnel = None
        
        self.ping_query = "SELECT 1"

    def create_tunnel(self, host, pwd, user='root', port=22):
        # parse db_uri
        # mysql+pymysql://<user>:<pwd>@<host>:<port>/<db>
        db_host, db_port = self.db_uri.split('@')[1].split(':')
        db_port = int(db_port.split('/')[0])

        self.tunnel = SSHTunnelForwarder(
            logger=self.logger,
            ssh_address_or_host=(host, port),
            ssh_username=user,
            ssh_password=pwd,
            remote_bind_address=(db_host, db_port),
        )
        self.tunnel.start()
        self.orig_db_uri = self.db_uri
        self.db_uri.replace(db_host, '127.0.0.1').replace(db_port, self.tunnel.local_bind_port)

    def close_tunnel(self):
        self.tunnel.stop()
        self.db_uri = self.orig_db_uri

    def create_simple_engine(self):
        """Create an engine with basic configuration and no connection pool """
        if not self.engine:
            args = {'connect_timeout': self.connect_timeout}
            self.engine = create_engine(self.db_uri, connect_args=args)
            self.logger1.debug('New simple engine : %s' % self.engine)
            self.db_session = sessionmaker(bind=self.engine, autocommit=False, autoflush=True, expire_on_commit=True)
            self.logger1.debug('New db session %s over engine %s' % (self.db_session, self.engine))
        else:
            raise SqlManagerError('Engine already configured')            
    
    def create_pool_engine(self, pool_size=10, max_overflow=10, pool_recycle=3600, pool_timeout=30):
        """Create an engine with connection pool

        :param pool_size: [optional] [default=]
        :param max_overflow: [optional] [default=]
        :param pool_recycle: [optional] [default=]
        """
        if not self.engine:
            args = {'connect_timeout': self.connect_timeout}
            self.engine = create_engine(self.db_uri, pool_size=pool_size, max_overflow=max_overflow,
                                        pool_recycle=pool_recycle, pool_timeout=pool_timeout, connect_args=args)
            self.logger1.debug('New connection pool engine : %s' % self.engine)
            
            self.db_session = sessionmaker(bind=self.engine, autocommit=False, autoflush=True, expire_on_commit=True)
            self.logger1.debug('New db session %s over engine %s' % (self.db_session, self.engine))
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
                error = "Connection record belongs to pid %s, attempting to check out in pid %s" % \
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

    def exec_statements(self, statements):
        """Exec statements defined by a function statements(connection)

        :param statements: function with signature statements(connection): ... return res
        :return: statements execution response
        """
        connection = None
        res = {}
        try:
            connection = self.engine.connect()
            res = statements(connection)
            self.logger.debug('Exec statements: %s' % truncate(res))
        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res

    def ping(self):
        """Ping dbms engine"""
        connection = None
        try:
            connection = self.engine.connect()
            self.logger.debug('Get connection : %s' % connection)
            connection.execute(self.ping_query)
            self.logger.debug('Ping dbms %s: OK' % self.engine)
            return True
        except Exception as ex:
            self.logger.error('Ping dbms %s: KO - %s' % (self.engine, ex))
            return False
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
                
    def invalidate_connection_pool(self):
        self.engine.dispose()
    
    def get_dbs(self):
        """Get dbs list
        """
        connection = None
        res = {}
        try:
            connection = self.engine.connect()
            result = connection.execute('select table_schema, count(table_name) '
                                        'from information_schema.tables group by table_schema')
            for row in result:
                res[row[0]] = {
                    'db': row[0],
                    'tables': row[1]
                }
            # add empty db
            result = connection.execute('show databases')
            for row in result:
                if row[0] not in res.keys():
                    res[row[0]] = {
                        'db': row[0],
                        'tables': 0
                    }
            res = res.values()
            self.logger.debug('Get db list: %s' % res)
            
        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res

    def add_db(self, db_name, charset=None):
        """Add db

        :param db_name: db name
        :param charset: charset [optional]
        """
        connection = None
        res = {}
        try:
            connection = self.engine.connect()
            stm = 'CREATE DATABASE IF NOT EXISTS %s' % db_name
            if charset is not None:
                stm += 'CHARACTER SET = %s' % charset
            res = connection.execute(stm)
            self.logger.debug('Create db %s: %s' % (db_name, res))
        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res

    def drop_db(self, db_name):
        """Drop db

        :param db_name: db name
        """
        connection = None
        res = {}
        try:
            connection = self.engine.connect()
            stm = 'DROP DATABASE IF EXISTS %s' % db_name
            res = connection.execute(stm)
            self.logger.debug('Drop db %s: %s' % (db_name, res))
        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res

    def get_users(self):
        """Get users list
        """
        connection = None
        res = []
        try:
            connection = self.engine.connect()
            result = connection.execute('select Host, User from mysql.user')
            for row in result:
                res.append({'host': row[0], 'user': row[1]})
            self.logger.debug('Get users list: %s' % res)
            
        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res

    def add_user(self, name, host, password):
        """Add user

        :param name: user name
        :param host: user host
        :param password: user password
        """
        connection = None
        res = {}
        try:
            connection = self.engine.connect()
            stm = text("CREATE USER IF NOT EXISTS '%s'@'%s' IDENTIFIED BY '%s'" % (name, host, password))
            connection.execute(stm)
            self.logger.debug('Create user %s: %s' % (name, res))
        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return True

    def grant_db_to_user(self, name, host, db):
        """Grant db to user

        :param name: user name
        :param host: user host
        :param db: db name to grant
        """
        connection = None
        res = {}
        try:
            connection = self.engine.connect()
            stm = text("GRANT ALL privileges ON `%s`.* TO '%s'@'%s'" % (db, name, host))
            connection.execute(stm)
            self.logger.debug('Grant schema %s to user %s: %s' % (db, name, res))
        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return True

    def drop_user(self, db_name):
        """Drop user

        :param db_name: user name
        """
        connection = None
        res = {}
        try:
            connection = self.engine.connect()
            stm = 'DROP USER IF EXISTS %s' % db_name
            res = connection.execute(stm)
            self.logger.debug('Drop user %s: %s' % (db_name, res))
        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res
        
    def get_tables_names(self):
        """Get list of tables name """
        tables = self.engine.table_names()
        self.logger.debug("Get table list: %s" % tables)
        return tables
    
    def get_db_tables(self, db):
        """Get db table list
        
        :param str db: db name
        :return: entity instance
        :raise Exception:
        """
        connection = None
        res = []
        try:
            connection = self.engine.connect()
            sql = "select table_name, table_rows, data_length, index_length, "\
                  "auto_increment from information_schema.tables where "\
                  "table_schema='%s' order by table_name"
            result = connection.execute(sql % db)
            for row in result:
                res.append({
                    'table_name': row[0],
                    'table_rows': row[1],
                    'data_length': row[2],
                    'index_length': row[3],
                    'auto_increment': row[4]
                })
            self.logger.debug('Get tables for db %s: %s' % (db, res))
            
        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res      

    def get_table_description(self, table_name):
        """Describe a table.
        
        :param table_name: name of the table
        :return: list of columns description (name, type, default, is index, is nullable, is primary key, is unique)
        """
        from sqlalchemy import Table, MetaData
        metadata = MetaData()
        table_obj = Table(table_name, metadata, autoload=True, autoload_with=self.engine)
        self.logger.debug("Get description for table %s" % (table_name))
        return [{
            'name': c.name,
            'type': str(c.type),
            'default': c.default,
            'index': c.index,
            'is_nullable': c.nullable,
            'is_primary_key': c.primary_key,
            'is_unique': c.unique} for c in table_obj.columns]
    
    def query_table(self, table_name, where=None, fields="*", rows=20, offset=0, order=None):
        """Query a table
        
        :param table_name: name of the table to query [optional]
        :param where: query filter [optional]
        :param fields: list of fields to include in table qeury [optional]
        :param rows: number of rows to fetch [default=100]
        :param offset: row fetch offset [default=0]
        :param order: field used to order records [default=None]
        :return: query rows
        :raise SqlManagerError:
        """
        res = []
        
        if fields is not None:
            fields = ",".join(fields)

        query_count = "SELECT count(*) as count FROM %s" % table_name
        if where is not None:
            query_count = "%s WHERE %s" % (query_count, where)

        query = "SELECT %s FROM %s" % (fields, table_name)
        if where is not None:
            query = "%s WHERE %s" % (query, where)

        if order is not None:
            query = "%s ORDER BY %s" % order

        query = "%s LIMIT %s OFFSET %s" % (query, rows, offset)
        
        # get columns name
        col_names = [c['name'] for c in self.get_table_description(table_name)]
        
        try:
            # query tables
            connection = self.engine.connect()
            total = connection.execute(query_count).fetchone()[0]
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
                res.append(cols)
            self.logger.debug("Execute query %s: %s" % (query, truncate(res)))
        except Exception as ex:
            err = 'Mysql query %s error: %s' % (query, ex)
            self.logger.error(err)
            raise SqlManagerError(err)
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res, total
    
    def get_connection(self):
        try:
            if self.engine:
                conn = self.engine.connect()
                return conn
            raise SqlManagerError("There isn't active db session to use. Session can not be opened.")
        except exc.DBAPIError as e:
            # an exception is raised, Connection is invalidated. Connection 
            # pool will be refresh
            if e.connection_invalidated:
                self.logger1.warning("Connection was invalidated!")
                self.engine.connect()
    
    def release_connection(self, conn):
        conn.close()
        
    def get_session(self):
        """Open a database session.
        
        :return: session object
        """
        try:
            if self.db_session:
                session = self.db_session()
                # workaround when use sqlalchemy and flask-sqlalchemy
                # session._model_changes = {}
                self.logger1.debug("Open session: %s" % (session))
                return session
            raise SqlManagerError("There isn't active db session to use. Session can not be opened.")
        except (exc.DBAPIError, Exception) as e:
            self.logger1.error(e)
            # an exception is raised, Connection is invalidated. Connection 
            # pool will be refresh
            # if e.connection_invalidated:
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
        :param db_uri: database connection string. Ex. mysql+pymysql://<user>:<pwd>@<host>:<port>/<db>
        :param connect_timeout: connection timeout in seconds [default=5]
        """
        SqlManager.__init__(self, mysql_id, db_uri, connect_timeout)
        
        self.ping_query = "SELECT 1"

    def drop_all_tables(self, db):
        """Query a table

        :param db: db
        :return: True
        :raise SqlManagerError:
        """
        start = [
            "SET FOREIGN_KEY_CHECKS = 0;",
            "SET @tables = '';",
            "SET @views = '';",
            "SET SESSION group_concat_max_len = 10240;"
        ]
        end = [
            "SET FOREIGN_KEY_CHECKS = 1"
        ]

        select_tables = "SELECT GROUP_CONCAT(table_schema, '.', table_name) FROM information_schema.tables " \
                        "WHERE table_type='BASE TABLE' and table_schema = '%s';" % db

        select_views = "SELECT GROUP_CONCAT(table_schema, '.', table_name) FROM information_schema.tables " \
                       "WHERE table_type='VIEW' and table_schema = '%s';" % db

        set_tables = "SET @tables = '%s';"
        set_views = "SET @views = '%s';"

        drop_tables = [
            "SET @tables = CONCAT('DROP TABLE ', @tables);",
            "PREPARE stmt FROM @tables;",
            "EXECUTE stmt;",
            "DEALLOCATE PREPARE stmt;"
        ]

        drop_views = [
            # "DEALLOCATE PREPARE stmt;",
            "SET @views = CONCAT('DROP VIEW ', @views);",
            "PREPARE stmt FROM @views;",
            "EXECUTE stmt;",
            "DEALLOCATE PREPARE stmt;"
        ]

        try:
            connection = self.engine.connect()
            trans = connection.begin()

            # start
            for item in start:
                connection.execute(item)

            # get tables
            res = connection.execute(select_tables)
            tables = res.fetchone()[0]
            res.close()
            self.logger.debug(tables)

            # delete tables
            if tables is not None:
                connection.execute(set_tables % tables)
                for item in drop_tables:
                    connection.execute(item)

            # get views
            res = connection.execute(select_views)
            tables = res.fetchone()[0]
            res.close()
            self.logger.debug(tables)

            # delete views
            if tables is not None:
                connection.execute(set_views % tables)
                for item in drop_views:
                    connection.execute(item)

            # end
            for item in end:
                connection.execute(item)
            trans.commit()
        except:
            trans.rollback()
            self.logger.error('Error during drop all', exc_info=True)
            raise SqlManagerError('Error during drop all')
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return None

    def get_cluster_status(self):
        """Get cluster status
        """
        connection = None
        res = {}
        try:
            connection = self.engine.connect()
            result = connection.execute('select MEMBER_HOST, MEMBER_PORT, MEMBER_STATE '
                                        'from performance_schema.replication_group_members;')
            for row in result:
                res[row[0]] = {
                    'MEMBER_HOST': row[0],
                    'MEMBER_PORT': row[1],
                    'MEMBER_STATE': row[2]
                }
            self.logger.debug('Get mysql cluster status: %s' % res)

        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res

    def get_galera_cluster_status(self):
        """Get galera cluster status
        """
        connection = None
        res = {}
        try:
            connection = self.engine.connect()
            result = connection.execute('SHOW GLOBAL STATUS LIKE \'wsrep_cluster_status\';')
            for row in result:
                res[row[0]] = row[1]

            result = connection.execute('SHOW GLOBAL STATUS LIKE \'wsrep_cluster_size\';')
            for row in result:
                res[row[0]] = row[1]

            result = connection.execute('SHOW STATUS LIKE \'wsrep_local_state_comment\';')
            for row in result:
                res[row[0]] = row[1]

            self.logger.debug('Get mariadb galera cluster status: %s' % res)

        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res

    def get_replica_master_status(self):
        """Get replica master status
        """
        connection = None
        res = {}
        try:
            connection = self.engine.connect()
            result = connection.execute('SHOW MASTER STATUS;')
            for row in result:
                res[row[0]] = row[1]

            self.logger.debug('Get mariadb replica master status: %s' % res)

        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res

    def get_replica_slave_status(self):
        """Get replica slave status
        """
        connection = None

        desc = [
            'Slave_IO_State', 'Master_Host', 'Master_User', 'Master_Port', 'Connect_Retry', 'Master_Log_File',
            'Read_Master_Log_Pos', 'Relay_Log_File', 'Relay_Log_Pos', 'Relay_Master_Log_File', 'Slave_IO_Running',
            'Slave_SQL_Running', 'Replicate_Do_DB', 'Replicate_Ignore_DB', 'Replicate_Do_Table',
            'Replicate_Ignore_Table', 'Replicate_Wild_Do_Table', 'Replicate_Wild_Ignore_Table', 'Last_Errno',
            'Last_Error', 'Skip_Counter', 'Exec_Master_Log_Pos', 'Relay_Log_Space', 'Until_Condition', 'Until_Log_File',
            'Until_Log_Pos', 'Master_SSL_Allowed', 'Master_SSL_CA_File', 'Master_SSL_CA_Path', 'Master_SSL_Cert',
            'Master_SSL_Cipher', 'Master_SSL_Key', 'Seconds_Behind_Master', 'Master_SSL_Verify_Server_Cert',
            'Last_IO_Errno', 'Last_IO_Error', 'Last_SQL_Errno', 'Last_SQL_Error', 'Replicate_Ignore_Server_Ids',
            'Master_Server_Id', 'Master_SSL_Crl', 'Master_SSL_Crlpath', 'Using_Gtid', 'Gtid_IO_Pos',
            'Replicate_Do_Domain_Ids', 'Replicate_Ignore_Domain_Ids', 'Parallel_Mode', 'SQL_Delay',
            'SQL_Remaining_Delay', 'Slave_SQL_Running_State', 'Slave_DDL_Groups', 'Slave_Non_Transactional_Groups',
            'Slave_Transactional_Groups'
        ]

        res = []
        try:
            connection = self.engine.connect()
            result = connection.execute('SHOW SLAVE STATUS;')
            for row in result:
                item = {}
                for i in range(len(row)):
                    item[desc[i]] = row[i]
                res.append(item)

            self.logger.debug('Get mariadb replica slave status: %s' % res)

        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res

    def stop_replica_on_slave(self):
        """stop replica on slave
        """
        connection = None

        res = []
        try:
            connection = self.engine.connect()
            connection.execute('STOP SLAVE;')
            self.logger.debug('stop replica on slave')

        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res

    def start_replica_on_slave(self):
        """start replica on slave
        """
        connection = None

        res = []
        try:
            connection = self.engine.connect()
            connection.execute('START SLAVE;')
            self.logger.debug('start replica on slave')

        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res

    def show_binary_log(self):
        """show binary log
        """
        connection = None

        res = {}
        try:
            connection = self.engine.connect()
            result = connection.execute('SHOW BINARY LOGS;')
            for row in result:
                res[row[0]] = row[1]
            self.logger.debug('show binary log: %s' % res)

        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res

    def purge_binary_log(self, date=None):
        """purge binary log

        :param date: specify date before you want to to make purge. Ex. 2021-01-06 [optional]
        """
        connection = None

        res = []
        try:
            if date is None:
                date = datetime.today() - timedelta(days=2)
                date = '%s-%s-%s' % (date.year, date.month, date.day)

            connection = self.engine.connect()
            connection.execute("PURGE BINARY LOGS BEFORE '%s';" % date)
            self.logger.debug('purge binary log')

        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise
        finally:
            if connection is not None:
                connection.close()
                self.engine.dispose()
        return res


class PostgresManager(SqlManager):
    def __init__(self, mysql_id, db_uri, connect_timeout=5):
        """
        :param mysql_id: mysql manager id
        :param db_uri: database connection string. Ex. mysql+pymysql://<user>:<pwd>@<host>:<port>/<db>
        :param connect_timeout: connection timeout in seconds [default=5]
        """
        SqlManager.__init__(self, mysql_id, db_uri, connect_timeout)
        
        self.ping_query = "SELECT 1"
