from typing import Optional, Any, List

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
    def allowed_kdata() -> List[Any]:
        """Returns the allowed  list of :class:`KData`"""
        return [KData_Value, KData_ConfigMap, KData_Secret]

    @staticmethod
    def info(base_value, kdata: Optional[Any], default_value: Optional[Any] = None, enabled: bool = True,
             disable_if_none: bool = False) -> Any:
        """
        Outputs a configuration compatible with the Kubernetes *container.env* for the passed :class:`KData`,
        with a default value if it was not configured by the user.

        :param base_value: the base dict that is merged with the result, normally containing the name of the object.
        :type base_value: dict
        :param kdata: a value to check whether it should be treated as a :class:`KData` or not
        :param default_value: a default value to use if kdata is None
        :param enabled: whether the information is enabled. If not, a :class:`kubragen.data.DisabledData` is returned
        :param disable_if_none: automatically disable if default_value is None
        :return: a configuration compatible with the Kubernetes *container.env* specification
        """
        if not enabled:
            return ValueData(enabled=False)

        if disable_if_none and default_value is None:
            return DisabledData()

        ret = base_value
        if ret is None:
            ret = {}

        if isinstance(kdata, KData):
            if isinstance(kdata, KData_Value):
                default_value = {
                    'value': QuotedStr(kdata.value),
                }
            elif isinstance(kdata, KData_ConfigMap):
                default_value = {
                    'valueFrom': {
                        'configMapKeyRef': {
                            'name': kdata.configmapName,
                            'key': kdata.configmapData
                        }
                    },
                }
            elif isinstance(kdata, KData_Secret):
                default_value = {
                    'valueFrom': {
                        'secretKeyRef': {
                            'name': kdata.secretName,
                            'key': kdata.secretData
                        }
                    },
                }
            else:
                raise InvalidParamError('Unsupported KData: "{}"'.format(repr(kdata)))

        if default_value is None:
            default_value = kdata

        # Check again to be sure
        if disable_if_none and default_value is None:
            return ValueData(enabled=False)

        return Merger.merge(ret, default_value)


class KDataHelper_Volume(KDataHelper):
    """
    KData helpers for Kubernetes *podSpec.volumes* values.
    """
    @staticmethod
    def allowed_kdata() -> List[Any]:
        """Returns the allowed  list of :class:`KData`"""
        return [KData_Value, KData_ConfigMap, KData_Secret]

    @staticmethod
    def info(base_value, kdata: Optional[Any], default_value: Optional[Any] = None, key_path: Optional[str] = None,
             enabled: bool = True, disable_if_none: bool = False):
        """
        Outputs a configuration compatible with the Kubernetes *podSpec.volume* for the passed :class:`KData`,
        with a default value if it was not configured by the user.

        :param base_value: the base dict that is merged with the result, normally containing the name of the object.
        :type base_value: dict
        :param kdata: a value to check whether it should be treated as a :class:`KData` or not
        :param default_value: a default value to use if kdata is None
        :param enabled: whether the information is enabled. If not, a :class:`kubragen.data.DisabledData` is returned
        :param disable_if_none: automatically disable if default_value is None
        :return: a configuration compatible with the Kubernetes *podSpec.volume* specification
        """
        if not enabled:
            return ValueData(enabled=False)

        if disable_if_none and default_value is None:
            return ValueData(enabled=False)

        ret = base_value
        if ret is None:
            ret = {}

        if isinstance(kdata, KData):
            if isinstance(kdata, KData_Value):
                default_value = kdata.value
            elif isinstance(kdata, KData_ConfigMap):
                default_value = {
                    'configMap': {
                        'name': kdata.configmapName,
                        'items': [{
                            'key': kdata.configmapData,
                            'path': kdata.configmapData if key_path is None else key_path,
                        }],
                    }
                }
            elif isinstance(kdata, KData_Secret):
                default_value = {
                    'secret': {
                        'secretName': kdata.secretName,
                        'items': [{
                            'key': kdata.secretData,
                            'path': kdata.secretData if key_path is None else key_path,
                        }],
                    }
                }
            else:
                raise InvalidParamError('Unsupported KData: "{}"'.format(repr(kdata)))

        if default_value is None:
            default_value = kdata

        # Check again to be sure
        if disable_if_none and default_value is None:
            return ValueData(enabled=False)

        return Merger.merge(ret, default_value)
