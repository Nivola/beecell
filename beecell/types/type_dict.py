# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

def merge_dicts(*dict_args):
    """Given any number of dicts, shallow copy and merge into a new dict, precedence goes to key value pairs in latter
    dicts.

    :param *dict_args arbitrary number of dictionaries (1 to N)
    :return dict union of the N dict arguments
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def dict_get(data, key, separator='.', default=None):
    """Get a value from a dict. Key can be composed to get a field in a complex dict that contains other dict, list and
    string.

    :param data: dictionary to query
    :param key: key to search
    :param separator: key depth separator
    :param default: default value [default=None]
    :return:
    """
    keys = key.split(separator)
    res = data
    for k in keys:
        if isinstance(res, list):
            try:
                res = res[int(k)]
            except:
                res = {}
        else:
            if res is not None:
                res = res.get(k, {})
    if res is None or res == {}:
        res = default

    return res


def dict_set(data, key, value, separator='.'):
    """Set a key in a dict. Key can be a composition of different keys separated by a separator.

    :param data: dictionary to query
    :param key: key to update
    :param value: key new value
    :param separator: key depth separator
    :return:
    """
    def __dict_set(data):
        k = keys.pop()
        if len(keys) == 0:
            data[k] = value
        else:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data[k] = __dict_set(data[k])
        return data

    keys = key.split(separator)
    keys.reverse()
    data = __dict_set(data)

    return data


def dict_unset(data, key, separator='.'):
    """Unset a key in a dict. Key can be a composition of different keys separated by a separator.

    :param data: dictionary to query
    :param key: key to remove
    :param separator: key depth separator
    :return:
    """
    def __dict_unset(data):
        k = keys.pop()
        if len(keys) == 0:
            if k in data:
                data.pop(k, None)
        else:
            if k in data:
                data[k] = __dict_unset(data[k])
        return data

    keys = key.split(separator)
    keys.reverse()
    data = __dict_unset(data)

    return data


def flatten_dict(data, delimiter=":", loopArray=True):
    """Flat dictionary conversion

    :param data: input data
    :param loopArray: If True execute loop unrolling array items in keys. False otherwise
    :param delimiter: delimiter char
    :return dictionary unrolled with compound keys
    """

    def items():
        for key, value in data.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value, delimiter=delimiter, loopArray=loopArray).items():
                    yield key + delimiter + subkey, subvalue
            elif isinstance(value, list):
                if loopArray:
                    x = 0
                    for itemArray in value:
                        if isinstance(itemArray, dict):
                            for subkey, subvalue in flatten_dict(itemArray, delimiter=delimiter,
                                                                 loopArray=loopArray).items():
                                yield key + delimiter + str(x) + delimiter + subkey, subvalue
                        else:
                            yield key + delimiter + str(x), itemArray
                        x += 1
                else:
                    res = []
                    for itemArray in value:
                        res.append(flatten_dict(itemArray, delimiter=delimiter, loopArray=loopArray))
                    yield key, res
            else:
                yield key, value

    return dict(items())
