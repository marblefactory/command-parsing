import unittest

import numpy as np

from networks import descriptor_vector, LocationNN, MovementNN
from descriptor import Descriptor


class MockDescriptor(Descriptor):
    """
    Returns the supplied response for every string.
    """
    def __init__(self, response: float):
        self.r = response

    def response(self, text: str) -> float:
        return self.r

    def max_response(self) -> float:
        return 1


class DescriptorVectorTestCase(unittest.TestCase):
    def test_descriptor_vector(self):
        d0 = MockDescriptor(0)
        d1 = MockDescriptor(0.5)
        d2 = MockDescriptor(1)

        vec = descriptor_vector([d0, d1, d2], 'some text')
        expected = np.array([0, 0, 1])

        assert np.array_equal(vec, expected)


class LocationNNTestCase(unittest.TestCase):
    def test_absolute(self):
        """
        Tests for a high response for an absolute location.
        """
        sentence = 'Go forwards to room 506'

        vec = LocationNN().run(sentence)
        expected = np.array([1, 0, 0, 0, 0])

        assert np.array_equal(vec, expected)

    def test_contextual_missing_position(self):
        """
        Tests for a high response for a contextual location even when missing the position (e.g. first, second, etc)
        """
        sentence = 'Take the door on your left'

        vec = LocationNN().run(sentence)
        expected = np.array([0, 1, 0, 0, 0])

        assert np.array_equal(vec, expected)

    def test_contextual(self):
        """
        Tests for a high response for a contextual location.
        """
        sentence = 'Take first door on your left'

        vec = LocationNN().run(sentence)
        expected = np.array([0, 1, 0, 0, 0])

        assert np.array_equal(vec, expected)

    def test_directional(self):
        """
        Tests for a high response for a directional location.
        """
        sentence = 'Go forwards'

        vec = LocationNN().run(sentence)
        expected = np.array([0, 0, 1, 0, 0])

        assert np.array_equal(vec, expected)


class MovementNNTestCase(unittest.TestCase):
    def test_slow(self):
        """
        Tests for a high response for moving slowly.
        """
        sentence = 'go slowly to the end of the corridor'

        vec = MovementNN().run(sentence)
        expected = np.array([1, 0, 0, 0, 0, 1])

        assert np.array_equal(vec, expected)

    def test_med(self):
        """
        Tests for a high response for moving normally.
        """
        sentence = 'go to the end of the corridor'

        vec = MovementNN().run(sentence)
        expected = np.array([0, 1, 0, 0, 0, 1])

        assert np.array_equal(vec, expected)

    def test_fast(self):
        """
        Tests for a high response for moving quickly.
        """
        sentence = 'go quickly to the end of the corridor'

        vec = MovementNN().run(sentence)
        expected = np.array([0, 0, 1, 0, 0, 1])

        assert np.array_equal(vec, expected)

    def test_prone(self):
        """
        Tests for a high response for a prone stance.
        """
        sentence = 'go prone to the end of the corridor'

        vec = MovementNN().run(sentence)
        expected = np.array([0, 1, 0, 1, 0, 0])

        assert np.array_equal(vec, expected)

    def test_crouch(self):
        """
        Tests for a high response for a crouched stance.
        """
        sentence = 'move crouched to the end of the corridor'

        vec = MovementNN().run(sentence)
        expected = np.array([0, 1, 0, 0, 1, 0])

        assert np.array_equal(vec, expected)

    def test_stand(self):
        """
        Tests for a high response for a standing stance.
        """
        sentence = 'go to the end of the corridor'

        vec = MovementNN().run(sentence)
        expected = np.array([0, 1, 0, 0, 0, 1])

        assert np.array_equal(vec, expected)