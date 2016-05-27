'''
Created on Dec 9, 2013

@author: darkbk
'''
import cProfile
import logging
import unittest
import pprint
import time
import json
import urllib, urllib2
import httplib
import redis
from beecell.perf import watch_test
from beecell.logger import LoggerHelper
from beecell.db import MysqlManager
#from gibboncloudapi.model import AuthDbManager
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker

class UtilTestCase(unittest.TestCase):
    """To execute this test you need a mysql instance, a user and a 
    database associated to the user.
    """    
    logger = logging.getLogger('gibbon.test')
    pp = pprint.PrettyPrinter(width=140)

    @classmethod
    def setUpClass(cls):
        pass
        #cls._connection = createExpensiveConnectionObject()

    @classmethod
    def tearDownClass(cls):
        pass
        #cls._connection.destroy()

    def setUp(self):
        logging.getLogger('gibbon.test').info('========== %s ==========' % self.id()[9:])
        self.start = time.time()
        
        # db server
        self.db_uri = "mysql+pymysql://cloudapi:cloudapi@172.16.0.19:3308/cloudapi"
        #db_uri = "mysql+pymysql://cloudapi:cloudapi@10.102.90.203:3308/cloudapi"
        #self.auth_manager = AuthDbManager
        #self.conn_manager = MysqlManager('db_manager01', db_uri, connect_timeout=5)
        #self.conn_manager.create_simple_engine()
        
        # ldap server
        self.ldap_host = "10.102.90.200"
        self.ldap_port = 389
        #self.ldap_host = "172.16.0.19"
        #self.ldap_port = 10389
        self.ldap_domain = "clskdom.lab"
        self.ldap_timeout = 5
        
        self.ldap_host = "ad.comune.torino.it"
        self.ldap_port = 389
        self.ldap_domain = "ad.comune.torino.it"
        self.ldap_timeout = 100
        self.dn = "ou=utenze,DC=ad,DC=comune,DC=torino,DC=it"    
        
        self.ldap_host = 'ad.provincia.torino.it'
        self.ldap_port = 389
        self.ldap_domain = 'ad.provincia.torino.it'
        self.ldap_timeout = 100
        self.dn = 'ou=utenti,DC=ad,DC=provincia,DC=torino,DC=it'       
        
    def tearDown(self):
        elapsed = round(time.time() - self.start, 4)
        logging.getLogger('gibbon.test').info("========== %s ========== : %ss\n" % 
                                         (self.id()[9:], elapsed))
    
    def open_mysql_session(self, db_uri):
        engine = create_engine(db_uri)
        
        """
        engine = create_engine(app.db_uri,
                               pool_size=10, 
                               max_overflow=10,
                               pool_recycle=3600)
        """
        
        db_session = sessionmaker(bind=engine, 
                                  autocommit=False, 
                                  autoflush=False)
        return db_session

    def http_client(self, base_url, params):
        req_params = urllib.urlencode(params)
        timeout = 30
        f = urllib2.urlopen(base_url, req_params, timeout)
        response = f.read()
        f.close()
        self.logger.debug('Send http request to %s' % base_url)
        return response

    def http_client2(self, proto, host, path, method, 
                           data='', headers={}, port=80, timeout=30):
        """Http client. Usage:
            res = http_client2('https', 'host1', '/api', 'POST',
                                port=443, data='', headers={})        
        
        :param proto: Request proto. Ex. http, https
        :param host: Request host. Ex. 10.102.90.30
        :param port: Request port. [default=80]
        :param path: Request path. Ex. /api/
        :param method: Request method. Ex. GET, POST, PUT, DELETE
        :param headers: Request headers. [default={}]. Ex. 
                        {"Content-type": "application/x-www-form-urlencoded",
                         "Accept": "text/plain"}
        :param data: Request data. [default={}]. Ex. 
                       {'@number': 12524, '@type': 'issue', '@action': 'show'}
        :param timeout: Request timeout. [default=30s]
        """
        self.logger.debug('Send http %s request to %s://%s:%s%s' % 
                          (method, proto, host, port, path))
        if proto == 'http':       
            conn = httplib.HTTPConnection(host, port, timeout=timeout)
        else:
            conn = httplib.HTTPSConnection(host, port, timeout=timeout)
        conn.request(method, path, data, headers)
        response = conn.getresponse()
        self.logger.debug('Response status: %s %s' % 
                          (response.status, response.reason))
        if response.status in [200, 400]:
            res = response.read()
            if headers['Accept'] == 'json':
                res_dict = json.loads(res)
                self.logger.debug('Response data: \n %s' % self.pp.pformat(res_dict))
                return res_dict
            else:
                self.logger.debug('Response data: \n %s' % res)
                return res
        conn.close()
        return None
    
    def send_api_request(self, path, method, data='', headers={}):
        res = self.http_client2(self.proto, self.host, path, method,
                                port=self.port, data=data, headers=headers)
        return res
        #self.assertEqual(res_dict['status'], 'ok')    
        
def run_test(suite):
    log_file = '/tmp/test.log'
    watch_file = '/tmp/test.watch'
    
    #setting logger
    logger = logging.getLogger('gibbon.test')
    LoggerHelper.setup_file_handler(logger, logging.DEBUG, log_file)
    
    severLogger = logging.getLogger('beecell')
    LoggerHelper.setup_file_handler(severLogger, logging.DEBUG, log_file) 

    severLogger = logging.getLogger('beecell.perf')
    LoggerHelper.setup_file_handler(severLogger, logging.DEBUG, watch_file, frmt='%(message)s') 
    
    # run test suite
    alltests = unittest.TestSuite(suite)
    unittest.TextTestRunner(verbosity=2).run(alltests)

#if __name__ == '__main__':
# start profile over test suite
#cProfile.run('run_test()', 'log/test.profile')
#p = pstats.Stats('log/test.profile')