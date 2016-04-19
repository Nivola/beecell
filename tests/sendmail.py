'''
Created on Sep 2, 2013

@author: darkbk
'''
import logging
import unittest
import traceback
import random
import pprint
from gibbonutil.perf import watch_test
from gibbonutil.logger import Event, JobEvent, LoggerHelper, AMQPHandlerError
from gibbonutil.sendmail import Mailer

class MailerTestCase(unittest.TestCase):
    logger = logging.getLogger('gibbon.test')

    def setUp(self):
        self.logger.debug('\n########## %s.%s ##########' % 
                          (self.__module__, self.__class__.__name__))
        
        self.logging_level = logging.DEBUG
        self.mailer = Mailer('mailfarm-app.csi.it')
        
    def tearDown(self):
        pass

    @watch_test
    def test_send(self):
        # Create the body of the message (a plain-text and an HTML version).
        text = "Hi!\nHow are you?\nHere is the link you wanted:\nhttps://www.python.org"
        html = """\
        <html>
          <head></head>
          <body>
            <p>Hi!<br>
               How are you?<br>
               Here is the <a href="https://www.python.org">link</a> you wanted.
            </p>
          </body>
        </html>
        """
        
        # me == the sender's email address
        me = 'sergio.tonani@csi.it'
        # you == the recipient's email address
        you = 'sergio.tonani@csi.it'
        
        self.mailer.send(me, you, 'test', text, html)

def test_suite():
    tests = [
             'test_send',
            ]
    return unittest.TestSuite(map(MailerTestCase, tests))

if __name__ == '__main__':
    import os
    from gibbonutil.test_util import run_test
    syspath = os.path.expanduser("~")
    log_file = '/tmp/test.log'
    
    run_test([test_suite()], log_file)    