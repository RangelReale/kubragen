import copy
from typing import Any, Mapping, Sequence, MutableMapping, MutableSequence, Union

from .exception import InvalidOperationError
from .merger import Merger


class Data:
    """
    Base class to represent data that can be disabled by a flag.
    The :func:`get_value` function allows for dynamic code generation if needed.
    """
    def is_enabled(self) -> bool:
        """
        Whether the data is enabled. If not, it will be removed from the :class:`kubragen.object.Object` when set to it.
        """
        raise NotImplementedError()

    def get_value(self) -> Any:
        """
        Returns the value of the data.

        :return: the data value
        """
        raise NotImplementedError()


class DisabledData(Data):
    """A :class:`Data` class that is always disabled."""
    def is_enabled(self) -> bool:
        return False

    def get_value(self) -> Any:
        return None


class ValueData(Data):
    """
    A :class:`Data` class with constant values.

    :param value: the value to return in :func:`get_value`
    :param enabled: whether the data is enabled
    :param disabled_if_none: set enabled=False if value is None
    """
    def __init__(self, value = None, enabled: bool = True, disabled_if_none: bool = False):
        self.value = value
        self.enabled = enabled
        if disabled_if_none and value is None:
            self.enabled = False

    def is_enabled(self) -> bool:
        return self.enabled

    def get_value(self) -> Any:
        return self.value


class MergeData(Data):
    def __init__(self, value):
        self.value = value

    def is_enabled(self) -> bool:
        return True

    def get_value(self) -> Any:
        return self.value


class ConfigDataMerge(ValueData):
    def __init__(self, value = None, enabled: bool = True, default_merge = None, config = None):
        super().__init__(value, enabled)
        self.default_merge = default_merge
        self.config = config

    def get_value(self):
        ret = super().get_value()
        if isinstance(self.config, MergeData):
            Merger.merge(ret, self.config.get_value())
        else:
            if self.default_merge is not None:
                Merger.merge(ret, self.default_merge)
        return ret


def DataIsNone(value: Any) -> bool:
    """
    Checks if the value is None.
    If value is an instance of :class:`Data`, check its *is_enabled()* method.

    :param value: the value to check for None
    :return: whether the value is None or disabled
    """
    if isinstance(value, Data):
        if not value.is_enabled():
            return True
        return DataIsNone(value.get_value())
    return value is None


def DataGetValue(value: Any, raise_if_disabled: bool = False) -> Any:
    """
    Returns the value.
    If value is an instance of :class:`Data`, call its get_value() method, or return None if
    not enabled.

    :param value: the value to check
    :param raise_if_disabled: whether to raise an exception if the value is disabled.
    :return: the value
    :raises: :class:`kubragen.exception.InvalidOperationError`
    """
    if isinstance(value, Data):
        if not value.is_enabled():
            if raise_if_disabled:
                raise InvalidOperationError('Value is disabled')
            return None
        return DataGetValue(value.get_value())
    return value


def DataCleanProp(data: Union[MutableMapping, MutableSequence], key: Any) -> None:
    """
    Cleanup instances of Data class in Mapping or Sequence.
    """
    if isinstance(data[key], Data):
        if not data[key].is_enabled():
            del data[key]
        else:
            data[key] = data[key].get_value()


def DataClean(data: Any, in_place: bool = True) -> Any:
    """
    Cleanup all instances of Data classes, removing if not enabled or replacing by its value.

    :param data: the data to mutate
    :param in_place: whether to modify the data in-place. If False, data will be duplicated
        using copy.deepcopy
    :return: the same value passed, mutated, except if it is *Data{enabled=False}*, in this case it returns None.
    """
    if not in_place:
        data = copy.deepcopy(data)
    if isinstance(data, MutableMapping):
        keylist = list(data.keys())
        for key in keylist:
            DataCleanProp(data, key)
        for item in data.values():
            DataClean(item)
    elif isinstance(data, MutableSequence):
        for key in range(len(data) - 1, -1, -1):
            DataCleanProp(data, key)
        for item in data:
            DataClean(item)
    return DataGetValue(data)
