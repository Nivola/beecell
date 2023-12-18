# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

from email import encoders
from email.mime.base import MIMEBase
import logging
from pathlib import Path
from smtplib import SMTP, SMTP_SSL
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def check_email(email):
    logger = logging.getLogger("beecell.sendmail")
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    if email is None:
        logger.debug("Email None: %s" % email)
        return False

    import re
    if re.fullmatch(regex, email):
        logger.debug("Valid email: %s" % email)
        return True
    else:
        logger.debug("Invalid email: %s" % email)
        return False

class Mailer(object):
    def __init__(self, mailserver, mailport=None, mail_login=None, mail_pw=None):
        self.logger = logging.getLogger(self.__class__.__module__ + "." + self.__class__.__name__)

        self.mailserver = mailserver
        self.mailport = mailport
        self.mail_login = mail_login
        self.mail_pw = mail_pw

    def send(self, me, you, subject, text, html, files=None):
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = me

        if isinstance(you, str):
            msg["To"] = you
        elif isinstance(you, list):
            msg["To"] = ", ".join(you)

        # Record the MIME types of both parts - text/plain and text/html.
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        if text is not None:
            part1 = MIMEText(text, "plain")
            msg.attach(part1)

        if html is not None:
            part2 = MIMEText(html, "html")
            msg.attach(part2)

        if files is not None:
            for path in files:
                part = MIMEBase("application", "octet-stream")
                with open(path, "rb") as file:
                    part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", "attachment; filename={}".format(Path(path).name))
                msg.attach(part)

        # log raw email contents
        # self.logger.debug('Prepare email message: %s' % msg)

        # Send the message via local SMTP server.
        if self.mailport is None:
            smtp = SMTP(self.mailserver)
        else:
            smtp = SMTP_SSL(self.mailserver, self.mailport)

        if self.mail_login is not None:
            smtp.login(self.mail_login, self.mail_pw)

        self.logger.debug("Configure sendmail server: %s" % smtp)

        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        smtp.sendmail(me, you, msg.as_string())
        smtp.quit()

        self.logger.debug('Send email "%s" from %s to %s' % (subject, me, you))
