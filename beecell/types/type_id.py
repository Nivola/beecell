# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2026 CSI-Piemonte

from binascii import hexlify
from os import urandom
from string import ascii_letters, digits
from uuid import uuid4,UUID
from random import choice
from re import match
from logging import getLogger
from ..util import ensure_text
from typing import Union

logger = getLogger(__name__)


def id_gen(length=10, parent_id=None) -> str:
    """Generate unique uuid according to RFC 4122

    :param length: length of id to generate
    :param parent_id: root to append in the id
    :return: oid generated
    """
    oid = hexlify(urandom(int(length / 2)))
    if parent_id is not None:
        oid = "%s//%s" % (parent_id, ensure_text(oid))
    return ensure_text(oid)


def token_gen(args=None) -> str:
    """Generate a 128 bit token according to RFC 4122
    :return: token generated

    NB: it must take args=None as argument or it breaks
    when called by oauth2
    """
    return str(uuid4())


def transaction_id_generator(length=20) -> str:
    """Generate random string to use as transaction id

    :param length: length of id to generate
    return : random string
    """
    import random

    chars = ascii_letters + digits
    random.seed = urandom(1024)
    return "".join(choice(chars) for i in range(length))


def is_uuid(oid: Union[str, int]) -> bool:
    """Check if oid is a uuid

    :param oid:
    :return: True if oid is a uuid
    """
    try:
        UUID(str(oid))
    except ValueError:
        return False
    return True

def is_id(oid: Union[str, int]) -> bool:
    """check if oid represents an integer value
    (str or int)

    :param oid: id, uuid or name
    :type oid: Union[str, int]
    :return: True if oid represents an int value
    :rtype: bool
    """
    if oid is None:
        return False
    try:
        int(oid)
    except ValueError:
        return False
    return True

def is_name(oid)->bool:
    """Check if oid is uuid, id or literal name.

    :param oid:
    :return: True if it is a literal name
    """
    # get obj by uuid
    if is_uuid(oid):
        logger.debug("Param %s is an uuid" % oid)
        return False
    # get obj by id
    elif is_id(oid):
        logger.debug("Param %s is an id" % oid)
        return False
    # get obj by name
    elif match(r"[\-\w\d]+", oid):
        logger.debug("Param %s is a name" % oid)
        return True

def test_oid(oid: Union[str, int]) -> str:
    """Test oid in order to know if it is an id, uuid or name

    :param oid: oid to test
    :type oid: Union[str, int]
    :return: "id" | "uuid" | "name" | "unknown"
    :rtype: str
    """
    if is_id(oid):
        return "id"
    elif is_uuid(oid):
        return "uuid"
    elif is_valid_name(oid):
        return "name"
    else:
        return "unknown"

def is_valid_name(name) -> bool:
    """check if name is a valid cmp name

    :param name: a string
    :type name: str
    :return: True if it respects cmp naming constraints
    :rtype: bool
    """
    if not isinstance(name,str):
        return False

    if not name:
        # None or empty
        return False

    if name[0]=='-' or name[0]=='_':
        # first char can't be - or _
        return False

    # . is needed for service definitions
    return all(ch.isalnum() or ch=='-' or ch=='_' or ch=="." for ch in name)
