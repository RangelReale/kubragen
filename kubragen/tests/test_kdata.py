import unittest

from kubragen.kdata import KData_ConfigMap, KData_ConfigMapManual, KData_Secret, KData_SecretManual
from kubragen.kdatahelper import KDataHelper_Env, KDataHelper_Volume


class TestKData(unittest.TestCase):
    def test_helper_env_value(self):
        kdata = KDataHelper_Env.info(base_value={
            'name': 'APP_PASSWORD',
        }, value='mypassword', default_value={
            'valueFrom': {
                'secretKeyRef': {
                    'name': 'bt-config-secret',
                    'key': 'password'
                }
            },
        })
        self.assertEqual(kdata, {
            'name': 'APP_PASSWORD',
            'value': 'mypassword',
        })

    def test_helper_env_none(self):
        kdata = KDataHelper_Env.info(base_value={
            'name': 'APP_PASSWORD',
        }, value=None, default_value={
            'valueFrom': {
                'secretKeyRef': {
                    'name': 'bt-config-secret',
                    'key': 'password'
                }
            },
        })
        self.assertEqual(kdata, {
            'name': 'APP_PASSWORD',
            'valueFrom': {
                'secretKeyRef': {
                    'name': 'bt-config-secret',
                    'key': 'password'
                }
            },
        })

    def test_helper_env_configmap(self):
        kdata = KDataHelper_Env.info(base_value={
            'name': 'APP_PASSWORD',
        }, value=KData_ConfigMap(configmapName='mycm', configmapData='cmdata'), default_value={
            'valueFrom': {
                'secretKeyRef': {
                    'name': 'bt-config-secret',
                    'key': 'password'
                }
            },
        })
        self.assertEqual(kdata, {
            'name': 'APP_PASSWORD',
            'valueFrom': {
                'configMapKeyRef': {
                    'name': 'mycm',
                    'key': 'cmdata'
                }
            },
        })

    def test_helper_env_kdata(self):
        kdata = KDataHelper_Env.info(base_value={
            'name': 'APP_PASSWORD',
        }, value_if_kdata=KData_ConfigMap(configmapName='mycm', configmapData='cmdata'), default_value={
            'valueFrom': {
                'secretKeyRef': {
                    'name': 'bt-config-secret',
                    'key': 'password'
                }
            },
        })
        self.assertEqual(kdata, {
            'name': 'APP_PASSWORD',
            'valueFrom': {
                'configMapKeyRef': {
                    'name': 'mycm',
                    'key': 'cmdata'
                }
            },
        })

    def test_helper_env_kdata_notkdata(self):
        kdata = KDataHelper_Env.info(base_value={
            'name': 'APP_PASSWORD',
        }, value_if_kdata='not a KData', default_value={
            'valueFrom': {
                'secretKeyRef': {
                    'name': 'bt-config-secret',
                    'key': 'password'
                }
            },
        })
        self.assertEqual(kdata, {
            'name': 'APP_PASSWORD',
            'valueFrom': {
                'secretKeyRef': {
                    'name': 'bt-config-secret',
                    'key': 'password'
                }
            },
        })

    def test_helper_volume_value(self):
        kdata = KDataHelper_Volume.info(base_value={
            'name': 'data-volume',
        }, value={
            'emptyDir': {},
        }, default_value={
            'persistentVolumeClaim': {
                'claimName': 'bt-storage-claim'
            }
        })
        self.assertEqual(kdata, {
            'name': 'data-volume',
            'emptyDir': {},
        })

    def test_helper_volume_none(self):
        kdata = KDataHelper_Volume.info(base_value={
            'name': 'data-volume',
        }, value=None, default_value={
            'persistentVolumeClaim': {
                'claimName': 'bt-storage-claim'
            }
        })
        self.assertEqual(kdata, {
            'name': 'data-volume',
            'persistentVolumeClaim': {
                'claimName': 'bt-storage-claim'
            }
        })

    def test_helper_volume_configmap(self):
        kdata = KDataHelper_Volume.info(base_value={
            'name': 'data-volume',
        }, value=KData_ConfigMap(configmapName='mycm', configmapData='cmdata'), default_value={
            'persistentVolumeClaim': {
                'claimName': 'bt-storage-claim'
            }
        })
        self.assertEqual(kdata, {
            'name': 'data-volume',
            'configMap': {
                'name': 'mycm',
                'items': [{
                    'key': 'cmdata',
                    'path': 'cmdata',
                }],
            }
        })

    def test_helper_volume_kdata(self):
        kdata = KDataHelper_Volume.info(base_value={
            'name': 'data-volume',
        }, value_if_kdata=KData_ConfigMap(configmapName='mycm', configmapData='cmdata'), default_value={
            'persistentVolumeClaim': {
                'claimName': 'bt-storage-claim'
            }
        })
        self.assertEqual(kdata, {
            'name': 'data-volume',
            'configMap': {
                'name': 'mycm',
                'items': [{
                    'key': 'cmdata',
                    'path': 'cmdata',
                }],
            }
        })

    def test_helper_volume_configmap_manual(self):
        kdata = KDataHelper_Volume.info(base_value={
            'name': 'data-volume',
        }, value=KData_ConfigMapManual(configmapName='mycm', merge_config={
            'configMap': {
                'items': [{
                    'key': 'xcmdata',
                    'path': 'xcmdata',
                }],
            },
        }), default_value={
            'persistentVolumeClaim': {
                'claimName': 'bt-storage-claim'
            }
        })

        self.assertEqual(kdata, {
            'name': 'data-volume',
            'configMap': {
                'name': 'mycm',
                'items': [{
                    'key': 'xcmdata',
                    'path': 'xcmdata',
                }],
            }
        })

    def test_helper_volume_kdata_notkdata(self):
        kdata = KDataHelper_Volume.info(base_value={
            'name': 'data-volume',
        }, value_if_kdata='not a KData', default_value={
            'persistentVolumeClaim': {
                'claimName': 'bt-storage-claim'
            }
        })
        self.assertEqual(kdata, {
            'name': 'data-volume',
            'persistentVolumeClaim': {
                'claimName': 'bt-storage-claim'
            }
        })

    def test_helper_volume_secret(self):
        kdata = KDataHelper_Volume.info(base_value={
            'name': 'data-volume',
        }, value=KData_Secret(secretName='mycm', secretData='cmdata'), default_value={
            'persistentVolumeClaim': {
                'claimName': 'bt-storage-claim'
            }
        })
        self.assertEqual(kdata, {
            'name': 'data-volume',
            'secret': {
                'secretName': 'mycm',
                'items': [{
                    'key': 'cmdata',
                    'path': 'cmdata',
                }],
            }
        })

    def test_helper_volume_secret_manual(self):
        kdata = KDataHelper_Volume.info(base_value={
            'name': 'data-volume',
        }, value=KData_SecretManual(secretName='mycm', merge_config={
            'secret': {
                'items': [{
                    'key': 'xcmdata',
                    'path': 'xcmdata',
                }],
            },
        }), default_value={
            'persistentVolumeClaim': {
                'claimName': 'bt-storage-claim'
            }
        })
        self.assertEqual(kdata, {
            'name': 'data-volume',
            'secret': {
                'secretName': 'mycm',
                'items': [{
                    'key': 'xcmdata',
                    'path': 'xcmdata',
                }],
            }
        })