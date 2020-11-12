import deepmerge # type: ignore
import jsonpatchext # type: ignore

from ..data import Data
from ..helper import HelperStr, HelperStrNewInstance


class JSONPatchMerger(deepmerge.Merger):
    def value_strategy(self, path, base, nxt):
        if isinstance(base, Data):
            # If merging with Data class, merge with its value
            newbase = None
            if base.is_enabled():
                newbase = base.get_value()
            else:
                if isinstance(base.get_value(), dict):
                    newbase = {}
                elif isinstance(base.get_value(), list):
                    newbase = []
            return super().value_strategy(path, newbase, nxt)
        elif isinstance(base, HelperStr) and isinstance(nxt, HelperStr):
            # if both are HelperStr, use the type of nxt
            return super().value_strategy(path, str(base), nxt)
        return super().value_strategy(path, base, nxt)


def jsonpatch_merge_fallback(config, path, base, nxt):
    if isinstance(base, str) and isinstance(nxt, str):
        if isinstance(base, HelperStr) and not isinstance(nxt, HelperStr):
            # Use the same HelperStr class of the base
            return HelperStrNewInstance(base, nxt)
        else:
            return nxt
    return deepmerge.STRATEGY_END


jsonpatch_merge = JSONPatchMerger(
    [
        (list, "append"),
        (dict, "merge"),
    ],
    [jsonpatch_merge_fallback, jsonpatchext.merge_fallback],
    [jsonpatchext.merge_type_conflict]
)


class KGMergeOperation(jsonpatchext.MergeOperation):
    def apply_merge(self, subobj, part, value):
        # Use our own merger instead of the default
        if part is not None:
            subobj[part] = jsonpatch_merge.merge(subobj[part], value)
        else:
            jsonpatch_merge.merge(subobj, value)


class KGJsonPatchExt(jsonpatchext.JsonPatchExt):
    def __init__(self, patch):
        # Must inherit jsonpatchext.JsonPatchExt to change the merge operation class
        super(KGJsonPatchExt, self).__init__(patch)
        self.operations.update({
            'merge': KGMergeOperation,
        })
