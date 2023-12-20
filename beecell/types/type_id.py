# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

from binascii import hexlify
from os import urandom
from string import ascii_letters, digits
from uuid import uuid4
from random import choice
from re import match
from logging import getLogger
from six import ensure_text

logger = getLogger(__name__)


def id_gen(length=10, parent_id=None):
    """Generate unique uuid according to RFC 4122

    :param length: length of id to generate
    :param parent_id: root to append in the id
    :return: oid generated
    """
    oid = hexlify(urandom(int(length / 2)))
    if parent_id is not None:
        oid = "%s//%s" % (parent_id, ensure_text(oid))
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
    random.seed = urandom(1024)
    return "".join(choice(chars) for i in range(length))


def is_name(oid):
    """Check if oid is uuid, id or literal name.

    :param oid:
    :return: True if it is a literal name
    """
    # get obj by uuid
    if match("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", str(oid)):
        logger.debug("Param %s is an uuid" % oid)
        return False
    # get obj by id
    elif match("^\d+$", str(oid)):
        logger.debug("Param %s is an id" % oid)
        return False
    # get obj by name
    elif match("[\-\w\d]+", oid):
        logger.debug("Param %s is a name" % oid)
        return True


def is_uuid(oid):
    """Check if oid is a uuid

    :param oid:
    :return: True if oid is a uuid
    """
    if match("[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", str(oid)) is not None:
        return True
    return False
