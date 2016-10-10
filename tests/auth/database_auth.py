'''
Created on Oct 11, 2014

@author: darkbk
'''
import unittest
from tests.test_util import run_test, UtilTestCase
from beecell.auth import DatabaseAuth, SystemUser

class LdapAuthTestCase(UtilTestCase):
    def setUp(self):
        UtilTestCase.setUp(self)


        self.auth_provider = DatabaseAuth(self.auth_manager, self.conn_manager, 
                                          SystemUser)
        self.user = "admin@local"
        self.password = "testlab"
        
    def tearDown(self):
        UtilTestCase.tearDown(self)

    def test_login(self):
        self.auth_provider.login(self.user, self.password)

def test_suite():
    tests = [
             "test_login",
            ]
    return unittest.TestSuite(map(LdapAuthTestCase, tests))

if __name__ == '__main__':
    run_test([test_suite()])