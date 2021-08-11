# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte

from inspect import getmembers, isclass
from struct import pack
from logging import getLogger
from socket import inet_ntoa
from math import ceil

logger = getLogger(__name__)


from.crypto import *
from .types.type_date import *
from .types.type_list import *
from .types.type_dict import *
from .types.type_string import *
from .types.type_id import *
from .file import *
from .password import *

# def check_vault(data, key):
#     """Check if data is encrypted with fernet token and AES128
#
#     :param data: data to verify. If encrypted token '$BEEHIVE_VAULT;AES128 | ' is in head of data
#     :param key: fernet key
#     :return: decrypted key
#     """
#     data = ensure_binary(data)
#     if data.find(b('$BEEHIVE_VAULT;AES128 | ')) == 0:
#         if key is None:
#             raise Exception('Fernet key must be provided')
#         cipher_suite = Fernet(ensure_binary(key))
#         data = data.replace(b('$BEEHIVE_VAULT;AES128 | '), b(''))
#         data = cipher_suite.decrypt(data)
#     data = data.decode('utf-8')
#     return data
#
#
# def is_encrypted(data):
#     """Check if data is encrypted with fernet token and AES128
#
#     :param data: data to verify. If encrypted token '$BEEHIVE_VAULT;AES128 | ' is in head of data
#     :return: True if data is encrypted, False otherwise
#     """
#     if data.find('$BEEHIVE_VAULT;AES128 | ') == 0:
#         return True
#     return False
#
#
# def generate_fernet_key():
#     """Generate fernet key
#
#     :return: fernet key
#     """
#     return Fernet.generate_key()
#
#
# def encrypt_data(fernet_key, data):
#     """Encrypt data using a fernet key and a symmetric algorithm
#
#     :param fernet_key: fernet key. To generate use: Fernet.generate_key()
#     :param data: data to encrypt
#     :return: encrypted data
#     """
#     cipher_suite = Fernet(ensure_binary(fernet_key))
#     cipher_data = ensure_text(cipher_suite.encrypt(ensure_binary(data)))
#     return '$BEEHIVE_VAULT;AES128 | %s' % cipher_data
#
#
# def decrypt_data(fernet_key, data):
#     """Decrypt data using a fernet key and a symmetric algorithm
#
#     :param fernet_key: fernet key
#     :param data: data to decrypt
#     :return: decrypted data
#     """
#     data = ensure_text(data)
#     if data.find('$BEEHIVE_VAULT;AES128 | ') == 0:
#         data = data.replace('$BEEHIVE_VAULT;AES128 | ', '')
#         cipher_suite = Fernet(ensure_binary(fernet_key))
#         cipher_data = cipher_suite.decrypt(ensure_binary(data))
#     else:
#         cipher_data = data
#     return cipher_data


# def flatten_dict(d, delimiter=":", loopArray=True):
#     """Flat dictionary conversion
#
#     :param loopArray: If True execute loop unrolling array items in keys. False otherwise
#     :param delimiter: delimiter char
#     :return dictionary unrolled with compound keys
#     """
#
#     def items():
#         for key, value in d.items():
#             if isinstance(value, dict):
#                 for subkey, subvalue in flatten_dict(value, delimiter=delimiter, loopArray=loopArray).items():
#                     yield key + delimiter + subkey, subvalue
#             elif isinstance(value, list):
#                 if loopArray:
#                     x = 0
#                     for itemArray in value:
#                         if isinstance(itemArray, dict):
#                             for subkey, subvalue in flatten_dict(itemArray, delimiter=delimiter,
#                                                                  loopArray=loopArray).items():
#                                 yield key + delimiter + str(x) + delimiter + subkey, subvalue
#                         else:
#                             yield key + delimiter + str(x), itemArray
#                         x += 1
#                 else:
#                     res = []
#                     for itemArray in value:
#                         res.append(flatten_dict(itemArray, delimiter=delimiter, loopArray=loopArray))
#                     yield key, res
#             else:
#                 yield key, value
#
#     return dict(items())


# def getkey(data, key, separator='.'):
#     """Get key value from a complex data (dict with child dict and list) using a string key.
#
#     Example:
#
#         a = {'k1':[{'k2':..}]}
#         b = getkey(a, 'k1.0.k2')
#
#     :param data: complex object. Dict with nested list and dict
#     :param key: complex key to search. Ex key1.0.key2
#     :param separator: [default=.] key1 / list index separator
#     :return: value that meet nested key
#     """
#     keys = key.split(separator)
#     res = data
#     for k in keys:
#         if isinstance(res, list):
#             try:
#                 res = res[int(k)]
#             except:
#                 res = {}
#         else:
#             res = res.get(k, {})
#     if isinstance(res, list):
#         res = jsonDumps(res)
#     if res is None or res == {}:
#         res = '-'
#
#     return res


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
    convert = '%.' + b(decimal) + 'f'
    return convert % (ceil(number * factor) / factor)


