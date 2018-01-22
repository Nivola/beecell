"""
Created on Jan 19, 2018

@author: darkbk
"""
import unittest
from beecell.auth import extract
from beecell.db.manager import RedisManager, MysqlManager
from beecell.tests.test_util import run_test, UtilTestCase
import pprint
import redis_collections
from beecell.tests import BeecellTestCase, runtest
from beecell.paramiko_shell.shell import ParamikoShell

tests = [
    u'test_run_with_password',
    u'test_run_with_keyfile',
    u'test_run_with_keystring'
]


class ShellTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

        self.port = 22
        self.user = u'root'
        self.pwd = u'cs1$topix'
        self.host = u'10.102.184.69'
        self.keyfile = u'/home/io/workspace/git/clos-scripts/clos-scripts/beehive/inventories/lab5/.ssh/id_rsa'
        self.key_string = """-----BEGIN RSA PRIVATE KEY-----
        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
        -----END RSA PRIVATE KEY-----"""

    def tearDown(self):
        BeecellTestCase.tearDown(self)

    def test_run_with_password(self):
        self.client = ParamikoShell(self.host, self.user, pwd=self.pwd)
        self.client.run()

    def test_run_with_keyfile(self):
        self.client = ParamikoShell(self.host, self.user, keyfile=self.keyfile)
        self.client.run()

    def test_run_with_keystring(self):
        self.client = ParamikoShell(self.host, self.user, keystring=self.key_string)
        self.client.run()


if __name__ == u'__main__':
    runtest(ShellTestCase, tests)
