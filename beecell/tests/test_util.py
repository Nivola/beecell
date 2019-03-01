# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

import logging
import os
import unittest
import pprint
import time
import json
import urllib, urllib2
import httplib
import yaml
from beecell.logger import LoggerHelper
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from beecell.simple import dict_get

logger = logging.getLogger(__name__)


class BeecellTestCase(unittest.TestCase):
    """Helper class to run test
    """
    logger = logging.getLogger(u'beecell.test.log')
    runlogger = logging.getLogger(u'beecell.test.run')
    pp = pprint.PrettyPrinter(width=200)
    logging.addLevelName(60, u'TESTPLAN')
    logging.addLevelName(70, u'TEST')

    main_config_file = None
    spec_config_file = None
    validation_active = False
    run_test_user = u'test1'

    @classmethod
    def setUpClass(cls):
        logger.log(60, u'#################### Testplan %s - START ####################' % cls.__name__)
        self = cls

        # load configs
        try:
            home = os.path.expanduser(u'~')
            if self.main_config_file is None:
                config_file = u'%s/beecell.yml' % home
                self.main_config_file = config_file
            else:
                config_file = self.main_config_file
            config = self.load_file(config_file)
            logger.info(u'Get beecell test configuration: %s' % config_file)
        except Exception as ex:
            raise Exception(u'Error loading config file. Search in user home. %s' % ex)

        self.test_config = config

    @classmethod
    def tearDownClass(cls):
        logger.log(60, u'#################### Testplan %s - STOP ####################' % cls.__name__)

    def setUp(self):
        logger.log(70, u'========== %s ==========' % self.id()[9:])
        self.start = time.time()

    def tearDown(self):
        elapsed = round(time.time() - self.start, 4)
        logger.log(70, u'========== %s ========== : %ss' % (self.id()[9:], elapsed))

    @classmethod
    def load_file(cls, file_config):
        f = open(file_config, u'r')
        config = f.read()
        if file_config.find(u'.json') > 0:
            config = json.loads(config)
        elif file_config.find(u'.yml') > 0:
            config = yaml.load(config, Loader=yaml.Loader)
        f.close()
        return config

    def convert(self, data, separator=u'.'):
        if isinstance(data, dict):
            for k, v in data.items():
                data[k] = self.convert(v, separator)

        elif isinstance(data, list):
            datal = []
            for v in data:
                datal.append(self.convert(v, separator))
            data = datal

        elif isinstance(data, str) or isinstance(data, unicode):
            if data.find(u'$REF$') == 0:
                data = dict_get(self.test_config, data.lstrip(u'$REF$'), separator)

        return data

    def conf(self, key, separator=u'.'):
        res = dict_get(self.test_config, key, separator)
        if isinstance(res, dict):
            for k, v in res.items():
                res[k] = self.convert(v, separator)
        return res

    def open_mysql_session(self, db_uri):
        engine = create_engine(db_uri)
        db_session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
        return db_session

    def http_client(self, base_url, params):
        req_params = urllib.urlencode(params)
        timeout = 30
        f = urllib2.urlopen(base_url, req_params, timeout)
        response = f.read()
        f.close()
        self.logger.debug(u'Send http request to %s' % base_url)
        return response

    def http_client2(self, proto, host, path, method, data='', headers={}, port=80, timeout=30):
        """Http client. 
        
        Usage:
            
            res = http_client2('https', 'host1', '/api', 'POST', port=443, data='', headers={})        
        
        :param proto: Request proto. Ex. http, https
        :param host: Request host. Ex. 10.102.90.30
        :param port: Request port. [default=80]
        :param path: Request path. Ex. /api/
        :param method: Request method. Ex. GET, POST, PUT, DELETE
        :param headers: Request headers. [default={}]. Ex. 
            {"Content-type": "application/x-www-form-urlencoded", Accept": "text/plain"}
        :param data: Request data. [default={}]. Ex. 
            '@number': 12524, '@type': 'issue', '@action': 'show'}
        :param timeout: Request timeout. [default=30s]
        """
        self.logger.debug(u'Send http %s request to %s://%s:%s%s' % (method, proto, host, port, path))
        if proto == u'http':       
            conn = httplib.HTTPConnection(host, port, timeout=timeout)
        else:
            conn = httplib.HTTPSConnection(host, port, timeout=timeout)
        conn.request(method, path, data, headers)
        response = conn.getresponse()
        self.logger.debug(u'Response status: %s %s' % (response.status, response.reason))
        if response.status in [200, 400]:
            res = response.read()
            if headers[u'Accept'] == u'json':
                res_dict = json.loads(res)
                self.logger.debug(u'Response data: \n %s' % self.pp.pformat(res_dict))
                return res_dict
            else:
                self.logger.debug(u'Response data: \n %s' % res)
                return res
        conn.close()
        return None
    
    def send_api_request(self, path, method, data='', headers={}):
        res = self.http_client2(self.proto, self.host, path, method, port=self.port, data=data, headers=headers)
        return res


def configure_test(log_file_name=u'test'):
    """Configure est

    :param log_file_name: log file name
    """
    home = os.path.expanduser(u'~')
    log_file = u'%s/%s.log' % (home, log_file_name)
    watch_file = u'%s/%s.watch' % (home, log_file_name)
    # run_file = u'%s/%s.run' % (home, log_file_name)

    logging.captureWarnings(True)

    loggers = [
        logging.getLogger(u'beecell.perf'),
    ]
    LoggerHelper.file_handler(loggers, logging.DEBUG, watch_file, frmt=u'%(message)s')

    # loggers = [
    #     logging.getLogger(u'beecell.test.run'),
    # ]
    # LoggerHelper.file_handler(loggers, logging.DEBUG, run_file, frmt=u'%(message)s')

    # setting logger
    frmt = u'%(asctime)s - %(levelname)s - %(message)s'
    loggers = [
        logging.getLogger(u'beecell')
    ]
    LoggerHelper.file_handler(loggers, logging.DEBUG, log_file, frmt=frmt)


def runtest(testcase_class, tests):
    """Run test. Accept as external input args:

    :param testcase_class: test class
    :param tests: test list
    """
    configure_test()

    # run test suite
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(unittest.TestSuite(map(testcase_class, tests)))