# def merge_dicts(*dict_args):
#     """Given any number of dicts, shallow copy and merge into a new dict, precedence goes to key value pairs in latter
#     dicts.
#
#     :param *dict_args arbitrary number of dictionaries (1 to N)
#     :return dict union of the N dict arguments
#     """
#     result = {}
#     for dictionary in dict_args:
#         result.update(dictionary)
#     return result


# def merge_list(*list_args):
#     """Given any number of lists, merge into a new list.
#
#     :param *list_args arbitrary number of list (1 to N)
#     :return list
#     """
#     result = []
#     for list_arg in list_args:
#         result.extend(list_arg)
#     return result


# def run_command(command):
#     """Run a shell command as an external process and return response or error.
#
#     :param command: unix command: list like ['ls', '-l', 'ps']
#     :param stdout: pipe to the standard out stream should be opened, default subprocess.PIPE
#     :param stderr: pipe to the standard error stream should be opened, default subprocess.PIPE
#     :returns tuple of 0 and the output of the command if there is no error, code error and error message otherwise
#     """
#     p = Popen(command, stdout=PIPE, stderr=PIPE)
#     out, err = p.communicate()
#     if p.returncode == 0:
#         return 0, out
#     else:
#         return p.returncode, err


# def str2uni(value):
#     """Convert in unicode (py2) or string (py3)
#
#     :param value: string to convert
#     :return: unicode (py2) or string (py3)
#     """
#     value = ensure_text(value)
#     return value


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


def get_value(value_dict, key, default_value, exception=False, vtype=None):
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
        except:
            raise AttribException('Attribute %s is missing' % key)
    else:
        value = default_value
        if key in value_dict:
            value = value_dict[key]

    # check type
    if vtype is not None:
        if not isinstance(value, vtype):
            raise AttribException('Attribute type is wrong')

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


def getmembers(obj, predicate=None):
    """Return all members of an object as (name, value) pairs sorted by name.
    Optionally, only return members that satisfy a given predicate.

    :param obj:
    :param predicate: predicate to satisfy
    :return: list of members
    """
    results = []
    for key in dir(obj):

        try:
            value = getattr(obj, key)
        except AttributeError:
            continue
        if not predicate or predicate(value):
            results.append((key, value))
    results.sort()
    return results


# def print_table(fields, data):
#     """print a list of value and header like a table in string format
#
#     :param fields: list like ["City name", "Area", "Population", "Annual Rainfall"]
#     :param data: list like ["Adelaide",1295, 1158259, 600.5]
#     :return: table string formatted
#     """
#
#     tab = PrettyTable(fields)
#     tab.align = "l"  # Left align city names
#     tab.padding_width = 1  # One space between column edges and contents (default)
#     for item in data:
#         tab.add_row(item)
#     return tab
#
#
# def print_table_from_dict(list, order_field=None):
#     """print a list of dictionary like a table in string format and eventually order a determined column
#
#     :param list: list of dictionary
#     :param order_field: column to order
#     :return: None if list
#     """
#     if len(list) > 0:
#         fields = list[0].keys()
#         data = []
#         for item in list:
#             data.append(item.values())
#         tab = print_table(fields, data)
#
#         if order_field:
#             print(tab.get_string(sortby=order_field))
#         else:
#             print(tab)
#     else:
#         return None


def query_python_object(obj):
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(getmembers(obj))


def dynamic_import(name):
    """Import dinamically a python library

    :param name: name of the library
    :return:
    """
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def import_func(name):
    """Import dinamically a function

    :param name: name of the function
    :return:
    """
    components = name.split('.')
    mod = __import__('.'.join(components[:-1]), globals(), locals(), [components[-1]], -1)
    func = getattr(mod, components[-1], None)
    return func


def import_class(cl):
    """Import dinamically a class

    :param cl: name of the class
    :return:
    """

    cl = str(cl)
    d = cl.rfind(".")
    classname = cl[d + 1:len(cl)]
    m = __import__(cl[0:d], globals(), locals(), [classname])
    return getattr(m, classname, None)


def get_class_props(cls):
    return [i for i in cls.__dict__.keys() if i[:1] != '_']


def get_member_class(args):
    """"""
    try:
        classname = args[0].__class__.__name__
    except:
        classname = ''
    return classname


def get_class_name(classref):
    """"""
    name = str(classref).split('.')[-1].rstrip("'>").lower()
    return "%s.%s" % (classref.__module__, name)


