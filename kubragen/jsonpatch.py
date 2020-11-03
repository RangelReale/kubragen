from typing import Any, Optional, Union, Sequence, Dict, Mapping, Callable

from jsonpatch import InvalidJsonPatch

from .exception import InvalidJsonPatchError, InvalidParamError
from .object import ObjectItem, Object
from .private.jsonpatch import KGJsonPatchExt


ObjectFilterCallable = Callable[[Any], bool]


class ObjectFilterBase:
    """
    Base class for object filters
    """
    def is_include(self, object: ObjectItem) -> bool:
        """
        Checks if the object should be included on the filter.

        :param object: object to check
        :return: whether the object should be included
        """
        return False


class ObjectFilter(ObjectFilterBase):
    """
    Object filter that filter by a list of object properties.

    To be accepted **ALL** conditions should be TRUE.

    :param names: List of names to include
    :param sources: List of sources to include
    :param instances: List of instances to include
    :param callables: List of callables to call and check for inclusion. **At least one** must return True
        to accept the object.
    """
    names: Optional[Sequence[str]]
    sources: Optional[Sequence[str]]
    instances: Optional[Sequence[str]]
    callables: Optional[Sequence[ObjectFilterCallable]]

    def __init__(self, names: Optional[Union[Sequence[str], str]] = None, sources: Optional[Union[Sequence[str], str]] = None,
                 instances: Optional[Union[Sequence[str], str]] = None,
                 callables: Optional[Union[Sequence[ObjectFilterCallable], ObjectFilterCallable]] = None):
        if isinstance(names, str):
            self.names = [names]
        else:
            self.names = names
        if isinstance(sources, str):
            self.sources = [sources]
        else:
            self.sources = sources
        if isinstance(instances, str):
            self.instances = [instances]
        else:
            self.instances = instances
        if callables is not None and not isinstance(callables, Sequence):
            self.callables = [callables]
        else:
            self.callables = callables

    def is_include(self, object: ObjectItem):
        if not isinstance(object, Object) and (self.names is not None or self.sources is not None or
                                               self.instances is not None):
            # If is not an object but have object filters, it is impossible to check
            return False

        if isinstance(object, Object):
            if self.names is not None and object.name not in self.names:
                return False
            if self.sources is not None and object.source not in self.sources:
                return False
            if self.instances is not None and object.instance not in self.instances:
                return False

        if self.callables is not None:
            for c in self.callables:
                if c(object):
                    return True
            return False

        return True


def ObjectFilterFromDict(d: Mapping) -> ObjectFilter:
    """
    Build an object filter from a dict.

    :param d: source dict
    :return: an :class:`ObjectFilter`
    """
    if not any(name in d for name in ['names', 'sources', 'instances', 'callables']):
        raise InvalidParamError("Object filter dict must have at least one of 'names', 'sources', 'instances', 'callables'")
    return ObjectFilter(names=d['names'] if 'names' in d else None,
                        sources=d['sources'] if 'sources' in d else None,
                        instances=d['instances'] if 'instances' in d else None,
                        callables=d['callables'] if 'callables' in d else None)


def ObjectFilterCheck(object: ObjectItem, filters: Optional[Sequence[Any]]) -> bool:
    """
    Checks if the object should be included, using the list of filters.

    :param object: :class:`kubragen.object.ObjectItem` to check
    :param filters: list of filters to check
    :return: whether at least one of the filters accepts the object
    """
    if filters is None:
        return True
    for filter in filters:
        if isinstance(filter, ObjectFilterBase):
            if filter.is_include(object):
                return True
        elif isinstance(filter, Mapping):
            if ObjectFilterFromDict(filter).is_include(object):
                return True
        elif callable(filter):
            if filter(object):
                return True
        else:
            raise InvalidParamError('Unknown object filter type')
    return False


ObjectFilterType = Union[
    ObjectFilterBase,
    Dict[str, Union[Sequence[str], str]],
    Callable[[Any], bool]
]
"""
The types of the filters accepted.
"""


class FilterJSONPatch:
    """
    Represets a set of patches in a list of objects filtered by name.

    :param patches: list of json patches defined by the :py:mod:`jsonpatchext` module
    :param filters:
        List of filters to check if the object should be patched. The be accepted **at least one** of filters
        should accept the object.

         Each filter can be:

        * An instance of :class:`ObjectFilter`
        * A :class:`dict` with at least of field of ``['names', 'sources', 'instances', 'callables']``
        * A callable that receives an :class:`kubragen.object.ObjectItem` as parameter and returns a bool whether the
          object should be included
    """
    patches: Sequence[Any]
    filters: Optional[Sequence[ObjectFilterType]]

    def __init__(self, patches: Sequence[Any], filters: Optional[Union[Sequence[ObjectFilterType], ObjectFilterType]]):
        self.patches = patches
        if filters is not None and not isinstance(filters, Sequence):
            self.filters = [filters]
        else:
            self.filters = filters


FilterJSONPatches = Optional[Sequence[FilterJSONPatch]]


def JSONPatches_Apply(items: Union[Any, Sequence[Any]], jsonpatches: Sequence[Any] = None) -> Any:
    """
    Apply the patches to a list of items.

    This is a DESTRUCTIVE method, the passed objects will be mutated in place.

    :param items: list of values, or a single value.
    :param jsonpatches: list of json patches defined by the :py:mod:`jsonpatchext` module
    :return: same as *items* after patching
    :raises: :class:`kubragen.exception.InvalidJsonPatchError`
    """
    try:
        if isinstance(items, Sequence):
            for item in items:
                KGJsonPatchExt(jsonpatches).apply(item, in_place=True)
        else:
            KGJsonPatchExt(jsonpatches).apply(items, in_place=True)
    except InvalidJsonPatch as e:
        raise InvalidJsonPatchError(str(e)) from e
    return items


def FilterJSONPatches_Apply(items: Sequence[ObjectItem], jsonpatches: FilterJSONPatches = None) -> Sequence[ObjectItem]:
    """
    Apply the patches to a list of :data:`kubragen.object.ObjectItem`.

    This is a DESTRUCTIVE method, the passed objects will be mutated in place.

    :param items: list of :data:`kubragen.object.ObjectItem`.
    :param jsonpatches: list of json patches defined by the :py:mod:`jsonpatchext` module
    :return: same as *items* after patching
    :raises: :class:`kubragen.exception.InvalidJsonPatchError`
    """
    if jsonpatches is not None:
        try:
            for item in items:
                for jp in jsonpatches:
                    if ObjectFilterCheck(item, jp.filters):
                        KGJsonPatchExt(jp.patches).apply(item, in_place=True)
        except InvalidJsonPatch as e:
            raise InvalidJsonPatchError(str(e)) from e
    return items
