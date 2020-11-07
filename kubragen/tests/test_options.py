import unittest
from typing import Optional, Any

from kubragen.exception import OptionError
from kubragen.helper import LiteralStr, HelperStr
from kubragen.option import OptionDef, OptionRoot, OptionDefaultValue, OptionValue, Option, OptionValueCallable
from kubragen.options import Options, option_root_get, OptionsBase


class TestOptions(unittest.TestCase):

    def test_options_standalone(self):
        options = Options({
            'foo': {
                'bar': 'baz',
            }
        })
        self.assertEqual(options.value_get('foo.bar'), 'baz')

    def test_options_defined(self):
        # Cannot create key when there are defined options
        with self.assertRaises(OptionError):
            OptionsBase(defined_options={
                'foo': {
                    'bar': OptionDef(default_value='baz'),
                }
            }, options={
                'foo': {
                    'nobar': 'nobaz',
                }
            })

    def test_options_default_value(self):
        opt = OptionsBase(defined_options={
            'foo': {
                'bar': OptionDef(default_value='baz'),
            }
        }, options={
            'foo': {
            }
        })
        self.assertEqual(option_root_get(opt, 'foo.bar'), 'baz')

    def test_options_required(self):
        with self.assertRaises(TypeError):
            opt = OptionsBase(defined_options={
                'foo': {
                    'bar': OptionDef(required=True),
                }
            }, options={
                'foo': {
                }
            })
            option_root_get(opt, 'foo.bar')

    def test_options_allowed_type(self):
        with self.assertRaises(TypeError):
            opt = OptionsBase(defined_options={
                'foo': {
                    'bar': OptionDef(required=True, allowed_types=[str, int]),
                }
            }, options={
                'foo': {
                    'bar': 3.0,
                }
            })
            option_root_get(opt, 'foo.bar')

    def test_options_helper(self):
        opt = OptionsBase(defined_options={
            'foo': {
                'bar': OptionDef(default_value='baz'),
            }
        }, options={
            'foo': {
                'bar': LiteralStr('baz_literal'),
            }
        })
        self.assertIsInstance(option_root_get(opt, 'foo.bar'), HelperStr)

    def test_options_value(self):
        class TOptionValue(OptionValue):
            def get_value(self, name: Optional[str] = None, base_option: Optional[Option] = None) -> Any:
                return 'baz_value'

        opt = OptionsBase(defined_options={
            'foo': {
                'bar': OptionDef(default_value='baz'),
            }
        }, options={
            'foo': {
                'bar': TOptionValue(),
            }
        })
        self.assertEqual(option_root_get(opt, 'foo.bar'), 'baz_value')

    def test_options_value_default_value(self):
        opt = OptionsBase(defined_options={
            'foo': {
                'bar': OptionDef(default_value='baz'),
            }
        }, options={
            'foo': {
                'bar': OptionDefaultValue(),
            }
        })
        self.assertEqual(option_root_get(opt, 'foo.bar'), 'baz')

    def test_options_value_callable(self):
        opt = OptionsBase(defined_options={
            'foo': {
                'bar': OptionDef(default_value='baz'),
            }
        }, options={
            'foo': {
                'bar': OptionValueCallable(lambda n, o: 'baz_value'),
            }
        })
        self.assertEqual(option_root_get(opt, 'foo.bar'), 'baz_value')

    def test_options_root(self):
        root_options = Options({
            'root_bar': 'baz',
        })

        opt = OptionsBase(defined_options={
            'foo': {
                'bar': OptionDef(required=True),
            }
        }, options={
            'foo': {
                'bar': OptionRoot('root_bar'),
            }
        })
        self.assertEqual(option_root_get(opt, 'foo.bar', root_options=root_options), 'baz')
