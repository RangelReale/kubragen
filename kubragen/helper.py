from .exception import KGException, InvalidParamError


class HelperStr(str):
    """
    Base class for string generator helper
    """
    pass


class QuotedStr(HelperStr):
    """
    Class to indicate that the value should be quoted using the default quote type.
    """
    pass


class SingleQuotedStr(HelperStr):
    """
    Class to indicate that the value should be quoted using single quotes.
    """
    pass


class DoubleQuotedStr(HelperStr):
    """
    Class to indicate that the value should be quoted using double quotes.
    """
    pass


class FoldedStr(HelperStr):
    """
    Class to indicate that the value should use the YAML folded string style.
    """
    pass


class LiteralStr(HelperStr):
    """
    Class to indicate that the value should use the YAML literal string style.
    """
    pass


def HelperStrNewInstance(base: HelperStr, value: str) -> HelperStr:
    """
    Returns a new :class:`HelperStr` instance of the same type as the base.

    :param base: Instance to check the type. Its content are not used
    :param value: String value of the returned instance

    :return: The value wrapped by the type of base
    :raises: :class:`kubragen.exception.InvalidParamError`
    """
    if isinstance(base, QuotedStr):
        return QuotedStr(value)
    elif isinstance(base, SingleQuotedStr):
        return SingleQuotedStr(value)
    elif isinstance(base, DoubleQuotedStr):
        return DoubleQuotedStr(value)
    elif isinstance(base, FoldedStr):
        return FoldedStr(value)
    elif isinstance(base, LiteralStr):
        return LiteralStr(value)
    else:
        raise InvalidParamError('Unknown helper instance: "{}"'.format(repr(base)))
