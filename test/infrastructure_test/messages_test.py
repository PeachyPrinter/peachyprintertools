import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from infrastructure.messages import MoveMessage


class MoveMesssageTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_move_message_encodes_and_decodes(self):
        inital_message = MoveMessage(77, 88, 55)
        proto_bytes = inital_message.get_bytes()
        self.assertTrue(len(proto_bytes) > 0)
        decoded_message = MoveMessage.from_bytes(proto_bytes)
        self.assertEqual(inital_message, decoded_message)


if __name__ == '__main__':
    unittest.main()
