import unittest
from typing import Optional, Any

from kubragen.exception import OptionError
from kubragen.option import OptionDef, OptionRoot, OptionDefaultValue, OptionValue, Option, OptionValueCallable
from kubragen.options import Options, option_root_get


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

        class TOption(Options):
            def define_options(self) -> Optional[Any]:
                return {
                    'foo': {
                        'bar': OptionDef(default_value='baz'),
                    }
                }

        with self.assertRaises(OptionError):
            TOption({
                'foo': {
                    'nobar': 'nobaz',
                }
            })

    def test_options_default_value(self):
        class TOption(Options):
            def define_options(self) -> Optional[Any]:
                return {
                    'foo': {
                        'bar': OptionDef(default_value='baz'),
                    }
                }

        opt = TOption({
            'foo': {
            }
        })
        self.assertEqual(option_root_get(opt, 'foo.bar'), 'baz')

    def test_options_required(self):
        class TOption(Options):
            def define_options(self) -> Optional[Any]:
                return {
                    'foo': {
                        'bar': OptionDef(required=True),
                    }
                }

        with self.assertRaises(TypeError):
            opt = TOption({
                'foo': {
                }
            })
            option_root_get(opt, 'foo.bar')

    def test_options_allowed_type(self):
        class TOption(Options):
            def define_options(self) -> Optional[Any]:
                return {
                    'foo': {
                        'bar': OptionDef(required=True, allowed_types=[str, int]),
                    }
                }

        with self.assertRaises(TypeError):
            opt = TOption({
                'foo': {
                    'bar': 3.0,
                }
            })
            option_root_get(opt, 'foo.bar')

    def test_options_value(self):
        class TOptionValue(OptionValue):
            def get_value(self, name: Optional[str] = None, base_option: Optional[Option] = None) -> Any:
                return 'baz_value'

        class TOption(Options):
            def define_options(self) -> Optional[Any]:
                return {
                    'foo': {
                        'bar': OptionDef(default_value='baz'),
                    }
                }

        opt = TOption({
            'foo': {
                'bar': TOptionValue(),
            }
        })
        self.assertEqual(option_root_get(opt, 'foo.bar'), 'baz_value')

    def test_options_value_default_value(self):
        class TOption(Options):
            def define_options(self) -> Optional[Any]:
                return {
                    'foo': {
                        'bar': OptionDef(default_value='baz'),
                    }
                }

        opt = TOption({
            'foo': {
                'bar': OptionDefaultValue(),
            }
        })
        self.assertEqual(option_root_get(opt, 'foo.bar'), 'baz')

    def test_options_value_callable(self):
        class TOption(Options):
            def define_options(self) -> Optional[Any]:
                return {
                    'foo': {
                        'bar': OptionDef(default_value='baz'),
                    }
                }

        opt = TOption({
            'foo': {
                'bar': OptionValueCallable(lambda n, o: 'baz_value'),
            }
        })
        self.assertEqual(option_root_get(opt, 'foo.bar'), 'baz_value')

    def test_options_root(self):
        class TOption(Options):
            def define_options(self) -> Optional[Any]:
                return {
                    'foo': {
                        'bar': OptionDef(required=True),
                    }
                }

        root_options = Options({
            'root_bar': 'baz',
        })

        opt = TOption({
            'foo': {
                'bar': OptionRoot('root_bar'),
            }
        })
        self.assertEqual(option_root_get(opt, 'foo.bar', root_options=root_options), 'baz')