# def id_gen(length=10, parent_id=None):
#     """Generate unique uuid according to RFC 4122
#
#     :param length: length of id to generate
#     :param parent_id: root to append in the id
#     :return: oid generated
#     """
#     oid = hexlify(urandom(int(length / 2)))
#     if parent_id is not None:
#         oid = '%s//%s' % (parent_id, ensure_text(oid))
#     return ensure_text(oid)
#
#
# def token_gen(args=None):
#     """Generate a 128 bit token according to RFC 4122
#     :return: token generated
#     """
#     return str(uuid4())
#
#
# def transaction_id_generator(length=20):
#     """Generate random string to use as transaction id
#
#     :param length: length of id to generate
#     return : random string
#     """
#     import random
#     chars = ascii_letters + digits
#     random.seed = (urandom(1024))
#     return ''.join(choice(chars) for i in range(length))


def get_remote_ip(request):
    """Get a remote id

    :param request: request to do
    :return:  remote ip
    """
    try:
        try:
            # get remote ip when use nginx as balancer
            ipaddr = request.environ['HTTP_X_REAL_IP']
        except:
            ipaddr = request.environ['REMOTE_ADDR']

        return ipaddr
    except RuntimeError:
        return None


# def truncate(msg, size=600, replace_new_line=True):
#     """Truncate message to fixed size.
#
#     :param str msg: message to truncate
#     :param size: max message length [default=400]
#     :return: truncated Message with ...
#     """
#     msg = str(msg)
#     if replace_new_line is True:
#         msg = msg.replace('\n', ' + ')
#
#     if len(msg) > size:
#         return msg[0:size] + '...'
#     else:
#         return msg


# def set_dict_item(in_dict, key, value):
#     """Set item in input dictionary if item is not None
#
#     :param in_dict: input dictionary
#     :param value: key value to add
#     :param key: dictionary key to add
#     :return dictionary modified
#     """
#     if value is not None:
#         in_dict[key] = value
#     return in_dict


# def parse_redis_uri(uri):
#     """Parse redis uri.
#
#     :param uri: redis connection uri. Ex
#             ``redis://localhost:6379/1``
#             ``localhost:6379:1``
#             ``redis-cluster://localhost:6379,localhost:6380``
#
#     :return:
#
#         {'type':'single', 'host':host, 'port':port, 'db':db}
#
#         or
#
#         {'type':'cluster', 'nodes':[
#             {'host': '10.102.184.121', 'port': '6379'},
#             {'host': '10.102.91.23', 'port': '6379'}
#         ]}
#
#     """
#     # redis cluster
#     if uri.find('redis-cluster') >= 0:
#         redis_uri = uri.replace('redis-cluster://', '')
#         host_ports = redis_uri.split(',')
#         cluster_nodes = []
#         for host_port in host_ports:
#             host, port = host_port.split(':')
#             cluster_nodes.append({'host': host, 'port': port})
#         res = {'type': 'cluster', 'nodes': cluster_nodes}
#
#     # redis with sentinel
#     elif uri.find('redis-sentinel') >= 0:
#         pwd = None
#         if uri.find('@') > 0:
#             redis_uri = uri.replace('redis-sentinel://:', '')
#             pwd, redis_uri = redis_uri.split('@')
#         else:
#             redis_uri = uri.replace('redis-sentinel://', '')
#         hosts, group, port = redis_uri.split(':')
#         port, db = port.split('/')
#         res = {'type': 'sentinel', 'hosts': hosts.split(','), 'port': int(port), 'db': int(db), 'pwd': pwd,
#                'group': group}
#
#     # single redis node
#     elif uri.find('redis') >= 0:
#         pwd = None
#         if uri.find('@') > 0:
#             redis_uri = uri.replace('redis://:', '')
#             pwd, redis_uri = redis_uri.split('@')
#         else:
#             redis_uri = uri.replace('redis://', '')
#         host, port = redis_uri.split(':')
#         port, db = port.split('/')
#         res = {'type': 'single', 'host': host, 'port': int(port), 'db': int(db), 'pwd': pwd}
#
#     # single redis node
#     else:
#         host, port, db = uri.split(";")
#         res = {'type': 'single', 'host': host, 'port': int(port), 'db': int(db)}
#
#     return res


# def str2bool(value):
#     """Convert value from string to bool
#
#     :param value: value to convert
#     :return: converted value
#     """
#
#     res = None
#     if value in ['False', 'false', 0, 'no', False]:
#         res = False
#     elif value in ['True', 'true', 1, 'yes', 'si', True]:
#         res = True
#     return res
#
#
# def bool2str(value):
#     """Convert value from bool to string
#
#     :param value: value to convert
#     :return: converted value
#     """
#
#     res = None
#     if value in [False, 0, 'no']:
#         res = 'false'
#     elif value in [True, 1, 'yes', 'si']:
#         res = 'true'
#     return res


