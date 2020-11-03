import base64
from typing import Union

from .consts import PROVIDER_GENERIC, PROVIDERSVC_GENERIC
from .types import TProvider, TProviderSvc


class Provider:
    """
    Represents a target Kubernetes service provider to allow builders to customize objects.

    :param provider: The service provider (Google, Amazon, etc)
    :param service: The Kubernetes service in the service provider (GKE, EKS, etc)
    """
    provider: TProvider
    service: TProviderSvc

    def __init__(self, provider: TProvider, service: TProviderSvc):
        self.provider = provider
        self.service = service

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


class Provider_Generic(Provider):
    """
    A generic provider.
    """
    def __init__(self):
        super().__init__(provider=PROVIDER_GENERIC, service=PROVIDERSVC_GENERIC)
