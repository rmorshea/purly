import collections


def diff(into, data):
    return merged_difference(into, data, {})[1]


def merge(into, data):
    return merged_difference(into, data, {})[0]


def merged_difference(into, data, diff):
    for k in data:
        v = data[k]
        if isinstance(v, collections.Mapping):
            merged_difference(
                into.setdefault(k, {}),
                v,
                diff.setdefault(k, {}),
            )
        elif k in into:
            if v is None:
                diff[k] = None
                del into[k]
            elif into[k] != v:
                diff[k] = into[k] = v
        elif v is not None:
            diff[k] = into[k] = v
    return into, diff


def diritems(x):
    for k in dir(x):
        try:
            v = getattr(x, k)
        except AttributeError:
            pass
        else:
            yield k, v
