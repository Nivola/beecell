# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2026 CSI-Piemonte

import os
from logging import getLogger
from typing import Dict, Optional
import xml.etree.ElementTree as et

# from xmltodict import parse as xmltodict
from yaml import full_load
from ujson import loads # pylint: disable=no-name-in-module
from base64 import urlsafe_b64decode
from .util import b, ensure_binary
from beecell.crypto_util.fernet import Fernet
from beecell.crypto import VAULT_MARK

logger = getLogger(__name__)

def check_encrypted(data: Dict, fernet: 'Fernet') -> Dict:
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


def read_file(file_name: str, parse=True, secret: Optional[str] = None) -> Dict:
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


def read_file_v2(filepath: str, secret: str = None, default_extension=".yaml") -> Dict:
    """Load dict from a json or yaml or xml formatted file.

    :param filepath: file path
    :type filepath: str
    :param secret: encryption/decryption key, defaults to None
    :type secret: str, optional
    :param default_extension: fallback extension to use if missing or invalid, defaults to ".yaml"
    :type default_extension: str, optional
    :raises Exception: on invalid extension, file not found
    :return: parsed data
    :rtype: Dict
    """
    filename, extension = os.path.splitext(filepath)
    if not extension or extension not in [".json",".yaml",".yml",".xml"]:
        filepath = filepath + default_extension
        extension = default_extension

    logger.debug("About to read file: %s - extension: %s", filepath, extension)
    stream = open(os.path.expanduser(filepath), "r")
    data = stream.read()

    if extension == ".json":
        data = loads(data)
    elif extension == ".yaml" or extension == ".yml":
        data = full_load(data)
    elif extension == ".xml":
        data = et.fromstring(data)
    else:
        logger.error("Unsupported extension %s - file: %s", extension, filename)
        raise Exception("Unsupported extension %s - file: %s" % (extension, filename))

    stream.close()

    if secret:
        fernet = Fernet(urlsafe_b64decode(secret))
        # decrypt data
        data = check_encrypted(data, fernet)

    return data
