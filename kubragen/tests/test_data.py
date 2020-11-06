import unittest

from kubragen.data import ValueIsNone, DisabledData, ValueData, ValueGetValue
from kubragen.exception import InvalidOperationError


class TestData(unittest.TestCase):
    def test_value_is_None(self):
        self.assertTrue(ValueIsNone(None))
        self.assertFalse(ValueIsNone('xxx'))
        self.assertTrue(ValueIsNone(DisabledData()))
        self.assertFalse(ValueIsNone(ValueData(value='xxx', enabled=True)))
        self.assertTrue(ValueIsNone(ValueData(value=None, enabled=True)))
        self.assertTrue(ValueIsNone(ValueData(value=DisabledData(), enabled=True)))
        self.assertFalse(ValueIsNone(ValueData(value=ValueData(value='xxx', enabled=True), enabled=True)))

    def test_value_get_value(self):
        self.assertEqual(ValueGetValue(None), None)
        self.assertEqual(ValueGetValue('xxx'), 'xxx')
        self.assertEqual(ValueGetValue(DisabledData()), None)
        with self.assertRaises(InvalidOperationError):
            ValueGetValue(DisabledData(), raise_if_disabled=True)
        self.assertEqual(ValueGetValue(ValueData(value='xxx', enabled=True)), 'xxx')
        self.assertEqual(ValueGetValue(ValueData(value=None, enabled=True)), None)
        self.assertEqual(ValueGetValue(ValueData(value=DisabledData(), enabled=True)), None)
        self.assertEqual(ValueGetValue(ValueData(value=ValueData(value='xxx', enabled=True), enabled=True)), 'xxx')
