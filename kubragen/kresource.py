from typing import Optional, Any, Sequence, Mapping

from kubragen.exception import InvalidParamError
from kubragen.helper import QuotedStr
from kubragen.merger import Merger
from kubragen.object import ObjectItem
from kubragen.provider import PersistentVolumeProfile, PersistentVolumeClaimProfile, Provider
from kubragen.util import dict_get_value, dict_has_name


class KResource:
    pass


class KRStorageClass(KResource):
    pass


# class KRPersistentVolumeProfile(KResource):
#     def __init__(self, storageclass: Optional[str] = None):
#         self.storageclass = storageclass
#
#     def build(self, provider, config, merge_config):
#         pass


class KRPersistentVolumeProfile_EmptyDir(PersistentVolumeProfile):
    def build(self, provider: Provider, name: str, config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        if config is not None:
            if 'name' in config:
                name = config['name']

        ret = Merger.merge({
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'emptyDir': {}
            },
        }, merge_config if merge_config is not None else {})

        if self.storageclass is not None:
            Merger.merge(ret, {
                'spec': {
                    'storageClassName': self.storageclass,
                }
            })

        return ret


class KRPersistentVolumeProfile_HostPath(PersistentVolumeProfile):
    def build(self, provider: Provider, name: str, config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        hostPath = None
        if config is not None:
            if 'name' in config:
                name = config['name']
            if 'hostPath' in config:
                hostPath = config['hostPath']
        if hostPath is None:
            raise InvalidParamError('"hostPath" config is required')

        ret = Merger.merge({
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'hostPath': hostPath,
            },
        }, merge_config if merge_config is not None else {})

        if self.storageclass is not None:
            Merger.merge(ret, {
                'spec': {
                    'storageClassName': self.storageclass,
                }
            })

        return ret



class KRPersistentVolumeProfile_NFS(PersistentVolumeProfile):
    def build(self, provider: Provider, name: str, config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        nfs = None
        if config is not None:
            if 'name' in config:
                name = config['name']
            if 'nfs' in config:
                nfs = config['nfs']
        if nfs is None:
            raise InvalidParamError('"nfs" config is required')

        ret = Merger.merge({
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'nfs': nfs,
            },
        }, merge_config if merge_config is not None else {})

        if self.storageclass is not None:
            Merger.merge(ret, {
                'spec': {
                    'storageClassName': self.storageclass,
                }
            })

        return ret


class KRPersistentVolumeProfile_CSI(PersistentVolumeProfile):
    def build(self, provider: Provider, name: str, config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        csi = None
        if config is not None:
            if 'name' in config:
                name = config['name']
            if 'csi' in config:
                csi = config['csi']
        if csi is None:
            raise InvalidParamError('"csi" config is required')

        ret = Merger.merge({
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'csi': csi,
            },
        }, merge_config if merge_config is not None else {})

        if self.storageclass is not None:
            Merger.merge(ret, {
                'spec': {
                    'storageClassName': self.storageclass,
                }
            })

        return ret


class KRPersistentVolumeProfile_AWSElasticBlockStore(PersistentVolumeProfile):
    def build(self, provider: Provider, name: str, config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        specdata = {}
        if config is not None:
            if 'name' in config:
                name = config['name']
            if 'csi' in config:
                if 'volumeHandle' in config['csi']:
                    specdata['volumeID'] = config['csi']['volumeHandle']
                if 'fsType' in config['csi']:
                    specdata['fsType'] = config['csi']['fsType']
                if 'readOnly' in config['csi']:
                    specdata['readOnly'] = config['csi']['readOnly']

        ret = Merger.merge({
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'awsElasticBlockStore': specdata,
            },
        }, merge_config if merge_config is not None else {})

        if self.storageclass is not None:
            Merger.merge(ret, {
                'spec': {
                    'storageClassName': self.storageclass,
                }
            })

        return ret


class KRPersistentVolumeProfile_CSI_AWSEBS(KRPersistentVolumeProfile_CSI):
    def build(self, provider: Provider, name: str, config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        specdata = {
            'driver': 'ebs.csi.aws.com',
        }
        if config is not None:
            if 'name' in config:
                name = config['name']
            if 'nodriver' in config and config['nodriver'] is True:
                del specdata['driver']
            if 'csi' in config:
                Merger.merge(specdata, config['csi'])

        ret = Merger.merge({
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'csi': specdata,
            },
        }, merge_config if merge_config is not None else {})

        if self.storageclass is not None:
            Merger.merge(ret, {
                'spec': {
                    'storageClassName': self.storageclass,
                }
            })

        return ret


class KRPersistentVolumeProfile_CSI_AWSEFS(KRPersistentVolumeProfile_CSI):
    def build(self, provider: Provider, name: str, config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        specdata = {
            'driver': 'efs.csi.aws.com',
        }
        if config is not None:
            if 'name' in config:
                name = config['name']
            if 'nodriver' in config and config['nodriver'] is True:
                del specdata['driver']
            if 'csi' in config:
                Merger.merge(specdata, config['csi'])

        ret = Merger.merge({
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'csi': specdata,
            },
        }, merge_config if merge_config is not None else {})

        if self.storageclass is not None:
            Merger.merge(ret, {
                'spec': {
                    'storageClassName': self.storageclass,
                }
            })

        return ret


