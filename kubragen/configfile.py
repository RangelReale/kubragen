from typing import Any, Tuple, Sequence

from kubragen.exception import NotSupportedError
from kubragen.options import OptionGetter


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
