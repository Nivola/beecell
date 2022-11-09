# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2022 CSI-Piemonte

from binascii import hexlify
from os import urandom
from string import ascii_letters, digits
from uuid import uuid4
from random import choice
from six import ensure_text


def id_gen(length=10, parent_id=None):
    """Generate unique uuid according to RFC 4122

    :param length: length of id to generate
    :param parent_id: root to append in the id
    :return: oid generated
    """
    oid = hexlify(urandom(int(length / 2)))
    if parent_id is not None:
        oid = '%s//%s' % (parent_id, ensure_text(oid))
    return ensure_text(oid)


def token_gen(args=None):
    """Generate a 128 bit token according to RFC 4122
    :return: token generated
    """
    return str(uuid4())


def transaction_id_generator(length=20):
    """Generate random string to use as transaction id

    :param length: length of id to generate
    return : random string
    """
    import random
    chars = ascii_letters + digits
    random.seed = (urandom(1024))
    return ''.join(choice(chars) for i in range(length))