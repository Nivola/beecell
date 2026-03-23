#!/usr/bin/env python
# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2026 CSI-Piemonte


import numbers
import logging
from typing import List, Optional, TYPE_CHECKING, Union
import uuid
from beecell.util import ensure_str
if TYPE_CHECKING:
    from bonsai import LDAPEntry

logger = logging.getLogger()


def sid_to_str(sid_bytes: Union[bytes, bytearray]):
    """converts bytes representing sid to string

    :param sid_bytes: bytes representing sid
    :type sid_bytes: Union[bytes, bytearray]
    :return: str representation of sid, or None
    :rtype: Optional[str]
    """
    if not isinstance(sid_bytes, (bytes, bytearray)):
        return None
    try:
        revision = sid_bytes[0]
        sub_authority_count = sid_bytes[1]
        identifier_authority = int.from_bytes(sid_bytes[2:8], "big")
        offset = 8
        sub_authorities = []
        for _ in range(sub_authority_count):
            sa = int.from_bytes(sid_bytes[offset:offset+4], "little")
            sub_authorities.append(sa)
            offset += 4
        return f"S-{revision}-{identifier_authority}-" + "-".join(map(str, sub_authorities))
    except Exception as ex:
        logging.error("Error while converting sid to str: %s", ex)
        return None

def decode_guid(value: Union[bytes, bytearray]):
    """converts bytes representing guid to string

    :param value: bytes representing guid
    :type value: Union[bytes, bytearray]
    :return: str representation of guid, or None
    :rtype: Optional[str]
    """
    if isinstance(value, (bytes, bytearray)) and len(value) == 16:
        try:
            return str(uuid.UUID(bytes_le=value))
        except Exception as ex:
            logging.error("Error while converting guid to str: %s", ex)
            return None
    return None

def sanitize_ldap_value(value, flatten_one_element_lists=True):
    if value is None:
        return None

    # bytes (maybe GUID or SID or binary data)
    if isinstance(value, (bytes, bytearray)):
        # GUID?
        guid = decode_guid(value)
        if guid:
            return guid

        # SID?
        sid = sid_to_str(value)
        if sid:
            return sid

        # Otherwise return hex dump so it is printable
        return value.hex()

    # --- list of values ---
    if isinstance(value, list):
        if flatten_one_element_lists and len(value)==1:
            return sanitize_ldap_value(value[0])
        else:
            return [sanitize_ldap_value(v) for v in value]

    # --- dict or LDAPEntry-like ---
    if isinstance(value, dict):
        return {k: sanitize_ldap_value(v) for k, v in value.items()}

    # --- strings, ints, etc. ---
    if isinstance(value, numbers.Number):
        return value

    # bonsai class instance e.g. bonsai.LDAPDN
    if value.__class__.__module__.startswith("bonsai."):
        value = str(value)
    return ensure_str(value)

def ldap_entry_to_dict(entry: 'LDAPEntry', fields: Optional[List[str]]=None):
    """
    Convert Bonsai LDAPEntry to a safe, printable dict.
    - fields = None -> convert all fields
    - fields = List[str] -> convert only wanted fields and discard the rest
    """
    if fields is not None and isinstance(fields, list):
        # only selected fields
        return {str(k): sanitize_ldap_value(v) for k, v in entry.items() if k in fields}
    else:
        # all fields
        return {str(k): sanitize_ldap_value(v) for k, v in entry.items()}
