# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2022 CSI-Piemonte

from six import b, ensure_text, ensure_binary
from logging import getLogger
from cryptography.fernet import Fernet

logger = getLogger(__name__)


def check_vault(data, key):
    """Check if data is encrypted with fernet token and AES128

    :param data: data to verify. If encrypted token '$BEEHIVE_VAULT;AES128 | ' is in head of data
    :param key: fernet key
    :return: decrypted key
    """
    data = ensure_binary(data)
    if data.find(b('$BEEHIVE_VAULT;AES128 | ')) == 0:
        if key is None:
            raise Exception('Fernet key must be provided')
        cipher_suite = Fernet(ensure_binary(key))
        data = data.replace(b('$BEEHIVE_VAULT;AES128 | '), b(''))
        data = cipher_suite.decrypt(data)
    data = data.decode('utf-8')
    return data


def is_encrypted(data):
    """Check if data is encrypted with fernet token and AES128

    :param data: data to verify. If encrypted token '$BEEHIVE_VAULT;AES128 | ' is in head of data
    :return: True if data is encrypted, False otherwise
    """
    if data.find('$BEEHIVE_VAULT;AES128 | ') == 0:
        return True
    return False


def generate_fernet_key():
    """Generate fernet key

    :return: fernet key
    """
    return Fernet.generate_key()


def encrypt_data(fernet_key, data):
    """Encrypt data using a fernet key and a symmetric algorithm

    :param fernet_key: fernet key. To generate use: Fernet.generate_key()
    :param data: data to encrypt
    :return: encrypted data
    """
    cipher_suite = Fernet(ensure_binary(fernet_key))
    cipher_data = ensure_text(cipher_suite.encrypt(ensure_binary(data)))
    return '$BEEHIVE_VAULT;AES128 | %s' % cipher_data


def decrypt_data(fernet_key, data):
    """Decrypt data using a fernet key and a symmetric algorithm

    :param fernet_key: fernet key
    :param data: data to decrypt
    :return: decrypted data
    """
    data = ensure_text(data)
    if data.find('$BEEHIVE_VAULT;AES128 | ') == 0:
        data = data.replace('$BEEHIVE_VAULT;AES128 | ', '')
        cipher_suite = Fernet(ensure_binary(fernet_key))
        cipher_data = cipher_suite.decrypt(ensure_binary(data))
    else:
        cipher_data = data
    return cipher_data
