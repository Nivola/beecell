'''
Created on Sep 2, 2013

@author: darkbk
'''
import unittest
from gibbonutil.auth import extract
from tests.test_util import run_test, UtilTestCase

class PermTestCase(UtilTestCase):
    """
    """
    def setUp(self):
        UtilTestCase.setUp(self)
        
    def tearDown(self):
        UtilTestCase.tearDown(self)

    def test_extract(self):
        perms = ['a1//b1//c4//*',
                 'a1//b1//c1//*',
                 'a1//b1//c2//*',
                 'a1//b2//*//*',
                 'a2//b3//*//*',
                 'a1//b4//c3//d1',
                 'a1//*//*//*']
        #perms = ['*//*//*//*']
        perms = [u'a1//b4//c3//d1']
        #perms = [u'portal//main//statustop', u'portal//main//statusbottom', u'portal//main//menuleft']
        res = extract(perms)
        print res

def test_suite():
    tests = [
             'test_extract',       
            ]
    return unittest.TestSuite(map(PermTestCase, tests))

if __name__ == '__main__':
    run_test([test_suite()])