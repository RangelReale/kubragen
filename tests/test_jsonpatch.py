import unittest

from kubragen.data import ValueData
from kubragen.helper import QuotedStr, LiteralStr, HelperStr
from kubragen.jsonpatch import FilterJSONPatches_Apply, FilterJSONPatch, ObjectFilter
from kubragen.object import Object


class TestJSONPatch(unittest.TestCase):

    def test_merge(self):
        data = [
            Object({
                'foo': 'bar',
                'shin': {
                    'gami': 'hai',
                    'shami': 'nai',
                },
            }, name='x')
        ]

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters={'names': ['x']}, patches=[
                {'op': 'add', 'path': '/shin/tari', 'value': 'bai'}
            ])
        ])

        self.assertEqual(ret, [{'foo': 'bar', 'shin': {'gami': 'hai', 'shami': 'nai', 'tari': 'bai'}}])

    def test_no_merge(self):
        data = [
            Object({
                'foo': 'bar',
                'shin': {
                    'gami': 'hai',
                    'shami': 'nai',
                },
            }, name='x', source='y', instance='z')
        ]

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters={'names': ['a']}, patches=[
                {'op': 'add', 'path': '/shin/tari', 'value': 'bai'}
            ])
        ])
        self.assertEqual(ret, [{'foo': 'bar', 'shin': {'gami': 'hai', 'shami': 'nai'}}])

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters={'sources': ['b']}, patches=[
                {'op': 'add', 'path': '/shin/tari', 'value': 'bai'}
            ])
        ])
        self.assertEqual(ret, [{'foo': 'bar', 'shin': {'gami': 'hai', 'shami': 'nai'}}])

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters={'instances': ['c']}, patches=[
                {'op': 'add', 'path': '/shin/tari', 'value': 'bai'}
            ])
        ])
        self.assertEqual(ret, [{'foo': 'bar', 'shin': {'gami': 'hai', 'shami': 'nai'}}])

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters=ObjectFilter(names='a', sources='y', instances='z'), patches=[
                {'op': 'add', 'path': '/shin/tari', 'value': 'bai'}
            ])
        ])
        self.assertEqual(ret, [{'foo': 'bar', 'shin': {'gami': 'hai', 'shami': 'nai'}}])

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters=[ObjectFilter(sources='h', instances='j'), lambda o: o.name == 'i'], patches=[
                {'op': 'add', 'path': '/shin/tari', 'value': 'bai'}
            ])
        ])
        self.assertEqual(ret, [{'foo': 'bar', 'shin': {'gami': 'hai', 'shami': 'nai'}}])

    def test_merge_filters(self):
        data = [
            Object({
                'foo': 'bar',
                'shin': {
                    'gami': 'hai',
                    'shami': 'nai',
                },
            }, name='x', source='y', instance='z')
        ]

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters={'names': ['x'], 'sources': 'y', 'instances': ['z']}, patches=[
                {'op': 'add', 'path': '/shin/tari', 'value': 'bai'}
            ])
        ])

        self.assertEqual(ret, [{'foo': 'bar', 'shin': {'gami': 'hai', 'shami': 'nai', 'tari': 'bai'}}])

    def test_merge_filters_2(self):
        data = [
            Object({
                'foo': 'bar',
                'shin': 'gami',
            }, name='x', source='y', instance='z')
        ]

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters=ObjectFilter(names=['x'], sources='y', instances=['z']), patches=[
                {'op': 'add', 'path': '/tari', 'value': 'bai'}
            ])
        ])
        self.assertEqual(ret, [{'foo': 'bar', 'shin': 'gami', 'tari': 'bai'}])

    def test_merge_filters_3(self):
        data = [
            Object({
                'foo': 'bar',
                'shin': 'gami',
            }, name='x', source='y', instance='z')
        ]

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters=lambda o: o.name == 'x' and o.source == 'y' and o.instance == 'z', patches=[
                {'op': 'add', 'path': '/tari', 'value': 'bai'}
            ])
        ])
        self.assertEqual(ret, [{'foo': 'bar', 'shin': 'gami', 'tari': 'bai'}])

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters=lambda o: o.name == 'x' and o.source == 'y' and o.instance == 'k', patches=[
                {'op': 'add', 'path': '/gari', 'value': 'sai'}
            ])
        ])
        self.assertEqual(ret, [{'foo': 'bar', 'shin': 'gami', 'tari': 'bai'}])

    def test_merge_filters_4(self):
        data = [
            Object({
                'foo': 'bar',
                'shin': 'gami',
            }, name='x', source='y', instance='z')
        ]

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters=[lambda o: o.name == 'a', lambda o: o.name == 'x'], patches=[
                {'op': 'add', 'path': '/tari', 'value': 'bai'}
            ])
        ])
        self.assertEqual(ret, [{'foo': 'bar', 'shin': 'gami', 'tari': 'bai'}])

    def test_merge_filters_5(self):
        data = [
            Object({
                'foo': 'bar',
                'shin': 'gami',
            }, name='x', source='y', instance='z')
        ]

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters=ObjectFilter(callables=[lambda o: o.name == 'a', lambda o: o.name == 'b']), patches=[
                {'op': 'add', 'path': '/tari', 'value': 'bai'}
            ])
        ])
        self.assertEqual(ret, [{'foo': 'bar', 'shin': 'gami'}])

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters=ObjectFilter(callables=[lambda o: o.name == 'a', lambda o: o.name == 'x']), patches=[
                {'op': 'add', 'path': '/tari', 'value': 'bai'}
            ])
        ])
        self.assertEqual(ret, [{'foo': 'bar', 'shin': 'gami', 'tari': 'bai'}])

    def test_merge_valuedata(self):
        data = [
            Object({
                'foo': 'bar',
                'shin': ValueData(value={
                    'gami': 'hai',
                    'shami': 'nai',
                }),
            }, name='x')
        ]

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters={'names': ['x']}, patches=[
                {'op': 'add', 'path': '/shin/tari', 'value': 'bai'}
            ])
        ])

        self.assertEqual(ret, [{'foo': 'bar', 'shin': {'gami': 'hai', 'shami': 'nai', 'tari': 'bai'}}])

    def test_merge_str_to_helperstr(self):
        data = [
            Object({
                'foo': 'bar',
                'shin': QuotedStr('gami'),
            }, name='x')
        ]

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters={'names': ['x']}, patches=[
                {'op': 'replace', 'path': '/shin', 'value': 'bai'}
            ])
        ])

        self.assertEqual(ret, [{'foo': 'bar', 'shin': 'bai'}])
        self.assertNotIsInstance(ret[0]['shin'], HelperStr)

    def test_merge_helperstr_to_str(self):
        data = [
            Object({
                'foo': 'bar',
                'shin': 'gami',
            }, name='x')
        ]

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters={'names': ['x']}, patches=[
                {'op': 'replace', 'path': '/shin', 'value': QuotedStr('bai')}
            ])
        ])

        self.assertEqual(ret, [{'foo': 'bar', 'shin': 'bai'}])
        self.assertIsInstance(ret[0]['shin'], QuotedStr)

    def test_merge_helperstr_to_helperstr(self):
        data = [
            Object({
                'foo': 'bar',
                'shin': QuotedStr('gami'),
            }, name='x')
        ]

        ret = FilterJSONPatches_Apply(items=data, jsonpatches=[
            FilterJSONPatch(filters={'names': ['x']}, patches=[
                {'op': 'replace', 'path': '/shin', 'value': LiteralStr('bai')}
            ])
        ])

        self.assertEqual(ret, [{'foo': 'bar', 'shin': 'bai'}])
        self.assertIsInstance(ret[0]['shin'], LiteralStr)
