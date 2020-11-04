from typing import Mapping, Any, Sequence, Optional, MutableMapping

from .exception import OptionError


def dict_has_name(dict: Mapping, name: str) -> bool:
    """Checks if the dict has a name using a dotted accessor-string

    :param dict: source dictionary
    :param name: dotted value name
    """
    current_data = dict
    for chunk in name.split('.'):
        if chunk not in current_data:
            return False
        current_data = current_data.get(chunk, {})
    return True


def dict_get_value(dict: Mapping, name: str) -> Any:
    """Gets data from a dictionary using a dotted accessor-string

    :param dict: source dictionary
    :param name: dotted value name
    """
    current_data = dict
    for chunk in name.split('.'):
        if not isinstance(current_data, (Mapping, Sequence)):
            raise OptionError('Could not find option "{}"'.format(name))
        if chunk not in current_data:
            raise OptionError('Could not find option "{}"'.format(name))
        current_data = current_data.get(chunk, {})
    return current_data


def dict_flatten(d, parent_key='', sep='.') -> Mapping:
    """
    Flatten a dict to a single level.
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(dict_flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def urljoin(*args: str) -> str:
    """
    Join an array of strings using a forward-slash representing an url.

    :param args: list of strings to join
    :return: joined strings
    """
    return "/".join(map(lambda x: str(x).rstrip('/'), args))


def type_name(t) -> str:
    """
    Gets a string naming the type
    :param t: value to get type if
    :return: the type name
    """
    if not isinstance(t, type):
        t = type(t)

    # if isinstance(t, type):
    #     raise TypeError('T is "type"')

    return getattr(t, '__name__', repr(t))


def is_allowed_types(value: Any, allowed_types: Optional[Sequence[Any]], required: Optional[bool] = None) -> bool:
    """
    Check whether the type of value is in the allowed types.

    :param value: the value to check the type of
    :param allowed_types: a list of allowed types, to be checked with :func:`isinstance`.
        If *None*, no type check is made.
    :return: whether the type is allowed
    """
    if value is None and required is not None:
        return not required
    if allowed_types is None:
        return True
    tfound = False
    for t in allowed_types:
        if t is None:
            if value is None:
                tfound = True
                break
        elif isinstance(value, t):
            tfound = True
            break
    return tfound
