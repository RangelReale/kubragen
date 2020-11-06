from typing import Optional, Any, Sequence, Mapping

from .data import ValueData, DisabledData
from .exception import InvalidParamError
from .helper import QuotedStr
from .kdata import KData_Secret, KData_Value, KData_ConfigMap, KData
from .merger import Merger


class KDataHelper:
    """Base class of :class:`kubragen.kdata.KData` helpers."""
    pass


class KDataHelper_Env(KDataHelper):
    """
    KData helpers for Kubernetes *container.env* values.
    """
    @staticmethod
    def allowed_kdata() -> Sequence[Any]:
        """Returns the allowed  list of :class:`KData`"""
        return [KData_Value, KData_ConfigMap, KData_Secret]

    @staticmethod
    def info(base_value, value: Optional[Any] = None, value_if_kdata: Optional[Any] = None,
             default_value: Optional[Any] = None, enabled: bool = True, disable_if_none: bool = False) -> Any:
        """
        Outputs a configuration compatible with the Kubernetes *container.env*.

        If *value* is not a Mapping, it will be considered a simple 'value' field.

        :param base_value: the base dict that is merged with the result, normally containing the name of the object.
        :type base_value: Mapping
        :param value: a value configured by the user, possibly None
        :param value_if_kdata: a :class:`kubragen.kdata.KData` value configured by the user, possibly None. If
            not a KData instance, **it will be ignored**, and you are supposed to set a value in *default_value.
        :param default_value: a default value to use if value is None
        :param enabled: whether the information is enabled. If not, a :class:`kubragen.data.DisabledData` is returned
        :param disable_if_none: automatically disable if value and kdata_value is None
        :return: a configuration compatible with the Kubernetes *container.env* specification
        """
        if not enabled:
            return DisabledData()

        if value_if_kdata is not None and isinstance(value_if_kdata, KData):
            value = value_if_kdata

        if disable_if_none and value is None and value_if_kdata is None:
            return DisabledData()

        ret = base_value
        if ret is None:
            ret = {}

        if isinstance(value, KData):
            if isinstance(value, KData_Value):
                default_value = {
                    'value': QuotedStr(value.value),
                }
            elif isinstance(value, KData_ConfigMap):
                default_value = {
                    'valueFrom': {
                        'configMapKeyRef': {
                            'name': value.configmapName,
                            'key': value.configmapData
                        }
                    },
                }
            elif isinstance(value, KData_Secret):
                default_value = {
                    'valueFrom': {
                        'secretKeyRef': {
                            'name': value.secretName,
                            'key': value.secretData
                        }
                    },
                }
            else:
                raise InvalidParamError('Unsupported KData: "{}"'.format(repr(value)))
        elif value is not None:
            if isinstance(value, Mapping):
                default_value = value
            else:
                default_value = {
                    'value': QuotedStr(value),
                }

        # Check again
        if disable_if_none and default_value is None:
            return DisabledData()

        return Merger.merge(ret, default_value)


class KDataHelper_Volume(KDataHelper):
    """
    KData helpers for Kubernetes *podSpec.volumes* values.
    """
    @staticmethod
    def allowed_kdata() -> Sequence[Any]:
        """Returns the allowed  list of :class:`KData`"""
        return [KData_Value, KData_ConfigMap, KData_Secret]

    @staticmethod
    def info(base_value, value: Optional[Any] = None, value_if_kdata: Optional[Any] = None,
             default_value: Optional[Any] = None, key_path: Optional[str] = None, enabled: bool = True,
             disable_if_none: bool = False):
        """
        Outputs a configuration compatible with the Kubernetes *podSpec.volume* for the passed :class:`KData`,
        with a default value if it was not configured by the user.

        :param base_value: the base dict that is merged with the result, normally containing the name of the object.
        :type base_value: dict
        :param value: a value configured by the user, possibly None
        :param value_if_kdata: a :class:`kubragen.kdata.KData` value configured by the user, possibly None. If
            not a KData instance, **it will be ignored**, and you are supposed to set a value in *default_value.
        :param default_value: a default value to use if value is None
        :param enabled: whether the information is enabled. If not, a :class:`kubragen.data.DisabledData` is returned
        :param disable_if_none: automatically disable if value and kdata_value is None
        :return: a configuration compatible with the Kubernetes *podSpec.volume* specification
        """
        if not enabled:
            return DisabledData()

        if value_if_kdata is not None and isinstance(value_if_kdata, KData):
            value = value_if_kdata

        if disable_if_none and value is None and value_if_kdata is None:
            return DisabledData()

        ret = base_value
        if ret is None:
            ret = {}

        if isinstance(value, KData):
            if isinstance(value, KData_Value):
                default_value = value.value
            elif isinstance(value, KData_ConfigMap):
                default_value = {
                    'configMap': {
                        'name': value.configmapName,
                        'items': [{
                            'key': value.configmapData,
                            'path': value.configmapData if key_path is None else key_path,
                        }],
                    }
                }
            elif isinstance(value, KData_Secret):
                default_value = {
                    'secret': {
                        'secretName': value.secretName,
                        'items': [{
                            'key': value.secretData,
                            'path': value.secretData if key_path is None else key_path,
                        }],
                    }
                }
            else:
                raise InvalidParamError('Unsupported KData: "{}"'.format(repr(value)))
        elif value is not None:
            if isinstance(value, Mapping):
                default_value = value
            else:
                raise InvalidParamError('Unsupported Volume spec: "{}"'.format(str(value)))

        # Check again
        if disable_if_none and default_value is None:
            return DisabledData()

        return Merger.merge(ret, default_value)
