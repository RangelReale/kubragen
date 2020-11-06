import unittest

from kubragen.data import ValueIsNone, DisabledData, ValueData


class TestData(unittest.TestCase):
    def test_value_is_None(self):
        self.assertTrue(ValueIsNone(None))
        self.assertFalse(ValueIsNone('xxx'))
        self.assertTrue(ValueIsNone(DisabledData()))
        self.assertFalse(ValueIsNone(ValueData(value='xxx', enabled=True)))
        self.assertTrue(ValueIsNone(ValueData(value=None, enabled=True)))
        self.assertTrue(ValueIsNone(ValueData(value=DisabledData(), enabled=True)))
        self.assertFalse(ValueIsNone(ValueData(value=ValueData(value='xxx', enabled=True), enabled=True)))
