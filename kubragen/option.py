from enum import Enum
from typing import Any, Optional, Sequence, Callable


class Option:
    """
    Base option class.
    """
    pass


class OptionDefFlags(Enum):
    """
    Option flags. Reserved for future.
    """
    RESERVED = 255


class OptionDefFormat(Enum):
    """
    Format of OptionDef. This is meant to document advanced types to indicate a custom class can be used
    and will be treated differently.
    """

    ANY = 1
    """Default format"""

    KDATA_ENV = 2
    """Option will be a Kubernetes container env param"""

    KDATA_VOLUME = 2
    """Option will be a Kubernetes container volume param"""

    def is_kdata(self) -> bool:
        """
        Checks whether the OptionDef type is a :class:`kubragen.kdata.KData` object.
        """
        return self in [self.KDATA_ENV, self.KDATA_VOLUME]


class OptionDef(Option):
    """
    Option definition to be used by builders to declare the options it support.
    Generators are required to use this class to define its options so the replacing logic works correctly.

    :param required: Whether the option is erquired
    :param default_value: The default valued to use if not set by the builder user
    :param flags: Option flags (See :class:`OptionDefFlags`)
    :param format: Option format (See :class:`OptionDefFormat`)
    :param allowed_types: a list of allowed types, to be checked with :func:`isinstance`.
        If *None*, no type check is made. If *required* is False, :class:`None` is
        automatically allowed.
    """
    required: bool
    default_value: Optional[Any]
    flags: Sequence[OptionDefFlags]
    format: OptionDefFormat
    allowed_types: Optional[Sequence[Any]]

    def __init__(self, required: bool = False, default_value: Optional[Any] = None,
                 flags: Optional[Sequence[OptionDefFlags]] = None, format: OptionDefFormat = OptionDefFormat.ANY,
                 allowed_types: Optional[Sequence[Any]] = None):
        self.required = required
        self.default_value = default_value
        self.flags = flags if flags is not None else []
        self.format = format
        self.allowed_types = allowed_types

    def is_flag(self, flag: OptionDefFlags) -> bool:
        """
        Checks whether the flag is set
        :param flag: flag to check
        :return: True if flag is set
        """
        return flag in self.flags


class OptionRoot(Option):
    """
    Indicate that a global option value should be used.

    This should be used by the users of builders.

    :param name: the option name in dot format (config.service_port)
    """
    name: str

    def __init__(self, name: str):
        self.name = name


class OptionValue(Option):
    """
    Base class for option values.

    :param name: option name if available
    :param base_option: previous option value if available
    :return: the option value
    """
    def get_value(self, name: Optional[str] = None, base_option: Optional[Option] = None) -> Any:
        raise NotImplementedError()


class OptionDefaultValue(OptionValue):
    """
    Return the default value of the base value.
    """
    def get_value(self, name: Optional[str] = None, base_option: Optional[Option] = None) -> Any:
        if isinstance(base_option, OptionDef):
            return base_option.default_value
        return base_option


class OptionValueCallable(OptionValue):
    """
    Use a callable to get the option value.
    """
    valuefunc: Callable[[Optional[str], Optional[Option]], Any]

    def __init__(self, valuefunc: Callable[[Optional[str], Optional[Option]], Any]):
        self.valuefunc = valuefunc

    def get_value(self, name: Optional[str] = None, base_option: Optional[Option] = None) -> Any:
        return self.valuefunc(name, base_option)