class KRPersistentVolumeProfile_GCEPersistentDisk(PersistentVolumeProfile):
    def build(self, provider: Provider, name: str, config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        specdata = {}
        if config is not None:
            if 'name' in config:
                name = config['name']
            if 'csi' in config:
                if 'volumeHandle' in config['csi']:
                    specdata['pdName'] = config['csi']['volumeHandle']
                if 'fsType' in config['csi']:
                    specdata['fsType'] = config['csi']['fsType']
                if 'readOnly' in config['csi']:
                    specdata['readOnly'] = config['csi']['readOnly']

        ret = Merger.merge({
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'gcePersistentDisk': specdata,
            },
        }, merge_config if merge_config is not None else {})

        if self.storageclass is not None:
            Merger.merge(ret, {
                'spec': {
                    'storageClassName': self.storageclass,
                }
            })

        return ret


class KRPersistentVolumeProfile_CSI_GCEPD(KRPersistentVolumeProfile_CSI):
    def build(self, provider: Provider, name: str, config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        specdata = {
            'driver': 'pd.csi.storage.gke.io',
        }
        if config is not None:
            if 'name' in config:
                name = config['name']
            if 'nodriver' in config and config['nodriver'] is True:
                del specdata['driver']
            if 'csi' in config:
                Merger.merge(specdata, config['csi'])

        ret = Merger.merge({
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'csi': specdata,
            },
        }, merge_config if merge_config is not None else {})

        if self.storageclass is not None:
            Merger.merge(ret, {
                'spec': {
                    'storageClassName': self.storageclass,
                }
            })

        return ret


class KRPersistentVolumeProfile_CSI_DOBS(KRPersistentVolumeProfile_CSI):
    noformat: Optional[bool]

    def __init__(self, storageclass: Optional[str] = None, noformat: Optional[bool] = True):
        super().__init__(storageclass)
        self.noformat = noformat

    def build(self, provider: Provider, name: str, config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        specdata = {
            'driver': 'dobs.csi.digitalocean.com',
        }
        if config is not None:
            if 'name' in config:
                name = config['name']
            if 'nodriver' in config and config['nodriver'] is True:
                del specdata['driver']
            if 'csi' in config:
                Merger.merge(specdata, config['csi'])

        if self.noformat is not None:
            if 'volumeAttributes' not in specdata:
                specdata['volumeAttributes'] = {}
            if 'com.digitalocean.csi/noformat' not in specdata['volumeAttributes']:
                specdata['volumeAttributes']['com.digitalocean.csi/noformat'] = QuotedStr(
                    'false' if self.noformat is False else 'true')

        ret = Merger.merge({
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'csi': specdata,
            },
        }, merge_config if merge_config is not None else {})

        if 'volumeHandle' in specdata and specdata['volumeHandle'] is not None:
            # https://github.com/digitalocean/csi-digitalocean/blob/master/examples/kubernetes/pod-single-existing-volume/README.md
            Merger.merge(ret, {
                'metadata': {
                    'annotations': {
                        'pv.kubernetes.io/provisioned-by': 'dobs.csi.digitalocean.com',
                    }
                }
            })

        storageclass = 'do-block-storage'
        if self.storageclass is not None:
            storageclass = self.storageclass

        Merger.merge(ret, {
            'spec': {
                'storageClassName': storageclass,
            }
        })

        return ret


class KRPersistentVolumeClaimProfile_Default(PersistentVolumeClaimProfile):
    def build(self, provider: Provider, name: str, config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        namespace = None
        persistentVolume: Optional[ObjectItem] = None
        if config is not None:
            if 'name' in config:
                name = config['name']
            if 'namespace' in config:
                namespace = config['namespace']
            if 'persistentVolume' in config:
                persistentVolume = provider.persistentvolume_build(config['persistentVolume'])[0]

        pvdata = {
            'apiVersion': 'v1',
            'kind': 'PersistentVolumeClaim',
            'metadata': {
                'name': name,
            },
            'spec': {
            },
        }
        if namespace is not None:
            pvdata['metadata']['namespace'] = namespace
        if self.storageclass is not None:
            pvdata['spec']['storageClassName'] = self.storageclass
        if persistentVolume is not None:
            if dict_has_name(persistentVolume, 'spec.storageClassName'):
                pv_storageclassname = dict_get_value(persistentVolume, 'spec.storageClassName')
                if pv_storageclassname is not None:
                    pvdata['spec']['storageClassName'] = pv_storageclassname

        ret = Merger.merge(pvdata, merge_config if merge_config is not None else {})

        if persistentVolume is not None:
            if not dict_has_name(ret, 'spec.accessModes') and dict_has_name(persistentVolume, 'spec.accessModes'):
                ret['spec']['accessModes'] = persistentVolume['spec']['accessModes']
            if not dict_has_name(ret, 'spec.resources.requests.storage') and dict_has_name(persistentVolume, 'spec.capacity.storage'):
                Merger.merge(ret, {
                    'spec': {
                        'resources': {
                            'requests': {
                                'storage': dict_get_value(persistentVolume, 'spec.capacity.storage'),
                            }
                        }
                    }
                })

        return ret
