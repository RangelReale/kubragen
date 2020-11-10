import copy
from typing import Optional, Any, Sequence, Dict

from kubragen.exception import InvalidParamError
from kubragen.helper import QuotedStr
from kubragen.merger import Merger
from kubragen.object import ObjectItem
from kubragen.provider import Provider
from kubragen.util import dict_get_value, dict_has_name


class KResourceBuilder:
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        raise NotImplementedError()


class KRStorageClass(KResourceBuilder):
    pass


class KRPersistentVolumeProfile(KResourceBuilder):
    storageclass: Optional[str]

    def __init__(self, storageclass: Optional[str] = None):
        self.storageclass = storageclass


class KRPersistentVolumeClaimProfile(KResourceBuilder):
    storageclass: Optional[str]

    def __init__(self, storageclass: Optional[str] = None):
        self.storageclass = storageclass


class KResourceDatabase:
    _persistentvolumeprofiles: Dict[str, KRPersistentVolumeProfile]
    _persistentvolumeclaimprofiles: Dict[str, KRPersistentVolumeClaimProfile]
    _storageclasses: Dict[str, Any]
    _persistentvolumes: Dict[str, Any]
    _persistentvolumeclaims: Dict[str, Any]

    def __init__(self):
        self._persistentvolumeprofiles = {}
        self._persistentvolumeclaimprofiles = {}
        self._storageclasses = {}
        self._persistentvolumes = {}
        self._persistentvolumeclaims = {}

    def persistentvolumeprofile_add(self, name: str, profile: KRPersistentVolumeProfile):
        self._persistentvolumeprofiles[name] = profile

    def persistentvolumeclaimprofile_add(self, name: str, profile: KRPersistentVolumeClaimProfile):
        self._persistentvolumeclaimprofiles[name] = profile

    def persistentvolume_add(self, name: str, profile: str, config: Optional[Any] = None,
                             merge_config: Optional[Any] = None):
        self._persistentvolumes[name] = {
            'profile': profile,
            'config': config,
            'merge_config': merge_config,
        }

    def persistentvolumeclaim_add(self, name: str, profile: str,
                                  config: Optional[Any] = None, merge_config: Optional[Any] = None):
        self._persistentvolumeclaims[name] = {
            'profile': profile,
            'config': config,
            'merge_config': merge_config,
        }

    def persistentvolume_build(self, provider: Provider, *persistentvolumenames: str) -> Sequence[ObjectItem]:
        ret = []
        for pvname, pvdata in self._persistentvolumes.items():
            if len(persistentvolumenames) == 0 or pvname in persistentvolumenames:
                ret.append(self._persistentvolumeprofiles[pvdata['profile']].build(provider, self, pvname, pvdata['config'], pvdata['merge_config']))
        return ret

    def persistentvolumeclaim_build(self, provider: Provider, *persistentvolumeclaimnames: str) -> Sequence[ObjectItem]:
        ret = []
        for pvcname, pvcdata in self._persistentvolumeclaims.items():
            if len(persistentvolumeclaimnames) == 0 or pvcname in persistentvolumeclaimnames:
                ret.append(self._persistentvolumeclaimprofiles[pvcdata['profile']].build(provider, self, pvcname, pvcdata['config'], pvcdata['merge_config']))
        return ret

    def storageclass_add(self, name, storageclass: KRStorageClass, config: Optional[Any] = None,
                             merge_config: Optional[Any] = None):
        self._storageclasses[name] = {
            'storageclass': storageclass,
            'config': config,
            'merge_config': merge_config,
        }

    def storageclass_build(self, provider: Provider, *storageclassesnames: str) -> Sequence[ObjectItem]:
        ret = []
        for scname, scvalue in self._storageclasses.items():
            if len(storageclassesnames) == 0 or scname in storageclassesnames:
                ret.append(scvalue['storageclass'].build(provider, self, scname, scvalue['config'], scvalue['merge_config']))
        return copy.deepcopy(ret)


class KRStorageClass_Default(KRStorageClass):
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        if config is not None:
            if 'name' in config:
                name = config['name']

        ret = Merger.merge({
            'apiVersion': 'storage.k8s.io/v1',
            'kind': 'StorageClass',
            'metadata': {
                'name': name,
            },
        }, merge_config if merge_config is not None else {})

        return ret


