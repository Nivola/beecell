# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

from struct import pack
from logging import getLogger
from socket import inet_ntoa
from math import ceil

logger = getLogger(__name__)


def nround(number, decimal=4):
    """Round a given number

    Example: decimal = 2

        3.5643 -> '3.60'
        3.5343 -> '3.55'

    :param number: number to round
    :param decimal: number of decimal to keep
    :return: rounded number in UNICODE format
    """
    factor = 10 * decimal
    convert = "%." + b(decimal) + "f"
    return convert % (ceil(number * factor) / factor)


class AttribException(Exception):
    pass


def get_attrib(value_dict, key, default_value, exception=False):
    """Get a value of dictionary given a key if it exist, otherwise it throw an exception or give a default value.

    :param value_dict: dictionary to query
    :param key: key to search
    :param default_value: default value if key not find and exception argument is False
    :param exception: exception thrown if argument is True
    :return: value found if key exist, default value or an exception otherwise according of the exception value
    """

    if exception is True:
        try:
            value = value_dict[key]
        except:
            raise AttribException("Attribute %s must be specified" % key)
    else:
        value = default_value
        if key in value_dict:
            value = value_dict[key]

    return value


def get_value(value_dict: dict, key: str, default_value, exception: bool = False, vtype=None):
    """Get a value of dictionary given a key if it exist, otherwise it throw an exception or give a default value.
        Moreover it perform a type checking of returned value.

    :param value_dict: dictionary to query
    :param key: key to search
    :param default_value: value to return if key was not found and exception is False
    :param exception: if True raise exceptione when key was not found [default=False]
    :param vtype: if not None verify value is of type 'vtype'
    :return: value found if key exist, default value or an exception otherwise according of the exception value
    """

    if exception is True:
        try:
            value = value_dict[key]
        except KeyError as ex:
            raise AttribException("Attribute %s is missing" % key)
    else:
        value = value_dict.get(key, default_value)

    # check type
    if vtype is not None:
        if not isinstance(value, vtype):
            raise AttribException("Attribute type is wrong")

    return value


def get_attrib2(inst, key, default_value=None):
    """Get a value of dictionary given a key if it exist, default value otherwise

    :param inst: dictonary to query
    :param key: key to find
    :param default_value: value to return if key is not find
    :return: value found if key exist, default value otherwhise
    """
    value = default_value
    if inst.__dict__.has_key(key):
        value = inst.__dict__[key]

    return value


from flask import Request


def get_remote_ip(request: Request):
    """Get a remote id

    :param request: request to do
    :return:  remote ip
    """
    try:
        try:
            # get remote ip when use nginx as balancer
            ipaddr = request.environ["HTTP_X_REAL_IP"]
        except:
            ipaddr = request.environ["REMOTE_ADDR"]

        return ipaddr
    except RuntimeError:
        return None


def prefixlength_to_netmask(prefixlength):
    """Convert a cidr prefix length in subnet mask. Ex. 24 to 255.255.255.0.

    Inspired from: https://stackoverflow.com/questions/33750233/convert-cidr-to-subnet-mask-in-python

    :param prefixlength: cidr prefix length. Ex. 24, 21
    :return:
    """
    host_bits = 32 - int(prefixlength)
    netmask = inet_ntoa(pack("!I", (1 << 32) - (1 << host_bits)))
    return netmask


def set_request_params(kwargs, supported):
    """Set params in request data

    :param dict kwargs: input params
    :param list supported: list of supported param names
    :return: dict with params that are not None
    """
    data = {}
    for key in supported:
        val = getattr(kwargs, key, None)
        if val is not None:
            data[key] = val
    return data


def get_line(size, char="-"):
    """Create a string of size char

    :param size: line lenght
    :param char: character used to create string
    """
    res = char * size
    return res


def get_pretty_size(data):
    """Convert size in pritty string"""
    if 1024 < data <= 1048576:
        data = "%sKB" % round(data / 1024, 2)
    elif 1048576 < data <= 1073741824:
        data = "%sMB" % round(data / 1048576, 2)
    elif 1073741824 < data < 1099511627776:
        data = "%sGB" % round(data / 1073741824, 2)
    elif data > 1099511627776:
        data = "%sTB" % round(data / 1099511627776, 2)
    return data


def jsonDumps(data, ensure_ascii=False):
    """Check type of data
    (in lib ujson 4.0.x reject_bytes is on)
    (in lib ujson 2.0.x 'reject_bytes=False' is an invalid keyword argument)

    :param data: data to convert
    :param ensure_ascii: if True ensure ascii
    :return: a json
    """
    import ujson as json

    params = {}
    if ensure_ascii:
        params["ensure_ascii"] = ensure_ascii

    vers_json = json.__version__
    major = vers_json.split(".")[0]
    if int(major) >= 3:
        params["reject_bytes"] = False

    resp = json.dumps(data, **params)
    return resp
