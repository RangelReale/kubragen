import unittest
from typing import Optional, Mapping

from kubragen import KubraGen
from kubragen.builder import Builder
from kubragen.data import DisabledData
from kubragen.kdata import KData_Secret, KData_ConfigMap, KData_Value
from kubragen.kdatahelper import KDataHelper_Volume, KDataHelper_Env
from kubragen.option import OptionDef, OptionDefFormat
from kubragen.options import Options
from kubragen.provider import Provider_Generic


class TestBuilder(unittest.TestCase):
    def setUp(self):
        self.kg = KubraGen(provider=Provider_Generic())

    def test_options_read(self):
        builder = BuilderTest(self.kg, BuilderTestOptions({

        }))
        self.assertEqual(builder.option_get('config.service_port'), 3000)

    def test_options_required(self):
        builder = BuilderTest(self.kg, BuilderTestOptions({

        }))
        with self.assertRaises(TypeError):
            builder.option_get('config.config_file')

    def test_options_kdata_invalid(self):
        builder = BuilderTest(self.kg, BuilderTestOptions({
            'config': {
                'password': KData_Value('mypassword'),
            }
        }))
        with self.assertRaises(TypeError):
            builder.option_get('config.password')

    def test_options_kdata_secret(self):
        builder = BuilderTest(self.kg, BuilderTestOptions({
            'config': {
                'password': KData_Secret(secretName='global-config-secret', secretData='password'),
            }
        }))

        kdata_default = {
            'name': 'APP_PASSWORD',
            'valueFrom': {
                'secretKeyRef': {
                    'name': 'global-config-secret',
                    'key': 'password'
                }
            },
        }

        kdata = KDataHelper_Env.info(base_value={
            'name': 'APP_PASSWORD',
        }, value=builder.option_get('config.password'), default_value={
            'valueFrom': {
                'secretKeyRef': {
                    'name': 'bt-config-secret',
                    'key': 'password'
                }
            },
        })
        self.assertEqual(kdata, kdata_default)

    def test_options_kdata_nosecret(self):
        builder = BuilderTest(self.kg, BuilderTestOptions({
            'config': {}
        }))

        kdata_default = {
            'name': 'APP_PASSWORD',
            'valueFrom': {
                'secretKeyRef': {
                    'name': 'bt-config-secret',
                    'key': 'password'
                }
            },
        }

        kdata = KDataHelper_Env.info(base_value={
            'name': 'APP_PASSWORD',
        }, value=builder.option_get('config.password'), default_value={
            'valueFrom': {
                'secretKeyRef': {
                    'name': 'bt-config-secret',
                    'key': 'password'
                }
            },
        })
        self.assertEqual(kdata, kdata_default)

    def test_options_kdata_disable(self):
        builder = BuilderTest(self.kg, BuilderTestOptions({
            'config': {}
        }))

        kdata_default = {
            'name': 'APP_PASSWORD',
            'valueFrom': {
                'secretKeyRef': {
                    'name': 'bt-config-secret',
                    'key': 'password'
                }
            },
        }

        kdata = KDataHelper_Env.info(base_value={
            'name': 'APP_PASSWORD',
        }, value=builder.option_get('config.password'), default_value={
            'valueFrom': {
                'secretKeyRef': {
                    'name': 'bt-config-secret',
                    'key': 'password'
                }
            },
        }, disable_if_none=True)
        self.assertIsInstance(kdata, DisabledData)


class BuilderTestOptions(Options):
    def define_options(self):
        return {
            'basename': OptionDef(required=True, default_value='bt', allowed_types=[str]),
            'namespace': OptionDef(required=True, default_value='btns', allowed_types=[str]),
            'config': {
                'service_port': OptionDef(required=True, default_value=3000, allowed_types=[int]),
                'frontend_url': OptionDef(allowed_types=[str]),
                'password': OptionDef(format=OptionDefFormat.KDATA_ENV,
                                      allowed_types=[str, KData_Secret, KData_ConfigMap]),
                'config_file': OptionDef(required=True),
            },
            'container': {
                'bt': OptionDef(required=True, default_value='bt/bt:7.2.0'),
            },
            'kubernetes': {
                'volumes': {
                    'data': OptionDef(required=True, format=OptionDefFormat.KDATA_VOLUME,
                                      default_value={'emptyDir': {}},
                                      allowed_types=[Mapping, *KDataHelper_Volume.allowed_kdata()]),
                },
                'resources': {
                    'deployment': OptionDef(),
                }
            },
        }


class BuilderTest(Builder):
    def __init__(self, kubragen: KubraGen, options: Optional[BuilderTestOptions] = None):
        super().__init__(kubragen)
        self.kubragen = kubragen
        if options is None:
            options = BuilderTestOptions()
        self.options = options

    def option_get(self, name: str):
        return self.kubragen.option_root_get(self.options, name)
