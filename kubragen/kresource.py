import copy
from typing import Optional, Any, Sequence, Dict

from kubragen.exception import InvalidParamError
from kubragen.helper import QuotedStr
from kubragen.merger import Merger
from kubragen.object import ObjectItem
from kubragen.provider import Provider
from kubragen.util import dict_get_value, dict_has_name


class KResourceBuilder:
    """
    Kubernetes generic resource builder.
    """
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        """
        Builds a resource and return an ObjectItem.

        :param provider: provider to target the resource.
        :param resources: the resource database.
        :param name: the resource name.
        :param config: a resource builder configuration
        :param merge_config: a :class:`Mapping` to merge to the final object.
        :return: an :class:`kubragen.object.ObjectItem`
        """
        raise NotImplementedError()


class KRStorageClass(KResourceBuilder):
    """
    A Kubernetes StorageClass builder.
    """
    pass


class KRPersistentVolumeProfile(KResourceBuilder):
    """
    A Kubernetes PersistentVolume builder.
    """
    storageclass: Optional[str]

    def __init__(self, storageclass: Optional[str] = None):
        self.storageclass = storageclass


class KRPersistentVolumeClaimProfile(KResourceBuilder):
    """
    A Kubernetes PersistentVolumeClaims builder.
    """
    storageclass: Optional[str]

    def __init__(self, storageclass: Optional[str] = None):
        self.storageclass = storageclass


class KResourceDatabase:
    """
    A Kubernetes resource database.
    """
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

    def persistentvolumeprofile_add(self, name: str, profile: KRPersistentVolumeProfile) -> None:
        """
        Adds a persistent volume profile.

        :param name: profile name
        :param profile: profile builder
        :return: None
        """
        self._persistentvolumeprofiles[name] = profile

    def persistentvolumeclaimprofile_add(self, name: str, profile: KRPersistentVolumeClaimProfile):
        """
        Adds a persistent volume claim profile.

        :param name: profile name
        :param profile: profile builder
        :return: None
        """
        self._persistentvolumeclaimprofiles[name] = profile

    def persistentvolume_add(self, name: str, profile: str, config: Optional[Any] = None,
                             merge_config: Optional[Any] = None):
        """
        Adds a persistent volume.

        :param name: persistent volume name
        :param profile: persistent volume profile name
        :param config: a resource builder configuration
        :param merge_config: a :class:`Mapping` to merge to the final object.
        :return: None
        """
        self._persistentvolumes[name] = {
            'profile': profile,
            'config': config,
            'merge_config': merge_config,
        }

    def persistentvolumeclaim_add(self, name: str, profile: str,
                                  config: Optional[Any] = None, merge_config: Optional[Any] = None):
        """
        Adds a persistent volume claim.

        :param name: persistent volume claim name
        :param profile: persistent volume claim profile name
        :param config: a resource builder configuration
        :param merge_config: a :class:`Mapping` to merge to the final object.
        :return: None
        """
        self._persistentvolumeclaims[name] = {
            'profile': profile,
            'config': config,
            'merge_config': merge_config,
        }

    def persistentvolume_build(self, provider: Provider, *persistentvolumenames: str) -> Sequence[ObjectItem]:
        """
        Generates one or more persistent volumes.

        :param provider: provider to target the resource.
        :param persistentvolumenames: list of persistent volume names
        :return: list of :class:`kubragen.object.ObjectItem`
        """
        ret = []
        for pvname, pvdata in self._persistentvolumes.items():
            if len(persistentvolumenames) == 0 or pvname in persistentvolumenames:
                ret.append(self._persistentvolumeprofiles[pvdata['profile']].build(provider, self, pvname, pvdata['config'], pvdata['merge_config']))
        return ret

    def persistentvolumeclaim_build(self, provider: Provider, *persistentvolumeclaimnames: str) -> Sequence[ObjectItem]:
        """
        Generates one or more persistent volume claims.

        :param provider: provider to target the resource.
        :param persistentvolumeclaimnames: list of persistent volume claim names
        :return: list of :class:`kubragen.object.ObjectItem`
        """
        ret = []
        for pvcname, pvcdata in self._persistentvolumeclaims.items():
            if len(persistentvolumeclaimnames) == 0 or pvcname in persistentvolumeclaimnames:
                ret.append(self._persistentvolumeclaimprofiles[pvcdata['profile']].build(provider, self, pvcname, pvcdata['config'], pvcdata['merge_config']))
        return ret

    def storageclass_add(self, name, storageclass: KRStorageClass, config: Optional[Any] = None,
                             merge_config: Optional[Any] = None):
        """
        Adds a storage class.

        :param name: persistent volume name
        :param storageclass: storage class
        :param config: a resource builder configuration
        :param merge_config: a :class:`Mapping` to merge to the final object.
        :return: None
        """
        self._storageclasses[name] = {
            'storageclass': storageclass,
            'config': config,
            'merge_config': merge_config,
        }

    def storageclass_build(self, provider: Provider, *storageclassesnames: str) -> Sequence[ObjectItem]:
        """
        Generates one or more storage classes.

        :param provider: provider to target the resource.
        :param storageclassesnames: list of storage class names.
        :return: list of :class:`kubragen.object.ObjectItem`
        """
        ret = []
        for scname, scvalue in self._storageclasses.items():
            if len(storageclassesnames) == 0 or scname in storageclassesnames:
                ret.append(scvalue['storageclass'].build(provider, self, scname, scvalue['config'], scvalue['merge_config']))
        return copy.deepcopy(ret)


class KRStorageClass_Default(KRStorageClass):
    """
    Default storage class. Used to configure manually.
    """
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
    """
    Default persistent volume profile. Used to configure manually.
    """
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
    """
    EmptyDir persistent volume profile.
    """
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
    """
    HostPath persistent volume profile.
    """
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
    """
    NFS persistent volume profile.
    """
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
    """
    CSI persistent volume profile.
    """
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


class KRPersistentVolumeClaimProfile_Default(KRPersistentVolumeClaimProfile):
    """
    Default persistent volume claim profile. Used to configure manually.
    """
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
                persistentVolume = resources.persistentvolume_build(provider, config['persistentVolume'])[0]

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


class KRPersistentVolumeClaimProfile_NoSelector(KRPersistentVolumeClaimProfile_Default):
    """
    Persistent volume claim profile that does not allow using selectors.
    """
    def build(self, provider: Provider, resources: 'KResourceDatabase', name: str,
              config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        ret = super().build(provider, resources, name, config, merge_config)

        persistentVolume: Optional[ObjectItem] = None
        if config is not None:
            if 'persistentVolume' in config:
                persistentVolume = resources.persistentvolume_build(provider, config['persistentVolume'])[0]

        if 'selector' in ret['spec']:
            if persistentVolume is None:
                raise InvalidParamError('PersistentVolumeClaim does not support selector but a PersistentVolume was not supplied')
            del ret['spec']['selector']
            ret['spec']['storageClassName'] = ''
            ret['spec']['volumeName'] = persistentVolume['metadata']['name']

        return ret