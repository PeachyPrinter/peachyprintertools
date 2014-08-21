import logging

from domain.notification import NotificationService

class EmailNotificationService(NotificationService):
    def __init__(self, email_gateway,sender,recipient):
        self._email_gateway = email_gateway
        self._sender = sender
        self._recipient = recipient
        self._template = """From: %s <%s>
To: %s <%s>
Subject: %s

%s
"""

    def send_message(self, subject, message):
        formatted_message = self._template % ( self._sender,self._sender, self._recipient, self._recipient, subject, message)
        try:
            self._email_gateway.send_email(self._sender,[self._recipient],formatted_message)
        except Exception as ex:
            logging.warning("Cannot send email Error: %s" % ex)

import smtplib

class EmailGateway(object):
    def __init__(self, host, port = 25):
        self.host = host
        self.port = port

    def send_email(self,sender, recievers, message):
        smtpObj = smtplib.SMTP(host,port)
        try:
            smtpObj.sendmail(sender, receivers, message)
        finally:
            smtpObj.quit()


