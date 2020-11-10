import base64
import copy
from typing import Union, Optional, Any, Sequence, Dict

from .consts import PROVIDER_GENERIC, PROVIDERSVC_GENERIC
from .object import ObjectItem
from .types import TProvider, TProviderSvc


class Provider:
    """
    Represents a target Kubernetes service provider to allow builders to customize objects.

    :param provider: The service provider (Google, Amazon, etc)
    :param service: The Kubernetes service in the service provider (GKE, EKS, etc)
    """
    provider: TProvider
    service: TProviderSvc

    _storageclasses: Dict[str, Any]
    _persistentvolumeprofiles: Dict[str, 'PersistentVolumeProfile']
    _persistentvolumeclaimprofiles: Dict[str, 'PersistentVolumeClaimProfile']
    _persistentvolumes: Dict[Any, Any]
    _persistentvolumeclaims: Dict[Any, Any]

    def __init__(self, provider: TProvider, service: TProviderSvc):
        self.provider = provider
        self.service = service
        self._storageclasses = {}
        self._persistentvolumeprofiles = {}
        self._persistentvolumeclaimprofiles = {}
        self._persistentvolumes = {}
        self._persistentvolumeclaims = {}

    def secret_data_encode(self, data: Union[bytes, str]) -> str:
        """
        Encode bytes or str secret using the current provider.
        By default encoding is done using base64, using the utf-8 charset.

        :param data: Data to encode
        :return: encoded secret
        :raises: KGException
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self.secret_data_encode_bytes(data).decode("utf-8")

    def secret_data_encode_bytes(self, data: bytes) -> bytes:
        """
        Encode bytes secret using the current provider.
        By default encoding is done using base64, and raw bytes are returned

        :param data: Data to encode
        :return: encoded secret
        :raises: KGException
        """
        return base64.b64encode(data)

    def persistentvolumeprofile_add(self, name: str, profile: 'PersistentVolumeProfile'):
        self._persistentvolumeprofiles[name] = profile

    def persistentvolumeclaimprofile_add(self, name: str, profile: 'PersistentVolumeClaimProfile'):
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

    def persistentvolume_build(self, *persistentvolumenames: str) -> Sequence[ObjectItem]:
        ret = []
        for pvname, pvdata in self._persistentvolumes.items():
            if len(persistentvolumenames) == 0 or pvname in persistentvolumenames:
                ret.append(self._persistentvolumeprofiles[pvdata['profile']].build(self, pvname, pvdata['config'], pvdata['merge_config']))
        return ret

    def persistentvolumeclaim_build(self, *persistentvolumeclaimnames: str) -> Sequence[ObjectItem]:
        ret = []
        for pvcname, pvcdata in self._persistentvolumeclaims.items():
            if len(persistentvolumeclaimnames) == 0 or pvcname in persistentvolumeclaimnames:
                ret.append(self._persistentvolumeclaimprofiles[pvcdata['profile']].build(self, pvcname, pvcdata['config'], pvcdata['merge_config']))
        return ret

    def storageclass_add(self, name, config: Any):
        self._storageclasses[name] = config

    def storageclass_build(self, *storageclassesnames: str) -> Sequence[ObjectItem]:
        ret = []
        for scname, scvalue in self._storageclasses.items():
            if len(storageclassesnames) == 0 or scname in storageclassesnames:
                ret.append(scvalue)
        return copy.deepcopy(ret)


class ProviderBuilder:
    def build(self, provider: Provider, name: str, config: Optional[Any], merge_config: Optional[Any]) -> ObjectItem:
        raise NotImplementedError()


class PersistentVolumeProfile(ProviderBuilder):
    storageclass: Optional[str]

    def __init__(self, storageclass: Optional[str] = None):
        self.storageclass = storageclass


class PersistentVolumeClaimProfile(ProviderBuilder):
    storageclass: Optional[str]

    def __init__(self, storageclass: Optional[str] = None):
        self.storageclass = storageclass


class Provider_Generic(Provider):
    """
    A generic provider.
    """
    def __init__(self):
        super().__init__(provider=PROVIDER_GENERIC, service=PROVIDERSVC_GENERIC)
