# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte

from yaml import full_load
from ujson import loads
from six import b


def read_file(file_name):
    """Load dict from a json or yaml formatted file.

    :param file_cname: file name
    :return: data
    """
    f = open(file_name, 'r')
    data = f.read()
    extension = file_name[-4:].lower()
    if extension == b('json') or extension == 'json':
        data = loads(data)
    elif extension == b('yaml') or extension == 'yaml':
        data = full_load(data)
    elif extension == b('.yml') or extension == '.yml':
        data = full_load(data)
    f.close()
    return data