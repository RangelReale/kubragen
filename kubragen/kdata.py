from typing import Any, Sequence, Optional, Mapping

from .exception import InvalidParamError


class KData:
    """Base class to represent advanced kubernetes objects."""
    pass


def IsKData(value, allowed: Sequence[Any] = None) -> bool:
    """
    Checks whether the value is a :class:`KData`, and optionally if it is one the allowed types.

    :param value: value to check
    :param allowed: list of :class:`KData` classes to check
    """
    if not isinstance(value, KData):
        return False
    if allowed is not None:
        found = False
        for al in allowed:
            if isinstance(value, al):
                found = True
                break
        if not found:
            raise InvalidParamError('KData type "{}" not allowed (allowed: "{}" '.format(repr(value), repr(allowed)))
    return True


class KData_Value(KData):
    """
    A :class:`KData` with a constant value.

    :param value: the data value
    """
    value: str

    def __init__(self, value: Any):
        self.value = value


class KData_ConfigMap(KData):
    """
    A :class:`KData` that represents a Kubernetes ConfigMap item.

    :param configmapName: ConfigMap name
    :param configmapData: ConfigMap data name
    """
    configmapName: str
    configmapData: str

    def __init__(self, configmapName: str, configmapData: str):
        self.configmapName = configmapName
        self.configmapData = configmapData


class KData_ConfigMapManual(KData):
    """
    A :class:`KData` that represents a Kubernetes ConfigMap.

    :param configmapName: ConfigMap name
    :param merge_config: A Mapping to merge on the result.
    """
    configmapName: str
    merge_config: Optional[Mapping[Any, Any]]

    def __init__(self, configmapName: str, merge_config: Optional[Mapping[Any, Any]] = None):
        self.configmapName = configmapName
        self.merge_config = merge_config


class KData_Secret(KData):
    """
    A :class:`KData` that represents a Kubernetes Secret item.

    :param secretName: Secret name
    :param secretData: Secret data name
    """
    secretName: str
    secretData: str

    def __init__(self, secretName: str, secretData: str):
        self.secretName = secretName
        self.secretData = secretData


class KData_SecretManual(KData):
    """
    A :class:`KData` that represents a Kubernetes Secret.

    :param secretName: Secret name
    :param merge_config: A Mapping to merge on the result.
    """
    secretName: str
    merge_config: Optional[Mapping[Any, Any]]

    def __init__(self, secretName: str, merge_config: Optional[Mapping[Any, Any]] = None):
        self.secretName = secretName
        self.merge_config = merge_config
