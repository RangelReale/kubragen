import unittest
from typing import Optional, Any

from kubragen.data import ValueData, Data, DisabledData
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

    def test_options_data(self):
        opt = OptionsBase(defined_options={
            'foo': {
                'bar': OptionDef(default_value='baz'),
            }
        }, options={
            'foo': {
                'bar': ValueData('diz', enabled=True),
            }
        })
        self.assertEqual(option_root_get(opt, 'foo.bar'), 'diz')
        self.assertIsInstance(option_root_get(opt, 'foo.bar', handle_data=False), Data)

    def test_options_data_recursive(self):
        opt = OptionsBase(defined_options={
            'foo': {
                'bar': OptionDef(default_value='baz'),
            }
        }, options={
            'foo': {
                'bar': ValueData(ValueData('diz', enabled=True), enabled=True),
            }
        })
        self.assertEqual(option_root_get(opt, 'foo.bar'), 'diz')
        self.assertIsInstance(option_root_get(opt, 'foo.bar', handle_data=False), Data)

    def test_options_data_disabled(self):
        opt = OptionsBase(defined_options={
            'foo': {
                'bar': OptionDef(default_value='baz'),
            }
        }, options={
            'foo': {
                'bar': ValueData('diz', enabled=False),
            }
        })
        self.assertIsNone(option_root_get(opt, 'foo.bar'))
        self.assertIsInstance(option_root_get(opt, 'foo.bar', handle_data=False), Data)

    def test_options_data_inner(self):
        opt = OptionsBase(defined_options={
            'foo': {
                'bar': OptionDef(default_value=[]),
            }
        }, options={
            'foo': {
                'bar': [
                    ValueData(1, enabled=True),
                    ValueData(2, enabled=False),
                ],
            }
        })
        self.assertEqual(option_root_get(opt, 'foo.bar'), [1])

    def test_options_data_inner2(self):
        opt = OptionsBase(defined_options={
            'foo': {
                'bar': OptionDef(default_value={}),
            }
        }, options={
            'foo': {
                'bar': {
                    'gin': ValueData(1, enabled=True),
                    'per': ValueData(2, enabled=False),
                },
            }
        })
        self.assertEqual(option_root_get(opt, 'foo.bar'), {'gin': 1})
