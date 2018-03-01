import unittest
from parsing.parse_result import *


class ParseResultTestCase(unittest.TestCase):
    def test_failure_less_than_partial(self):
        r1 = FailureParse()
        r2 = PartialParse(None, 0.0, 'Type')

        assert r1 < r2
        assert not r1 > r2

    def test_failure_less_than_success(self):
        r1 = FailureParse()
        r2 = SuccessParse(None, 0.0, [])

        assert r1 < r2
        assert not r1 > r2

    def test_partial_less_than_success(self):
        r1 = PartialParse(None, 0.0, 'Type')
        r2 = SuccessParse(None, 0.0, [])

        assert r1 < r2
        assert not r1 > r2

    def test_failures_equal(self):
        # Tests that two failures are worth the same.
        assert not FailureParse() < FailureParse()
        assert not FailureParse() > FailureParse()

    def test_partial_uses_response(self):
        # Tests that if two partials are compared, their response is used.
        r1 = PartialParse(None, 0.0, 'Type')
        r2 = PartialParse(None, 0.5, 'Type')

        assert r1 < r2
        assert not r1 > r2

    def test_partial_strictly_less_than(self):
        # Tests that if two partials are compared, their response is used.
        r1 = PartialParse(None, 0.5, 'Type')
        r2 = PartialParse(None, 0.5, 'Type')

        assert not r1 < r2
        assert not r1 > r2

    def test_success_uses_response(self):
        # Tests that if two successes are compared, their response is used.
        r1 = SuccessParse(None, 0.0, [])
        r2 = SuccessParse(None, 0.5, [])

        assert r1 < r2
        assert not r1 > r2

    def test_success_strictly_less_than(self):
        # Tests that if two successes are compared, their response is used.
        r1 = SuccessParse(None, 0.5, [])
        r2 = SuccessParse(None, 0.5, [])

        assert not r1 < r2
        assert not r1 > r2
