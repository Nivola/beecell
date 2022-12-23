# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

from inspect import isclass
from re import compile as re_compile


def str2bool(value: str):
    """Convert value from string to bool

    :param value: value to convert
    :return: converted value
    """

    res = None
    if value in ['False', 'false', 0, 'no', False]:
        res = False
    elif value in ['True', 'true', 1, 'yes', 'si', True]:
        res = True
    return res


def bool2str(value):
    """Convert value from bool to string

    :param value: value to convert
    :return: converted value
    """

    res = None
    if value in [False, 0, 'no']:
        res = 'false'
    elif value in [True, 1, 'yes', 'si']:
        res = 'true'
    return res


def truncate(msg:str, size:int=600, replace_new_line:bool=True)->str:
    """Truncate message to fixed size.

    :param str msg: message to truncate
    :param size: max message length [default=400]
    :return: truncated Message with ...
    """
    msg = str(msg)
    if replace_new_line is True:
        msg = msg.replace('\n', ' + ')

    if len(msg) > size:
        return msg[0:size] + '...'
    else:
        return msg


def validate_string(data, validation_string=r'[^a-zA-Z0-9\-].'):
    """Validate a string respect a set of allowed characters

    :param data: data to validate
    :param validation_string: validation string [deafult=r'[^a-zA-Z0-9\-].']
    :return: True if validation is OK
    """
    char_re = re_compile(validation_string)
    data = char_re.search(data)
    return not bool(data)


def split_string_in_chunks(string, pos=100):
    """split a string in chunks

    :param string: string to split
    :param pos: position where split
    :return: list of string chunks
    """
    chunks = [string[i:i + pos] for i in range(0, len(string), pos)]
    return chunks


def compat(data):
    try:
        if isinstance(data, list):
            data = '[..]'
        elif isinstance(data, dict):
            newdata = {}
            for k, v in data.items():
                newdata[k] = compat(v)
            data = newdata
        elif isclass(data) is True:
            data = str(data)
        else:
            data = truncate(data, 30)
    except:
        data = None
    return data


def is_blank(myString):
    """Test if string is blank

    :param myString: string to test
    :return: True if blank, False otherwhise
    """

    return not (myString and myString.strip())


def is_not_blank(myString):
    """Test if string is not blank

    :param myString: string to test
    :return: True if not blank, False otherwhise
    """

    return bool(myString and myString.strip())


def get_pretty_size(data):
    """Convert size in pritty string"""
    KB = 1024
    MB = KB * 1024
    GB = MB * 1024
    TB = GB * 1024

    if KB < data < MB:
        data = '%sKB' % round(data / KB, 2)
    elif MB <= data < GB:
        data = '%sMB' % round(data / MB, 2)
    elif GB <= data < TB:
        data = '%sGB' % round(data / GB, 2)
    elif data >= TB:
        data = '%sTB' % round(data / TB, 2)
    return data
