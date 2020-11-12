from typing import Any, Optional, Tuple, Protocol, List

from .data import Data, DataClean
from .exception import OptionError
from .option import Option, OptionRoot, OptionDef, OptionValue
from .private.options import OptionsCheckDefinitions
from .util import dict_get_value, dict_has_name, is_allowed_types, type_name


class OptionsBase:
    """
    List of options.

    :param defined_options: the list of defined options.
    :param options: the options to be set. If options are defined in *defined_options*,
                    only declared options are allowed to be changed.

    :raises: :class:`kubragen.exception.OptionError`
    """
    defined_options: Any
    options: Any

    def __init__(self, defined_options: Optional[Any] = None, options: Optional[Any] = None):
        self.defined_options = defined_options
        self.options = options
        OptionsCheckDefinitions(self.defined_options, self.options)

    def value_definition_get(self, name: str) -> Tuple[Option, Any]:
        """
        Gets an option definition and value by name.

        :param name: the option name in dot format (config.service_port)
        :return: a tuple of the option definition and value
        """
        definition = dict_get_value(self.defined_options, name)
        if not isinstance(definition, Option):
            raise OptionError('Invalid option definition type: "{}"'.format(repr(definition)))
        if self.options is not None and dict_has_name(self.options, name):
            return definition, dict_get_value(self.options, name)
        return definition, definition

    def value_get(self, name: str) -> Any:
        """
        Gets an option value by name.

        :param name: the option name in dot format (config.service_port)
        :return: the option value
        """
        if self.defined_options is None:
            return dict_get_value(self.options, name)
        return self.value_definition_get(name)[1]


class Options(OptionsBase):
    """
    List of options.

    Generators should override :func:`define_options` and declare its options.
    If any options is declared in :func:`define_options`, only these options are allowed to be set,
    otherwise there is no restriction.

    :param options: the options to be set. If options are defined in :func:`define_options`,
                    only declared options are allowed to be changed.

    :raises: :class:`kubragen.exception.OptionError`
    """
    def __init__(self, options: Optional[Any] = None):
        super().__init__(defined_options=self.define_options(), options=options)

    def define_options(self) -> Optional[Any]:
        """
        Declares the options that are supported by this instance.
        If None, don't limit the possible option values.

        :return: The supported options
        """
        return None


def option_root_get(options: OptionsBase, name: str, root_options: Optional[OptionsBase] = None,
                    handle_data: bool = True) -> Any:
    """
    Get an option value using the root options if requested using :class:`OptionRoot`

    :param options: the builder options to get the primary options from
    :param name: the option name in dot format (config.service_port)
    :param root_options: the root options if available
    :param handle_data: whether to process :class:`kubragen.data.Data` instances or return them.
    :return: the option value
    :raises: :class:`kubragen.exception.OptionError`
    :raises: :class:`kubragen.exception.TypeError`
    """
    definition, value = options.value_definition_get(name)
    if isinstance(value, OptionRoot):
        if root_options is None:
            raise TypeError('Cannot get option from root')
        value = root_options.value_get(value.name)

    if isinstance(value, OptionDef):
        value = value.default_value

    if isinstance(value, OptionValue):
        value = value.get_value(name, definition)

    if not isinstance(value, Data):
        if isinstance(definition, OptionDef):
            if not is_allowed_types(value, definition.allowed_types, required=definition.required):
                if definition.allowed_types is None or (value is None and definition.required):
                    raise TypeError('Option "{}" is required'.format(name))

                tprint: List[Any] = []
                if not definition.required:
                    tprint.append(None)
                tprint.extend(definition.allowed_types)

                raise TypeError('Type "{}" for option "{}" is not in the allowed types ({})'.format(
                    type_name(value), name, ', '.join(['"{}"'.format(type_name(t)) for t in tprint])
                ))

    if handle_data:
        return DataClean(value, in_place=False)
    return value


class OptionGetter(Protocol):
    """
    Protocol for option getters
    """
    def option_get(self, name: str) -> Any:
        """
        Get an option value.

        :param name: the option name in dot format (config.service_port)
        :return: the option value
        :raises: :class:`kubragen.exception.OptionError`
        :raises: :class:`kubragen.exception.TypeError`
        """
        ...
