import unittest

from kubragen.data import DataIsNone, DisabledData, ValueData, DataGetValue
from kubragen.exception import InvalidOperationError


class TestData(unittest.TestCase):
    def test_data_is_None(self):
        self.assertTrue(DataIsNone(None))
        self.assertFalse(DataIsNone('xxx'))
        self.assertTrue(DataIsNone(DisabledData()))
        self.assertFalse(DataIsNone(ValueData(value='xxx', enabled=True)))
        self.assertTrue(DataIsNone(ValueData(value=None, enabled=True)))
        self.assertTrue(DataIsNone(ValueData(value=DisabledData(), enabled=True)))
        self.assertFalse(DataIsNone(ValueData(value=ValueData(value='xxx', enabled=True), enabled=True)))

    def test_data_get_value(self):
        self.assertEqual(DataGetValue(None), None)
        self.assertEqual(DataGetValue('xxx'), 'xxx')
        self.assertEqual(DataGetValue(DisabledData()), None)
        with self.assertRaises(InvalidOperationError):
            DataGetValue(DisabledData(), raise_if_disabled=True)
        self.assertEqual(DataGetValue(ValueData(value='xxx', enabled=True)), 'xxx')
        self.assertEqual(DataGetValue(ValueData(value=None, enabled=True)), None)
        self.assertEqual(DataGetValue(ValueData(value=DisabledData(), enabled=True)), None)
        self.assertEqual(DataGetValue(ValueData(value=ValueData(value='xxx', enabled=True), enabled=True)), 'xxx')
