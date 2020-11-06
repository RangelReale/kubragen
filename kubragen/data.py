from typing import Any, Mapping, Sequence

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

    def __getitem__(self, key):
        """Simulate dict/list access for the data value."""
        if not self.is_enabled():
            raise KeyError('Key "{}" not found because data is disabled'.format(key))
        if isinstance(self.get_value(), Mapping):
            return self.get_value()[key]
        elif isinstance(self.get_value(), Sequence):
            return self.get_value()[key]
        raise KeyError('Key "{}" not found because data is not dict or list'.format(key))


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


def ValueIsNone(value: Any) -> bool:
    """
    Checks if the value is None.
    If value is an instance of :class:`Data`, check its *is_enabled()* method.

    :param value: the value to check for None
    :return: whether the value is None or disabled
    """
    if isinstance(value, Data):
        if not value.is_enabled():
            return True
        return ValueIsNone(value.get_value())
    return value is None