# def parse_date(data_str, format=None):
#     """Parse string to date
#
#     :param data_str: date in string format
#     :param format: format date ex: %Y-%m-%dT%H:%M
#     :return: date
#     """
#     if format is None:
#         time_format = '%Y-%m-%dT%H:%M:%SZ'
#     else:
#         time_format = format
#
#     res = None
#     if data_str is not None:
#         res = datetime.strptime(data_str, time_format)
#     return res
#
#
# def format_date(date, format=None, microsec=False):
#     """Format date as rfc3339.
#
#     Ref. https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html
#
#     :param date: datetime object
#     :param format: format date ex: %Y-%m-%dT%H:%M
#     :return: formatted date
#     """
#
#     if format is None:
#         time_format = '%Y-%m-%dT%H:%M:%SZ'
#         if microsec is True:
#             time_format += '.%f'
#     else:
#         time_format = format
#     res = None
#     if date is not None:
#         res = ensure_text(date.strftime(time_format))
#     return res
#
#
# def get_date_from_timestamp(date):
#     if date is not None:
#         return datetime.fromtimestamp(date)
#     else:
#         return None
#
#
# def get_timestamp_from_date(date):
#     if date is not None:
#         return datetime.timestamp(date)
#     else:
#         return None


# def compat(data):
#     try:
#         if isinstance(data, list):
#             data = '[..]'
#         elif isinstance(data, dict):
#             newdata = {}
#             for k, v in data.items():
#                 newdata[k] = compat(v)
#             data = newdata
#         elif isclass(data) is True:
#             data = str(data)
#         else:
#             data = truncate(data, 30)
#     except:
#         logger.warning('compat data %s error' % data, exc_info=True)
#         data = None
#     return data


# def dict_get(data, key, separator='.', default=None):
#     """Get a value from a dict. Key can be composed to get a field in a complex dict that contains other dict, list and
#     string.
#
#     :param data: dictionary to query
#     :param key: key to search
#     :param separator: key depth separator
#     :param default: default value [default=None]
#     :return:
#     """
#     keys = key.split(separator)
#     res = data
#     for k in keys:
#         if isinstance(res, list):
#             try:
#                 res = res[int(k)]
#             except:
#                 res = {}
#         else:
#             if res is not None:
#                 res = res.get(k, {})
#     if res is None or res == {}:
#         res = default
#
#     return res
#
#
# def dict_set(data, key, value, separator='.'):
#     """Set a key in a dict. Key can be a composition of different keys separated by a separator.
#
#     :param data: dictionary to query
#     :param key: key to update
#     :param value: key new value
#     :param separator: key depth separator
#     :return:
#     """
#     def __dict_set(data):
#         k = keys.pop()
#         if len(keys) == 0:
#             data[k] = value
#         else:
#             if k not in data or not isinstance(data[k], dict):
#                 data[k] = {}
#             data[k] = __dict_set(data[k])
#         return data
#
#     keys = key.split(separator)
#     keys.reverse()
#     data = __dict_set(data)
#
#     return data
#
#
# def dict_unset(data, key, separator='.'):
#     """Unset a key in a dict. Key can be a composition of different keys separated by a separator.
#
#     :param data: dictionary to query
#     :param key: key to remove
#     :param separator: key depth separator
#     :return:
#     """
#     def __dict_unset(data):
#         k = keys.pop()
#         if len(keys) == 0:
#             if k in data:
#                 data.pop(k, None)
#         else:
#             if k in data:
#                 data[k] = __dict_unset(data[k])
#         return data
#
#     keys = key.split(separator)
#     keys.reverse()
#     data = __dict_unset(data)
#
#     return data


def prefixlength_to_netmask(prefixlength):
    """Convert a cidr prefix length in subnet mask. Ex. 24 to 255.255.255.0.

    Inspired from: https://stackoverflow.com/questions/33750233/convert-cidr-to-subnet-mask-in-python

    :param prefixlength: cidr prefix length. Ex. 24, 21
    :return:
    """
    host_bits = 32 - int(prefixlength)
    netmask = inet_ntoa(pack('!I', (1 << 32) - (1 << host_bits)))
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


def get_line(size, char='-'):
    """Create a string of size char

    :param size: line lenght
    :param char: character used to create string
    """
    res = char * size
    return res


def get_pretty_size(data):
    """Convert size in pritty string"""
    if 1024 < data <= 1048576:
        data = '%sKB' % round(data / 1024, 2)
    elif 1048576 < data <= 1073741824:
        data = '%sMB' % round(data / 1048576, 2)
    elif data > 1073741824:
        data = '%sGB' % round(data / 1073741824, 2)
    elif data > 1073741824:
        data = '%sTB' % round(data / 1073741824, 2)
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
        params['ensure_ascii'] = ensure_ascii

    vers_json = json.__version__
    major = vers_json.split(".")[0]
    if int(major) >= 3:
        params['reject_bytes'] = False

    resp = json.dumps(data, **params)
    return resp
