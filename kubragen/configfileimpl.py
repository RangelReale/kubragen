from typing import Any, Mapping

from kubragen.options import OptionGetter
from kubragen.util import dict_flatten
from kubragen.configfile import ConfigFileOutput, ConfigFileRender, ConfigFile


#
# Output
#

class ConfigFileOutput_RawStr(ConfigFileOutput):
    """
    Wraps a raw string.
    """
    pass


class ConfigFileOutput_DictSingleLevel(ConfigFileOutput):
    """
    Wraps a dict with a single level (no nested dicts).
    """
    pass


class ConfigFileOutput_DictDualLevel(ConfigFileOutput):
    """
    Wraps a dict with two levels (only one level of nested dicts).
    """
    pass


class ConfigFileOutput_Dict(ConfigFileOutput):
    """
    Wraps a dict with any number of levels.
    """
    pass


#
# File
#

class ConfigFile_RawStr(ConfigFile):
    """
    A raw string config file.
    """
    value: Any

    def __init__(self, value: Any):
        self.value = value

    def get_value(self, options: OptionGetter) -> ConfigFileOutput:
        return ConfigFileOutput_RawStr(self.value)


#
# Render
#

class ConfigFileRender_RawStr(ConfigFileRender):
    """
    Renderer that outputs a raw str output.
    """
    def supports(self, value: ConfigFileOutput) -> bool:
        if isinstance(value, ConfigFileOutput_RawStr):
            return True
        return super().supports(value)

    def render(self, value: ConfigFileOutput) -> str:
        if isinstance(value, ConfigFileOutput_RawStr):
            return str(value.value)
        super().render(value)


class ConfigFileRender_SysCtl(ConfigFileRender):
    """
    Renderer that outputs a SysCtl file output.

    SysCtl is ini-like without sections.
    """
    separator: str

    def __init__(self, separator: str = '.'):
        self.separator = separator

    def render_dict(self, value: Mapping) -> str:
        ret = []
        for dname, dvalue in dict_flatten(value, sep=self.separator).items():
            ret.append('{} = {}'.format(dname, str(dvalue)))
        return '\n'.join(ret)

    def supports(self, value: ConfigFileOutput) -> bool:
        if isinstance(value, ConfigFileOutput_DictSingleLevel) or \
           isinstance(value, ConfigFileOutput_DictDualLevel) or \
           isinstance(value, ConfigFileOutput_Dict):
            return True
        return super().supports(value)

    def render(self, value: ConfigFileOutput) -> str:
        if self.supports(value):
            return self.render_dict(value.value)
        super().render(value)