class KRPersistentVolumeProfile_Default(KRPersistentVolumeProfile):
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        pvdata = {
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
            },
        }
        if self.storageclass is not None:
            pvdata['spec']['storageClassName'] = self.storageclass
        if config is not None:
            if 'name' in config:
                pvdata['metadata']['name'] = config['name']

        return Merger.merge(pvdata, merge_config if merge_config is not None else {})


class KRPersistentVolumeProfile_EmptyDir(KRPersistentVolumeProfile):
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        pvdata = {
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'emptyDir': {}
            },
        }
        if self.storageclass is not None:
            pvdata['spec']['storageClassName'] = self.storageclass
        if config is not None:
            if 'name' in config:
                pvdata['metadata']['name'] = config['name']

        return Merger.merge(pvdata, merge_config if merge_config is not None else {})


class KRPersistentVolumeProfile_HostPath(KRPersistentVolumeProfile):
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        pvdata = {
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'hostPath': None,
            },
        }
        if self.storageclass is not None:
            pvdata['spec']['storageClassName'] = self.storageclass

        if config is not None:
            if 'name' in config:
                pvdata['metadata']['name'] = config['name']
            if 'hostPath' in config:
                pvdata['spec']['hostPath'] = config['hostPath']

        ret = Merger.merge(pvdata, merge_config if merge_config is not None else {})

        if ret['spec']['hostPath'] is None:
            raise InvalidParamError('"hostPath" is required')

        return ret


class KRPersistentVolumeProfile_NFS(KRPersistentVolumeProfile):
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        pvdata = {
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'nfs': None,
            },
        }
        if self.storageclass is not None:
            pvdata['spec']['storageClassName'] = self.storageclass
        if config is not None:
            if 'name' in config:
                pvdata['metadata']['name'] = config['name']
            if 'nfs' in config:
                pvdata['spec']['nfs'] = config['nfs']

        ret = Merger.merge(pvdata, merge_config if merge_config is not None else {})

        if ret['spec']['nfs'] is None:
            raise InvalidParamError('"nfs" config is required')

        return ret


class KRPersistentVolumeProfile_CSI(KRPersistentVolumeProfile):
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        pvdata = {
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'csi': None,
            },
        }
        if self.storageclass is not None:
            pvdata['spec']['storageClassName'] = self.storageclass
        if config is not None:
            if 'name' in config:
                pvdata['metadata']['name'] = config['name']
            if 'csi' in config:
                pvdata['spec']['csi'] = config['csi']

        ret = Merger.merge(pvdata, merge_config if merge_config is not None else {})

        if ret['spec']['csi'] is None:
            raise InvalidParamError('"csi" config is required')

        return ret


class KRPersistentVolumeProfile_AWSElasticBlockStore(KRPersistentVolumeProfile):
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        pvdata = {
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'awsElasticBlockStore': {},
            },
        }
        if self.storageclass is not None:
            pvdata['spec']['storageClassName'] = self.storageclass
        if config is not None:
            if 'name' in config:
                pvdata['metadata']['name'] = config['name']
            if 'csi' in config:
                if 'volumeHandle' in config['csi']:
                    pvdata['spec']['awsElasticBlockStore']['volumeID'] = config['csi']['volumeHandle']
                if 'fsType' in config['csi']:
                    pvdata['spec']['awsElasticBlockStore']['fsType'] = config['csi']['fsType']
                if 'readOnly' in config['csi']:
                    pvdata['spec']['awsElasticBlockStore']['readOnly'] = config['csi']['readOnly']

        return Merger.merge(pvdata, merge_config if merge_config is not None else {})


class KRPersistentVolumeProfile_CSI_AWSEBS(KRPersistentVolumeProfile_CSI):
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        ret = super().build(provider, resources, name, config, merge_config)
        ret['spec']['csi']['driver'] = 'ebs.csi.aws.com'
        if config is not None:
            if 'nodriver' in config and config['nodriver'] is True:
                del ret['spec']['csi']['driver']
        return ret


class KRPersistentVolumeProfile_CSI_AWSEFS(KRPersistentVolumeProfile_CSI):
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        ret = super().build(provider, resources, name, config, merge_config)
        ret['spec']['csi']['driver'] = 'efs.csi.aws.com'
        if config is not None:
            if 'nodriver' in config and config['nodriver'] is True:
                del ret['spec']['csi']['driver']
        return ret


