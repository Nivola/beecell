'''
Created on Oct 22, 2015

@author: darkbk

https://docs.python.org/2/library/email-examples.html
'''
# Import smtplib for the actual sending function
from smtplib import SMTP
from logging import getLogger

# Import the email modules we'll need
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class Mailer(object):
    def __init__(self, mailserver):
        self.logger = logging.getLogger(self.__class__.__module__+ \
                                        '.'+self.__class__.__name__)        
        
        self.mailserver = mailserver
        
    def send(self, me, you, subject, text, html):
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = me
        msg['To'] = you
        
        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)
        
        # Send the message via local SMTP server.
        s = SMTP(self.mailserver)
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(me, you, msg.as_string())
        s.quit()
        
        self.logger.debug('Send email "%s" from %s to %s' % (subject, me, you))  