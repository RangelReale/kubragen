from typing import Any, Optional, Mapping, Sequence

from ..exception import OptionError
from ..option import Option


def _options_checkdefinitions(path: Sequence[str], defined_options: Optional[Mapping[Any, Any]],
                              options: Optional[Mapping[Any, Any]]) -> None:
    if defined_options is None or options is None:
        return

    for oname, ovalue in options.items():
        if oname not in defined_options:
            raise OptionError('Unknown option: "{}.{}"'.format('.'.join(path), oname))
        if isinstance(defined_options[oname], Option):
            continue
        if isinstance(ovalue, Mapping):
            _options_checkdefinitions([*path, oname], defined_options[oname], ovalue)


def OptionsCheckDefinitions(defined_options: Optional[Mapping[Any, Any]],
                            options: Optional[Mapping[Any, Any]]) -> None:
    """
    Checks if options match the definitions.

    :param defined_options: the defined options
    :param options: the options to set
    :raises: :class:`kubragen.exception.OptionError`
    """
    _options_checkdefinitions([], defined_options, options)
