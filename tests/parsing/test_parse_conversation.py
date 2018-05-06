import unittest
from parsing.pre_processing import pre_process
from parsing.parse_action import statement
from actions.conversation import *


class GreetingTestCase(unittest.TestCase):
    def test_hello(self):
        s = pre_process('hello')
        r = statement().parse(s).parsed
        self.assertEqual(r, Greeting())

    def test_hi(self):
        s = pre_process('hi')
        r = statement().parse(s).parsed
        self.assertEqual(r, Greeting())


class WhatNameTestCase(unittest.TestCase):
    def test_what_name(self):
        s = pre_process('what is your name')
        r = statement().parse(s).parsed
        self.assertEqual(r, WhatName())


class WhoAreYouTestCase(unittest.TestCase):
    def test_who_are_you(self):
        s = pre_process('who are you')
        r = statement().parse(s).parsed
        self.assertEqual(r, WhoAreYou())


class ObscenityTestCase(unittest.TestCase):
    def test_starred(self):
        s = pre_process('f*** you')
        r = statement().parse(s).parsed
        self.assertEqual(r, Obscenity())

    def test_fuck(self):
        s = pre_process('fuck you')
        r = statement().parse(s).parsed
        self.assertEqual(r, Obscenity())


class RepeatTestCase(unittest.TestCase):
    def test_repeat(self):
        s = pre_process('repeat a b c')
        r = statement().parse(s).parsed
        self.assertEqual(r, Repeat(['a', 'b', 'c']))

    def test_repeat_after_me(self):
        s = pre_process('repeat after me a b c')
        r = statement().parse(s).parsed
        self.assertEqual(r, Repeat(['a', 'b', 'c']))

    def test_say(self):
        s = pre_process('say a b c')
        r = statement().parse(s).parsed
        self.assertEqual(r, Repeat(['a', 'b', 'c']))
