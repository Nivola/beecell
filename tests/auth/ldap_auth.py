'''
Created on Oct 11, 2014

@author: darkbk
'''
import unittest
from tests.test_util import run_test, UtilTestCase
from gibbonutil.auth import LdapAuth, SystemUser

class LdapAuthTestCase(UtilTestCase):
    def setUp(self):
        UtilTestCase.setUp(self)


        self.auth_provider = LdapAuth(self.ldap_host, self.ldap_domain, 
                                      SystemUser, port=self.ldap_port, 
                                      timeout=self.ldap_timeout, ssl=False, 
                                      dn=self.dn)
        #self.user = "admin@clskdom.lab"
        #self.password = "admin_01"
        self.user = ""
        self.password = ""
        
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