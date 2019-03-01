# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
import logging
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Mailer(object):
    def __init__(self, mailserver):
        self.logger = logging.getLogger(self.__class__.__module__ + u'.' + self.__class__.__name__)
        
        self.mailserver = mailserver
        
    def send(self, me, you, subject, text, html):
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart()
        msg[u'Subject'] = subject
        msg[u'From'] = me
        msg[u'To'] = you
        
        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, u'plain')
        part2 = MIMEText(html, u'html')
        
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)
        self.logger.debug(u'Prepare email message: %s' % msg)
        
        # Send the message via local SMTP server.
        s = SMTP(self.mailserver)
        self.logger.debug(u'Configure sendmail server: %s' % s)

        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(me, you, msg.as_string())
        s.quit()
        
        self.logger.debug(u'Send email "%s" from %s to %s' % (subject, me, you))
