from typing import Optional, Dict, Any

import yaml

from .data import Data
from .exception import KGException
from .helper import DoubleQuotedStr, SingleQuotedStr, FoldedStr, LiteralStr, QuotedStr
from .kubragen import KubraGen
from .object import Object
from .option import OptionDef
from .private.yaml import represent_single_quoted_str, represent_double_quoted_str, represent_folded_str, \
    represent_literal_str


def YamlDumper(kg: KubraGen):
    """
    Wrapper function to allow dumper to receive the kg param.

    :param kg: the :class:`kubragen.kubragen.KubraGen` instance
    :return: function that returns a dumper instance
    """
    def k(*args, **kwargs):
        return YamlDumperImpl(*args, kg=kg, **kwargs)
    return k


class YamlDumperBase(yaml.Dumper):
    """
    YAML dumper that takes KubraGen HelperStr classes in account.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # https://stackoverflow.com/questions/51272814/python-yaml-dumping-pointer-references
        self.ignore_aliases = lambda *args: True

        # String
        self.add_representer(SingleQuotedStr, represent_single_quoted_str)
        self.add_representer(DoubleQuotedStr, represent_double_quoted_str)
        self.add_representer(FoldedStr, represent_folded_str)
        self.add_representer(LiteralStr, represent_literal_str)

        # QuotedStr
        self._init_quotedstr()

    def _init_quotedstr(self):
        self.add_representer(QuotedStr, represent_single_quoted_str)


class YamlDumperImpl(YamlDumperBase):
    """
    YAML dumper that takes KubraGen classes in account.

    :param kg: the :class:`kubragen.kubragen.KubraGen` instance
    """
    kg: Optional[KubraGen]

    def __init__(self, *args, kg: Optional[KubraGen] = None, **kwargs):
        self.kg = kg
        super().__init__(*args, **kwargs)

        # KGObject
        def kgobject_representer(dumper: yaml.Dumper, data: Object):
            return dumper.represent_dict(data)
        self.add_representer(Object, kgobject_representer)

        # KGOptionDef
        def kgoptiondef_representer(dumper: yaml.Dumper, data: OptionDef):
            raise KGException('KGOptionDef cannot be output in yaml')
            # return dumper.represent(data.default_value)
        self.add_representer(OptionDef, kgoptiondef_representer)

        # KGData
        def kgdata_representer(dumper: yaml.Dumper, data: Data):
            if not data.is_enabled():
                return dumper.represent_none(None)
            return dumper.represent_data(data.get_value())
        self.add_multi_representer(Data, kgdata_representer)

    def represent_sequence(self, tag, sequence, flow_style=None):
        kgsequence = []
        for item in sequence:
            if isinstance(item, Data) and not item.is_enabled():
                continue
            kgsequence.append(item)
        return super().represent_sequence(tag, kgsequence, flow_style)

    def represent_mapping(self, tag, mapping, flow_style=None):
        kgmapping = {}
        if hasattr(mapping, 'items'):
            mapping = list(mapping.items())
        for item_key, item_value in mapping:
            if isinstance(item_value, Data) and not item_value.is_enabled():
                continue
            kgmapping[item_key] = item_value
        return super().represent_mapping(tag, kgmapping, flow_style=False)

    def _init_quotedstr(self):
        # QuotedStr
        def kgvaluequotedstr_representer(dumper: yaml.Dumper, data: QuotedStr):
            if self.kg is not None:
                if not self.kg.default_quoted_value_single():
                    return represent_double_quoted_str(dumper, data)
            return represent_single_quoted_str(dumper, data)
        self.add_representer(QuotedStr, kgvaluequotedstr_representer)


class YamlGenerator:
    """
    A YAML generator that takes in account KubraGen classes.

    :param kg: the :class:`kubragen.kubragen.KubraGen` instance
    """
    kg: KubraGen

    def __init__(self, kg: KubraGen):
        self.kg = kg

    def generate(self, data) -> str:
        """
        Generates an YAML document.

        :param data: source objects
        :return: YAML document text
        """
        yaml_dump_params: Dict[Any, Any] = {'default_flow_style': None, 'sort_keys': False}
        if isinstance(data, list):
            return yaml.dump_all(data, Dumper=YamlDumper(self.kg), **yaml_dump_params)
        return yaml.dump(data, Dumper=YamlDumper(self.kg), **yaml_dump_params)
