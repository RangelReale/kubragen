from typing import MutableMapping, MutableSequence

from ..data import Data


def object_clean_prop(object, key):
    """Cleanup instances of Data class"""
    if isinstance(object[key], Data):
        if not object[key].is_enabled():
            del object[key]
        else:
            object[key] = object[key].get_value()


def object_clean(object):
    """Cleanup all instances of Data classes, removing if not enabled or replacing by its value"""
    if isinstance(object, MutableMapping):
        keylist = list(object.keys())
        for key in keylist:
            object_clean_prop(object, key)
        for item in object.values():
            object_clean(item)
    elif isinstance(object, MutableSequence):
        for key in range(len(object)-1, -1, -1):
            object_clean_prop(object, key)
        for item in object:
            object_clean(item)
    else:
        pass
