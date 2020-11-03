class KGException(Exception):
    pass


class InvalidParamError(KGException):
    pass


class NotFoundError(KGException):
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
