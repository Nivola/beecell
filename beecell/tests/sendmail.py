# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

from beecell.sendmail import Mailer
from beecell.tests.test_util import runtest
from beecell.tests.test_util import BeecellTestCase


tests = [
    'test_send'
]


class MailerTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

        self.mailer = Mailer(self.conf('sendmail.mailer'))

    def tearDown(self):
        BeecellTestCase.tearDown(self)

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
        me = self.conf('sendmail.sender')
        # you == the recipient's email address
        you = self.conf('sendmail.receiver')
        
        self.mailer.send(me, you, 'test', text, html)


if __name__ == '__main__':
    runtest(MailerTestCase, tests)
