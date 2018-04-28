import unittest
from parsing.parse_conversation import *


class GreetingTestCase(unittest.TestCase):
    def test_hello(self):
        s = pre_process('hello')
        r = conversation().parse(s).parsed
        self.assertEqual(r, Greeting())

    def test_hi(self):
        s = pre_process('hi')
        r = conversation().parse(s).parsed
        self.assertEqual(r, Greeting())


class NoConversationTestCase(unittest.TestCase):
    def test_default(self):
        """
        Tests that the default value conversation is used when no other conversation is parsed.
        """
        s = pre_process('')
        r = conversation().parse(s).parsed
        self.assertEqual(r, DefaultConversation())
