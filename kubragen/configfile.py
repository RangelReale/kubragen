from typing import Any, Sequence, Mapping, Optional

import yaml

from kubragen.exception import NotSupportedError
from kubragen.options import OptionGetter
from kubragen.util import dict_flatten
from kubragen.yaml import YamlDumperBase


class ConfigFileOutput:
    """
    Config file output wrapper. Wraps a value with a type.
    """
    value: Any

    def __init__(self, value: Any):
        self.value = value


class ConfigFile:
    """
    Configuration file abstraction.
    """
    def get_value(self, options: OptionGetter) -> ConfigFileOutput:
        """
        Gets the configuration file contents.

        :param options: the target options, usually a :class:`kubragen.builder.Builder`
        :return: a :class:`ConfigFileOutput` with the config file contents
        """
        raise NotImplementedError()


class ConfigFileExtensionData:
    """
    Data class for config file extensions.

    This class is meant to avoid passing raw mutable data to the extensions.
    """
    data: Any

    def __init__(self, data: Any):
        self.data = data


class ConfigFileExtension:
    """
    An extension for a config file
    """
    def process(self, configfile: 'ConfigFile', data: ConfigFileExtensionData, options: OptionGetter) -> None:
        """
        Process a config file data, modifying it if necessary.

        :param configfile: the config file being extended
        :param data: the current config file data. Change the *data* property to make your extensions.
        :param options: the target options, usually a :class:`kubragen.builder.Builder`
        :raises: :class:`kubragen.exception.ConfigFileError`
        """
        pass


class ConfigFile_Extend(ConfigFile):
    """
    A :class:`ConfigFile` that allows extensions.

    :param extensions: the initial extensions
    """
    extensions: Sequence[ConfigFileExtension]

    def __init__(self, extensions: Optional[Sequence[ConfigFileExtension]] = None):
        super().__init__()
        if extensions is not None:
            self.extensions = extensions
        else:
            self.extensions = []

    def extension_add(self, *parts: ConfigFileExtension) -> None:
        """
        Add one or more config file extensions.

        :param parts: List of extensions to add
        """
        self.extensions.extend(parts)

    def init_value(self, options: OptionGetter) -> ConfigFileExtensionData:
        """
        Initialize data to send to extensions.

        :param options: the target options, usually a :class:`kubragen.builder.Builder`
        :return: the initial config data
        """
        raise NotImplementedError()

    def finish_value(self, options: OptionGetter, data: ConfigFileExtensionData) -> ConfigFileOutput:
        """
        Finish the value after the extensions processing.

        :param options: the target options, usually a :class:`kubragen.builder.Builder`
        :param data: the final data after extension processing
        :return: the data to be return by :func:`get_value`
        """
        raise NotImplementedError()

    def get_value(self, options: OptionGetter) -> ConfigFileOutput:
        """
        Process all extensions and return the config file data.
        """
        data = self.init_value(options)
        for extension in self.extensions:
            extension.process(self, data, options)
        return self.finish_value(options, data)


class ConfigFileRender:
    """
    A renderer for a config file
    """

    def supports(self, value: ConfigFileOutput) -> bool:
        """
        Checks whether this renderer supports the config file output.

        :param value: config file ouput
        :return: whether this renderer supports the output
        """
        return False

    def render(self, value: ConfigFileOutput) -> str:
        """
        Renders a configuration file.

        :param value: config file contents/output
        :return: config file contents rendered as a str
        :raises: `kubragen.exception.NotSupportedError`
        """
        raise NotSupportedError('Config file output not supported: "{}"'.format(repr(value)))


class ConfigFileRenderMulti(ConfigFileRender):
    """
    Config file renderer that tries multiple renderers in sequence
    """
    renderers: Sequence[ConfigFileRender]

    def __init__(self, renderers: Sequence[ConfigFileRender]):
        self.renderers = renderers

    def supports(self, value: ConfigFileOutput) -> bool:
        for r in self.renderers:
            if r.supports(value):
                return True
        return super().supports(value)

    def render(self, value: ConfigFileOutput) -> str:
        for r in self.renderers:
            if r.supports(value):
                return r.render(value)
        return super().render(value)


#
# IMPL
#

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
    Renderer that outputs a SysCtl file.

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


class ConfigFileRender_Yaml(ConfigFileRender):
    """
    Renderer that outputs a YAML file.
    """
    def render_yaml(self, value: Any) -> str:
        yaml_dump_params = {'default_flow_style': None, 'sort_keys': False}
        if isinstance(value, list):
            return yaml.dump_all(value, Dumper=YamlDumperBase, **yaml_dump_params)
        return yaml.dump(value, Dumper=YamlDumperBase, **yaml_dump_params)

    def supports(self, value: ConfigFileOutput) -> bool:
        if isinstance(value, ConfigFileOutput_DictSingleLevel) or \
           isinstance(value, ConfigFileOutput_DictDualLevel) or \
           isinstance(value, ConfigFileOutput_Dict):
            return True
        return super().supports(value)

    def render(self, value: ConfigFileOutput) -> str:
        if self.supports(value):
            return self.render_yaml(value.value)
        super().render(value)