class KRPersistentVolumeProfile_GCEPersistentDisk(KRPersistentVolumeProfile):
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        pvdata = {
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': name,
            },
            'spec': {
                'gcePersistentDisk': {},
            },
        }
        if config is not None:
            if 'name' in config:
                pvdata['metadata']['name'] = config['name']
            if 'csi' in config:
                if 'volumeHandle' in config['csi']:
                    pvdata['spec']['gcePersistentDisk']['pdName'] = config['csi']['volumeHandle']
                if 'fsType' in config['csi']:
                    pvdata['spec']['gcePersistentDisk']['fsType'] = config['csi']['fsType']
                if 'readOnly' in config['csi']:
                    pvdata['spec']['gcePersistentDisk']['readOnly'] = config['csi']['readOnly']

        return Merger.merge(pvdata, merge_config if merge_config is not None else {})


class KRPersistentVolumeProfile_CSI_GCEPD(KRPersistentVolumeProfile_CSI):
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        ret = super().build(provider, resources, name, config, merge_config)
        ret['spec']['csi']['driver'] = 'pd.csi.storage.gke.io'
        if config is not None:
            if 'nodriver' in config and config['nodriver'] is True:
                del ret['spec']['csi']['driver']
        return ret


class KRPersistentVolumeProfile_CSI_DOBS(KRPersistentVolumeProfile_CSI):
    noformat: Optional[bool]

    def __init__(self, storageclass: Optional[str] = None, noformat: Optional[bool] = True):
        super().__init__(storageclass)
        self.noformat = noformat

    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        ret = super().build(provider, resources, name, config, merge_config)
        ret['spec']['csi']['driver'] = 'dobs.csi.digitalocean.com'
        if config is not None:
            if 'nodriver' in config and config['nodriver'] is True:
                del ret['spec']['csi']['driver']

        if self.noformat is not None:
            if 'volumeAttributes' not in ret['spec']['csi']:
                ret['spec']['csi']['volumeAttributes'] = {}
            if 'com.digitalocean.csi/noformat' not in ret['spec']['csi']['volumeAttributes']:
                ret['spec']['csi']['volumeAttributes']['com.digitalocean.csi/noformat'] = QuotedStr(
                    'false' if self.noformat is False else 'true')

        if 'volumeHandle' in ret['spec']['csi'] and ret['spec']['csi']['volumeHandle'] is not None:
            # https://github.com/digitalocean/csi-digitalocean/blob/master/examples/kubernetes/pod-single-existing-volume/README.md
            Merger.merge(ret, {
                'metadata': {
                    'annotations': {
                        'pv.kubernetes.io/provisioned-by': 'dobs.csi.digitalocean.com',
                    }
                }
            })

        if 'storageClassName' not in ret['spec']:
            ret['spec']['storageClassName'] = 'do-block-storage'

        return ret


class KRPersistentVolumeClaimProfile_Default(KRPersistentVolumeClaimProfile):
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        pvcdata = {
            'apiVersion': 'v1',
            'kind': 'PersistentVolumeClaim',
            'metadata': {
                'name': name,
            },
            'spec': {
            },
        }
        if self.storageclass is not None:
            pvcdata['spec']['storageClassName'] = self.storageclass

        persistentVolume: Optional[ObjectItem] = None
        if config is not None:
            if 'name' in config:
                pvcdata['metadata']['name'] = config['name']
            if 'namespace' in config:
                pvcdata['metadata']['namespace'] = config['namespace']
            if 'persistentVolume' in config:
                persistentVolume = resources.persistentvolume_build(config['persistentVolume'])[0]

        if persistentVolume is not None:
            if dict_has_name(persistentVolume, 'spec.storageClassName'):
                pv_storageclassname = dict_get_value(persistentVolume, 'spec.storageClassName')
                if pv_storageclassname is not None:
                    pvcdata['spec']['storageClassName'] = pv_storageclassname

            if not dict_has_name(pvcdata, 'spec.accessModes') and dict_has_name(persistentVolume, 'spec.accessModes'):
                pvcdata['spec']['accessModes'] = persistentVolume['spec']['accessModes']

            if not dict_has_name(pvcdata, 'spec.resources.requests.storage') and dict_has_name(persistentVolume, 'spec.capacity.storage'):
                Merger.merge(pvcdata, {
                    'spec': {
                        'resources': {
                            'requests': {
                                'storage': dict_get_value(persistentVolume, 'spec.capacity.storage'),
                            }
                        }
                    }
                })

        return Merger.merge(pvcdata, merge_config if merge_config is not None else {})