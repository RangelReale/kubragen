from typing import TypeVar, Sequence, Any, Mapping, Dict, List

from .exception import KGException, InvalidNameError, NotFoundError, InvalidOperationError
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

    def jsonpatches(self: BuilderT, patches: FilterJSONPatches = None) -> BuilderT:
        """
        Add a list of json patches to apply when building.

        :param patches: list of json patches
        :return: self
        """
        self._jsonpatches = patches
        return self

    def object_name(self, name: str) -> str:
        """
        Gets the name of an object.

        :param name: name to search for
        :return: the object name
        :raises: :class:`kubragen.exception.NotFoundError`
        """
        if name not in self._objectnames:
            raise NotFoundError('Object name "{}" not found'.format(name))
        return self._objectnames[name]

    def object_names(self) -> Mapping[str, str]:
        """
        Return a list of all objects with their names.

        :return: list of all objects with their names
        """
        return self._objectnames

    def object_names_init(self: BuilderT, names: Mapping[str, str]) -> BuilderT:
        """
        Initialize object names.
        Should **only** be used at initialization time, in the constructor.

        :param names: Mapping with object names
        :return: self
        """
        self._objectnames.update(names)
        return self

    def object_names_change(self: BuilderT, names: Mapping[str, str]) -> BuilderT:
        """
        Change object names.
        Should **only** be used by end-users of the builder.
        This checks if the name exists, and throws an exception if it doesn't.

        :param names: Mapping with object names
        :return: self
        :raise: :class:`kubragen.exception.InvalidNameError`
        """
        for name, value in names.items():
            if name not in self._objectnames:
                raise InvalidNameError('Unknown object name "{}"'.format(name))
            self._objectnames[name] = value
        return self

    def internal_build(self, buildname: TBuild) -> Sequence[ObjectItem]:
        """
        Builders should override this function to effectively build the results.

        :param buildname: name of the build
        :return: list of :class:`kubragen.object.ObjectItem`
        """
        raise NotImplementedError()

    def build_names(self) -> Sequence[TBuild]:
        """
        Returns a list of supported build names.

        :return: list of supported build names
        """
        return []

    def build_names_required(self) -> Sequence[TBuild]:
        """
        Returns a list of required build names, depending on the current options.

        :return: list of required build names
        """
        return []

    def builditem_names(self) -> Sequence[TBuildItem]:
        """
        Returns a list of supported build item names.

        :return: list of supported build item names
        """
        return []

    def ensure_build_names(self, *buildnames: TBuild) -> None:
        """
        Ensures that all required build names will be build.
        End-users should call this to ensure their output will not miss any important configuration.

        :param buildnames: list of build names
        :raises: :class:`kubragen.exception.InvalidOperationError`
        """
        if not set(self.build_names_required()).issubset(set(buildnames)):
            raise InvalidOperationError('Missing required build names')

    def build(self, *buildnames: TBuild) -> Sequence[ObjectItem]:
        """
        Call the internal builders to effectively build the result.

        :param buildnames: list of build names
        :return: list of :class:`kubragen.object.ObjectItem`
        """
        ret: List[ObjectItem] = []
        for b in buildnames:
            if b not in self.build_names():
                raise KGException('Unknown build name: "{}"'.format(b))
            ret.extend(self.internal_build(b))
        return FilterJSONPatches_Apply(items=ret, jsonpatches=self._jsonpatches)

    def build_all(self) -> Sequence[ObjectItem]:
        """
        Helper method to build all supported builds.

        :return: list of :class:`kubragen.object.ObjectItem`
        """
        return self.build(*self.build_names())

    def _check_object_must_have(self, items: Sequence[ObjectItem], builditemnames: Sequence[TBuildItem], source: str) -> None:
        """
        Checks that all build items are contained in the items.

        :param items: list of :class:`kubragen.object.ObjectItem`
        :param builditemnames: list of build item names
        :param source: source to display in the error message
        :raises: :class:`kubragen.exception.InvalidNameError`
        """
        for must_have in builditemnames:
            if next((i for i in items if isinstance(i, Object) and i.name == must_have), None) is None:
                raise InvalidNameError('Missing item "{}" in "{}"'.format(must_have, source))
