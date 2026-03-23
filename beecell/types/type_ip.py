# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2026 CSI-Piemonte

from ipaddress import IPv4Address, IPv4Network, AddressValueError, NetmaskValueError, ip_network, ip_address
from logging import getLogger
from typing import Optional

logger = getLogger(__name__)

def ip_is_internet(ip: str) -> bool:
    """
    True iff ip is pablice
    """
    try:
        address = ip_address(ip)
        return address.is_global
    except ValueError:
        return False
        # raise ValueError(f"not valid: {ip}")
    
def subnet_is_internet(cidr:str)->bool:
    """
    True if  cidr is a internet subnet,
    """
    try:
        network = ip_network(cidr, strict=False)
        return network.is_global
    except ValueError:
        return False
        # raise ValueError(f"not valid: {cidr}")
    
def ip2cidr(ip_address):
    """

    :param ip_address:
    :return:
    """
    res = ip_address.split("/")
    if len(res) == 1:
        return f"{res[0]}/32"
    return ip_address

def try_cast_to_ip(input_str: str, raise_exc=True) -> Optional[IPv4Address]:
    """try getting ip address from string

    :param input_str: input representing ip address
    :type input_str: str
    :param raise_exc: if True raise on error, defaults to True
    :type raise_exc: bool, optional
    :raises AddressValueError: on invalid value
    :return: valid ip address or None/AddressValueError depending on raise_exc
    :rtype: Optional[IPv4Address]
    """
    try:
        res = IPv4Address(input_str)
    except AddressValueError as ex:
        logger.error("Invalid ip address %s: %s", input_str, ex)
        if raise_exc:
            raise AddressValueError(f"Invalid ip address {input_str}: {ex}") from ex
        res = None
    return res

def try_cast_to_network(input_str: str, raise_exc=True) -> Optional[IPv4Network]:
    """try getting ip network from string

    :param input_str: input representing cidr
    :type input_str: str
    :param raise_exc: if True raise on error, defaults to True
    :type raise_exc: bool, optional
    :raises Exception: on invalid value
    :return: valid ip network or None/Exception depending on raise_exc
    :rtype: Optional[IPv4Network]
    """
    try:
        network = IPv4Network(input_str)
    except (AddressValueError, NetmaskValueError) as ex:
        logger.error("Invalid ip network %s: %s", input_str, ex)
        if raise_exc:
            raise type(ex)(f"Invalid ip network {input_str}: {ex}") from ex
        network = None
    return network
