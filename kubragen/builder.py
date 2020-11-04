from typing import TypeVar, Sequence, Any, Mapping, Dict

from .exception import KGException, InvalidNameError, NotFoundError
from .jsonpatch import FilterJSONPatches, FilterJSONPatches_Apply
from .kubragen import KubraGen
from .object import ObjectItem, Object
from .types import TBuild, TBuildItem

BuilderT = TypeVar('BuilderT', bound='Builder')


class Builder:
    """
    Base class for configuration builders.
    """
    kubragen: KubraGen
    _jsonpatches: FilterJSONPatches
    _objectnames: Dict[str, str]

    def __init__(self, kubragen: KubraGen):
        self.kubragen = kubragen
        self._jsonpatches = None
        self._objectnames = {}

    def option_get(self, name: str) -> Any:
        """
        Get an option value.

        :param name: the option name in dot format (config.service_port)
        :return: the option value
        :raises: :class:`kubragen.exception.OptionError`
        :raises: :class:`kubragen.exception.TypeError`
        """
        raise NotImplementedError()

    def jsonpatches(self, patches: FilterJSONPatches = None) -> BuilderT:
        self._jsonpatches = patches
        return self

    def object_name(self, obj) -> str:
        if obj not in self._objectnames:
            raise NotFoundError('Object name "{}" not found'.format(obj))
        return self._objectnames[obj]

    def object_names(self) -> Mapping[str, str]:
        return self._objectnames

    def object_names_update(self, names: Mapping[str, str]) -> BuilderT:
        self._objectnames.update(names)
        return self

    def object_names_change(self, names: Mapping[str, str]) -> BuilderT:
        for name, value in names.items():
            if name not in self._objectnames:
                raise InvalidNameError('Unknown object name "{}"'.format(name))
            self._objectnames[name] = value
        return self

    def internal_build(self, buildname: TBuild) -> Sequence[ObjectItem]:
        raise NotImplementedError()

    def build_names(self) -> Sequence[TBuild]:
        return []

    def build_names_required(self) -> Sequence[TBuild]:
        return []

    def builditem_names(self) -> Sequence[TBuildItem]:
        return []

    def ensure_build_names(self, *buildnames: TBuild):
        return set(self.build_names_required()).issubset(set(buildnames))

    def build(self, *buildnames: TBuild) -> Sequence[ObjectItem]:
        ret = []
        for b in buildnames:
            if b not in self.build_names():
                raise KGException('Unknown build name: "{}"'.format(b))
            ret.extend(self.internal_build(b))
        return FilterJSONPatches_Apply(items=ret, jsonpatches=self._jsonpatches)

    def build_all(self) -> Sequence[ObjectItem]:
        return self.build(*self.build_names())

    def _check_object_must_have(self, items: Sequence[ObjectItem], names: Sequence[TBuildItem], source: str):
        for must_have in names:
            if next((i for i in items if isinstance(i, Object) and i.name == must_have), None) is None:
                raise InvalidNameError('Missing item "{}" in "{}"'.format(must_have, source))
