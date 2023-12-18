# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

from logging import getLogger
from string import ascii_uppercase, ascii_letters, digits, ascii_lowercase
from os import urandom
from random import SystemRandom

logger = getLogger(__name__)


def random_password(length=10, strong=False):
    """Generate random password
    inspired to: https://pynative.com/python-generate-random-string/

    :param length: length of string to generate
    :param strong: True for generate strong password (include upper/lowercase, digits and random_password character)
    :return: generated password in UNICODE format
    """
    chars = ascii_uppercase + digits + ascii_lowercase

    if strong is True:
        punctuation = "()_-."
        randomSource = ascii_letters + digits + punctuation
        password = SystemRandom().choice(ascii_lowercase)
        password += SystemRandom().choice(ascii_uppercase)
        password = SystemRandom().choice(ascii_lowercase)
        password += SystemRandom().choice(ascii_uppercase)
        password += SystemRandom().choice(digits)
        password += SystemRandom().choice(punctuation)
        password += SystemRandom().choice(punctuation)

        for i in range(length - 7):
            password += SystemRandom().choice(randomSource)

        passwordList = list(password)
        SystemRandom().shuffle(passwordList)
        password = "".join(passwordList)
    else:
        password = ""
        for i in range(length):
            password += chars[ord(urandom(1)) % len(chars)]

    return password


def obscure_data(data, fields=None):
    """Obscure some fields in data, fields can be password.

    :param data: data to check
    :param fields: list of fields to obfuscate. default=['password', 'pwd', 'passwd']
    :return: obscured data
    """
    if fields is None:
        fields = ["password", "pwd", "passwd", "pass"]

    if isinstance(data, str) or isinstance(data, bytes):
        return obscure_string(data, fields)

    for key, value in data.items():
        if isinstance(value, dict):
            obscure_data(value, fields)

        elif isinstance(value, str) or isinstance(value, bytes):
            for field in fields:
                # print("%s - %s" % (key, field))
                if key.lower().find(field) >= 0:
                    data[key] = "xxxxxx"

    return data


def obscure_string(data, fields=None):
    """Obscure entire string if it contains passwords.

    :param data: data to check
    :param fields: list of fields to obfuscate. default=['password', 'pwd', 'passwd']
    :return: obscured string
    """
    if fields is None:
        fields = ["password", "pwd", "passwd", "pass"]

    for field in fields:
        # logger.debug("+++++ obscure_string - %s - %s" % (type(data), type(field)))
        if type(data) is bytes:
            # logger.debug("+++++ obscure_string - data: %s" % (data))
            if data.lower().find(str.encode(field)) >= 0:
                data = "xxxxxx"

        else:
            if data.lower().find(field) >= 0:
                data = "xxxxxx"
    return data
