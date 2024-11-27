# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

import os
import xml.etree.ElementTree as et
# from xmltodict import parse as xmltodict
from yaml import full_load
from ujson import loads
from base64 import urlsafe_b64decode
from six import b, ensure_binary
from beecell.crypto_util.fernet import Fernet
from beecell.crypto import VAULT_MARK


def check_encrypted(data, fernet: Fernet):
    """
    Iterate through data dictionary to look for values encrypted by fernet token and AES128, and decrypt them.

    :param data: the dictionary to browse. Encrypted values start with '$BEEHIVE_VAULT;AES128 | '
    :param fernet: fernet key
    :return: the dictionary with decrypted values
    """
    for key, value in data.items():
        if isinstance(value, dict):
            check_encrypted(value, fernet)
        elif isinstance(value, str) and value.startswith(VAULT_MARK):
            value = ensure_binary(value)
            value = value.replace(b(VAULT_MARK), b(""))
            value = fernet.decrypt(value)
            data[key] = value.decode("utf-8")
    return data

# def read_file(file_name, parse=True):
def read_file(file_name: str, parse=True, secret: str = None) -> dict:
    """Load dict from a json or yaml formatted file.

    :param file_name: file name
    :param parse: if True parse file
    :param secret: encryption/decryption key
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

    if secret is not None:
        fernet = Fernet(urlsafe_b64decode(secret))
        data = check_encrypted(data, fernet)

    return data
