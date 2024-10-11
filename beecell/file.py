# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

import os
import xml.etree.ElementTree as et
from yaml import full_load
from six import b
from ujson import loads

# from xmltodict import parse as xmltodict


def read_file(file_name, parse=True):
    """Load dict from a json or yaml formatted file.

    :param file_name: file name
    :param parse: if True parse file
    :return: data
    """
    
    f = open(os.path.expanduser(file_name), "r")
    data = f.read()
    extension = file_name[-4:].lower()
    if parse is True:
        if extension == b("json") or extension == "json":
            data = loads(data)
        elif extension == b("yaml") or extension == "yaml":
            data = full_load(data)
        elif extension == b(".yml") or extension == ".yml":
            data = full_load(data)
        elif extension == b(".xml") or extension == ".xml":
            data = et.fromstring(data)
    f.close()
    return data
