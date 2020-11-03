from typing import Any, Optional, Union

from .private.object import object_clean
from .types import TBuildItem


class Object(dict):
    """
    Represents a single Kubernetes object, like *Pod*, *StatefulSet*, *Deployment*, *Secret*, etc.
    This is simply a :class:`dict` with extra properties to allow it to be found and changed using a name.

    Before being added, the :class:`dict` is cleaned of any :class:`kubragen.data.Data` that is not enabled.

    :param data: the Kubernetes object data, normally as a :class:`dict`
    :param name: the internal name used to locate the object
    :param source: the source of the object, normally the :class:`kubragen.builder.Builder` name
    :param instance: a possibly unique instance name, normally a :class:`kubragen.builder.Builder` basename
    """
    name: Optional[str]
    source: Optional[str]
    instance: Optional[str]
    data: Any

    def __init__(self, data=None, name: Optional[str] = None, source: Optional[str] = None,
                 instance: Optional[str] = None):
        super().__init__()
        object_clean(data)
        self.update(data)
        self.name = name
        self.source = source
        self.instance = instance


ObjectItem = Union[Object, dict]
"""Object abstraction that allows :class:`Object` or a raw :class:`dict`"""
