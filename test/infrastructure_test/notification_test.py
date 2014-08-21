import unittest
import os
import sys
import logging
from mock import patch

sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..', '..','src'))

from infrastructure.notification import *
import test_helpers

class TestEmailGateway(object):
    def __init__(self):
        self.messages = []
        self.raises = None

    def send_email(self, sender, recievers, message):
        if self.raises != None:
            raise self.raises
        self.messages.append((sender, recievers, message))

class EmailNotificationTests(unittest.TestCase):

    def test_send_message_calls_gateway_with_message(self):
        sender = "monty@python.org"
        recipient = "knights@roundtable.com"
        subject = "A Subject"
        expected_message = """From: monty@python.org <monty@python.org>
To: knights@roundtable.com <knights@roundtable.com>
Subject: A Subject

Message for you
"""
        gateway = TestEmailGateway()
        ns = EmailNotificationService(gateway,sender,recipient)
        ns.send_message("A Subject", "Message for you")

        self.assertEquals(1, len(gateway.messages))
        self.assertEquals(sender, gateway.messages[0][0])
        self.assertEquals([recipient], gateway.messages[0][1])
        self.assertEquals(expected_message, gateway.messages[0][2])

    def test_send_message_when_gateway_throws_error(self):
        sender = "monty@python.org"
        recipient = "knights@roundtable.com"
        subject = "A Subject"
        gateway = TestEmailGateway()
        gateway.raises = Exception("Boom")

        ns = EmailNotificationService(gateway,sender,recipient)
        ns.send_message("A Subject", "Message for you")


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level='INFO')
    unittest.main()
