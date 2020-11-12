import base64
from typing import Union, Sequence, Optional

import semver # type: ignore

from .consts import PROVIDER_GENERIC, PROVIDERSVC_GENERIC, DEFAULT_KUBERNETES_VERSION
from .exception import InvalidParamError
from .object import ObjectItem
from .types import TProvider, TProviderSvc


class Provider:
    """
    Represents a target Kubernetes service provider to allow builders to customize objects.

    :param provider: The service provider (Google, Amazon, etc)
    :param service: The Kubernetes service in the service provider (GKE, EKS, etc)
    :param kubernetes_version: Target Kubernetes version, to be parsed using the :mod:`semver` module
    """
    provider: TProvider
    service: TProviderSvc
    kubernetes_version: semver.VersionInfo

    def __init__(self, provider: TProvider, service: TProviderSvc,
                 kubernetes_version: Optional[Union[str, semver.VersionInfo]] = None):
        self.provider = provider
        self.service = service
        if kubernetes_version is None:
            kubernetes_version = DEFAULT_KUBERNETES_VERSION
        if isinstance(kubernetes_version, semver.VersionInfo):
            self.kubernetes_version = kubernetes_version
        else:
            try:
                self.kubernetes_version = semver.VersionInfo.parse(kubernetes_version)
            except Exception as e:
                raise InvalidParamError(str(e)) from e

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

    def objects_check(self, objects: Sequence[ObjectItem]) -> Sequence[ObjectItem]:
        """
        Checks and modifies the list of objects for provider-specific properties.

        :param objects: list of :class:`kubragen.object.ObjectItem`
        :return: the modified list of objects.
        """
        return objects


class Provider_Generic(Provider):
    """
    A generic provider.
    """
    def __init__(self, kubernetes_version: Optional[Union[str, semver.VersionInfo]] = None):
        super().__init__(provider=PROVIDER_GENERIC, service=PROVIDERSVC_GENERIC, kubernetes_version=kubernetes_version)
