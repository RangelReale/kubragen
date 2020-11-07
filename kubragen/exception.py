class KGException(Exception):
    pass


class InvalidOperationError(KGException):
    pass


class InvalidParamError(KGException):
    pass


class NotFoundError(KGException):
    pass


class NotSupportedError(KGException):
    pass


class InvalidNameError(KGException):
    pass


class OptionError(KGException):
    pass


class TypeError(KGException):
    pass


class MergeError(KGException):
    pass


class InvalidJsonPatchError(KGException):
    pass


class ConfigFileError(KGException):
    pass
