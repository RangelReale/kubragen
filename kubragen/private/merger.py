import deepmerge
from deepmerge.exception import InvalidMerge

from ..exception import OptionError, MergeError


def option_check_key_exist(config, path, base, nxt):
    for k, v in nxt.items():
        if k not in base:
            raise OptionError('Unknown option: "{}"'.format('.'.join(path + [k])))
    return deepmerge.STRATEGY_END


def option_type_conflict(config, path, base, nxt):
    if len(path) > 0:
        raise MergeError("Type conflict at '{}': {}, {}".format(
            '.'.join(path), type(base), type(nxt)
        ))
    raise MergeError("Type conflict: {}, {}".format(
        type(base), type(nxt)
    ))


def option_merge_fallback(config, path, base, nxt):
    if len(path) > 0:
        raise MergeError("Merge fallback at '{}': {}, {}".format(
            '.'.join(path), type(base), type(nxt)
        ))
    raise MergeError("Merge fallback: {}, {}".format(
        type(base), type(nxt)
    ))
