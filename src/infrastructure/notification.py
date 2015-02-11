import logging

from domain.notification import NotificationService


class EmailNotificationService(NotificationService):
    def __init__(self, email_gateway, sender, recipient):
        self._email_gateway = email_gateway
        self._sender = sender
        self._recipient = recipient
        self._template = """From: %s <%s>
To: %s <%s>
Subject: %s

%s
"""

    def send_message(self, subject, message):
        formatted_message = self._template % (self._sender, self._sender, self._recipient, self._recipient, subject, message)
        try:
            logging.info("Sending email message")
            self._email_gateway.send_email(self._sender, [self._recipient], formatted_message)

        except Exception as ex:
            logging.warning("Cannot send email Error: %s" % ex)

import smtplib


class EmailGateway(object):
    def __init__(self, host, port=25, username=None, password=None):
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    def send_email(self, sender, recievers, message):
        smtpObj = smtplib.SMTP(self._host, self._port)
        try:
            if self._username and self._password:
                smtpObj.login(self._username, self._password)
            smtpObj.sendmail(sender, recievers, message)
        finally:
            smtpObj.quit()
