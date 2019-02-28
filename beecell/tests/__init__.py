# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

import os
import gevent.monkey
from beehive.common.log import ColorFormatter
from beehive.common.apiclient import BeehiveApiClient
import xmltodict
import httplib
gevent.monkey.patch_all()

import logging
import unittest
import pprint
import time
import json
import urllib
import redis
import re
from beecell.logger import LoggerHelper
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
# from beecell.test.runner import TextTestRunner
from beecell.remote import RemoteClient, ServerErrorException,\
    UnsupporteMediaTypeException, ConflictException, TimeoutException,\
    NotAcceptableException, MethodNotAllowedException, NotFoundException,\
    ForbiddenException, BadRequestException, UnauthorizedException
from base64 import b64encode
import requests
from beecell.swagger import ApiValidator
from flex.core import load
from requests.auth import HTTPBasicAuth
#from requests import Request, Session

logger = logging.getLogger(__name__)

def assert_exception(exception):
    def wrapper(fn):
        def decorated(self, *args, **kwargs):
            self.assertRaises(exception, fn, self, *args, **kwargs)
        return decorated
    return wrapper

class BeecellTestCase(unittest.TestCase):
    logger = logging.getLogger(u'beecell.test.log')
    pp = pprint.PrettyPrinter(width=200)

    @classmethod
    def setUpClass(cls):
        logger.info(u'#################### Testplan %s - START ####################' % cls.__name__)
        self = cls

        # ssl
        #path = os.path.dirname(__file__).replace(u'beehive/common', u'beehive/tests')
        #pos = path.find(u'tests')
        #path = path[:pos+6]

        # load config
        try:
            #config = self.load_config(u'%s/params.json' % path)
            home = os.path.expanduser(u'~')
            config = self.load_config(u'%s/beecell.json' % home)
            logger.info(u'get beehive test configuration')
        except Exception:
            logger.error(u'Config file beecell.json was not find in user '\
                            u'home or is malformed', exc_info=1)
            raise Exception(u'Config file beecell.json was not find in user '\
                            u'home or is malformed')
        
        env = config.get(u'env')
        config = config.get(env)
        
        # mysql
        self.mysql = config.get(u'mysql')
        
        # redis
        self.redis_uri = config.get(u'redis').get(u'uri', u'')
        self.redis_cluster = config.get(u'redis').get(u'cluster', u'')

        # ldap server
        ldap = config.get(u'ldap')
        ldap_domain = u'ad.provincia.torino.it'
        ldap = ldap.get(ldap_domain)
        self.ldap_host = ldap.get(u'host')
        self.ldap_port = ldap.get(u'port')
        self.ldap_domain = ldap_domain
        self.ldap_timeout = ldap.get(u'timeout')
        self.dn = ldap.get(u'dn')         
      

    @classmethod
    def tearDownClass(cls):
        logger.info(u'#################### Testplan %s - STOP ####################' % cls.__name__)

    @classmethod
    def load_config(cls, file_config):
        f = open(file_config, u'r')
        config = f.read()
        config = json.loads(config)
        f.close()
        return config
        
    def setUp(self):
        logger.info(u'========== %s ==========' % self.id()[9:])          
        self.start = time.time()
        
    def tearDown(self):
        elapsed = round(time.time() - self.start, 4)
        logger.info(u'========== %s ========== : %ss\n' % (self.id()[9:], elapsed))         
    
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

def runtest(testcase_class, tests):
    log_file = u'/tmp/test.log'
    
    logging.captureWarnings(True)    
    
    #setting logger
    #frmt = "%(asctime)s - %(levelname)s - %(process)s:%(thread)s - %(message)s"
    frmt = u'%(asctime)s - %(levelname)s - %(message)s'
    loggers = [
        logging.getLogger(u'beecell'),
    ]
    LoggerHelper.file_handler(loggers, logging.DEBUG, log_file, frmt=frmt, 
                              formatter=ColorFormatter)
    
    # run test suite
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(unittest.TestSuite(map(testcase_class, tests)))