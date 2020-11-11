from typing import Union, Optional, Any, Sequence

import semver

from .consts import DEFAULT_KUBERNETES_VERSION
from .exception import InvalidParamError
from .kresource import KResourceDatabase
from .object import ObjectItem
from .options import Options, option_root_get, OptionsBase
from .provider import Provider


class KubraGen:
    """
    Application class. This class sets the base configurations and provider information used by all builders.

    :param provider: Target Kubernetes provider
    :param options: Global options to be referenced in builders using :class:`kubragen.option.OptionRoot`
    :param kubernetes_version: Target Kubernetes version, to be parsed using the :mod:`semver` module

    :raises: :class:`kubragen.exception.InvalidParamError`
    """
    provider: Provider
    kubernetes_version: semver.VersionInfo
    options: OptionsBase
    _resources: KResourceDatabase

    def __init__(self, provider: Provider, options: Optional[OptionsBase] = None, kubernetes_version: Optional[str] = None):
        self.provider = provider
        if options is None:
            options = Options({})
        if kubernetes_version is None:
            kubernetes_version = DEFAULT_KUBERNETES_VERSION
        try:
            self.kubernetes_version = semver.VersionInfo.parse(kubernetes_version)
        except Exception as e:
            raise InvalidParamError(str(e)) from e
        self.options = options
        self._resources = KResourceDatabase()

    def secret_data_encode(self, data: Union[bytes, str]) -> str:
        """
        Encode bytes or str secret using the current provider.
        By default encoding is done using base64, using the utf-8 charset.

        :param data: Data to encode
        :return: encoded secret
        :raises: :class:`kubragen.exception.KGException`
        """
        return self.provider.secret_data_encode(data)

    def secret_data_encode_bytes(self, data: bytes) -> bytes:
        """
        Encode bytes secret using the current provider.
        By default encoding is done using base64, and raw bytes are returned

        :param data: Data to encode
        :return: encoded secret
        :raises: :class:`kubragen.exception.KGException`
        """
        return self.provider.secret_data_encode_bytes(data)

    def default_quoted_value_single(self) -> bool:
        """
        Determine what quote style will be used in the output Yaml.

        :return: whether the quoted style should be single quotes
        """
        return True

    def option_get(self, name: str) -> Any:
        """
        Get an option value using the from the :class:`KubraGen' instance

        :param name: the option name in dot format (namespace.mon)
        :return: the option value
        :raises: :class:`kubragen.exception.OptionError`
        :raises: :class:`kubragen.exception.TypeError`
        """
        return self.options.value_get(name)

    def option_root_get(self, options: Options, name: str) -> Any:
        """
        Get an option value using the root options if requested using :class:`OptionRoot`

        :param options: the builder options to get the primary options from
        :param name: the option name in dot format (config.service_port)
        :return: the option value
        :raises: :class:`kubragen.exception.OptionError`
        :raises: :class:`kubragen.exception.TypeError`
        """
        return option_root_get(options, name, root_options=self.options)

    def resources(self) -> KResourceDatabase:
        """
        Returns the resource database.
        """
        return self._resources

    def storageclass_build(self, *storageclassesnames: str) -> Sequence[ObjectItem]:
        """
        Generates one or more storage classes.

        :param storageclassesnames: list of storage class names.
        :return: list of :class:`kubragen.object.ObjectItem`
        """
        return self.provider.objects_check(self._resources.storageclass_build(
            self.provider, *storageclassesnames))

    def persistentvolume_build(self, *persistentvolumenames: str) -> Sequence[ObjectItem]:
        """
        Generates one or more persistent volumes.

        :param persistentvolumenames: list of persistent volume names
        :return: list of :class:`kubragen.object.ObjectItem`
        """
        return self.provider.objects_check(self._resources.persistentvolume_build(
            self.provider, *persistentvolumenames))

    def persistentvolumeclaim_build(self, *persistentvolumeclaimnames: str) -> Sequence[ObjectItem]:
        """
        Generates one or more persistent volume claims.

        :param persistentvolumeclaimnames: list of persistent volume claim names
        :return: list of :class:`kubragen.object.ObjectItem`
        """
        return self.provider.objects_check(self._resources.persistentvolumeclaim_build(
            self.provider, *persistentvolumeclaimnames))
