# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
from struct import pack

import ujson as json
import os, random, subprocess, logging
from socket import inet_ntoa
from prettytable import PrettyTable
import string
import binascii
from uuid import uuid4
from math import ceil
from cryptography.fernet import Fernet
import datetime

logger = logging.getLogger(__name__)


def check_vault(data, key):
    """Check if data is encrypted with fernet token and AES128

    :param data: data to verify. If encrypted token '$BEEHIVE_VAULT;AES128 | ' is in head of data
    :param key: fernet key
    :return: decrypted key
    """
    if data.find(u'$BEEHIVE_VAULT;AES128 | ') == 0:
        if key is None:
            raise Exception(u'Fernet key must be provided')
        cipher_suite = Fernet(key)
        data = str(data.replace(u'$BEEHIVE_VAULT;AES128 | ', u''))
        data = cipher_suite.decrypt(data)
    return data


def is_encrypted(data):
    """Check if data is encrypted with fernet token and AES128

    :param data: data to verify. If encrypted token '$BEEHIVE_VAULT;AES128 | ' is in head of data
    :return: True if data is encrypted, False otherwise
    """
    if data.find(u'$BEEHIVE_VAULT;AES128 | ') == 0:
        return True
    return False


def encrypt_data(fernet_key, data):
    """Encrypt data using a fernet key and a symmetric algorithm

    :param fernet_key: fernet key
    :param data: data to encrypt
    :return: encrypted data
    """
    cipher_suite = Fernet(fernet_key)
    cipher_data = cipher_suite.encrypt(str(data))
    return u'$BEEHIVE_VAULT;AES128 | %s' % cipher_data


def decrypt_data(fernet_key, data):
    """Decrypt data using a fernet key and a symmetric algorithm

    :param fernet_key: fernet key
    :param data: data to decrypt
    :return: decrypted data
    """
    if data.find(u'$BEEHIVE_VAULT;AES128 | ') == 0:
        data = data.replace(u'$BEEHIVE_VAULT;AES128 | ', u'')
        cipher_suite = Fernet(fernet_key)
        cipher_data = cipher_suite.decrypt(str(data))
    else:
        cipher_data = data
    return cipher_data


def flatten_dict(d, delimiter=":", loopArray=True):
    """ Flat dictionary conversion

    :param loopArray: If True execute loop unrolling array items in keys. False otherwise
    :param delimiter: delimiter char
    :return dictionary unrolled with compound keys
    """

    def items():
        for key, value in d.items():
            if isinstance(value, dict):
                for subkey, subvalue in flatten_dict(value, delimiter=delimiter, loopArray=loopArray).items():
                    yield key + delimiter + subkey, subvalue
            elif isinstance(value, list):
                if loopArray:
                    x = 0
                    for itemArray in value:
                        if isinstance(itemArray, dict):
                            for subkey, subvalue in flatten_dict(itemArray, delimiter=delimiter,
                                                                 loopArray=loopArray).items():
                                yield key + delimiter + str(x) + delimiter + subkey, subvalue
                        else:
                            yield key + delimiter + str(x), itemArray
                        x += 1
                else:
                    res = []
                    for itemArray in value:
                        res.append(flatten_dict(itemArray, delimiter=delimiter, loopArray=loopArray))
                    yield key, res
            else:
                yield key, value

    return dict(items())


def getkey(data, key, separator=u'.'):
    """Get key value from a complex data (dict with child dict and list) using a string key.

    Example:

        a = {u'k1':[{u'k2':..}]}
        b = getkey(a, u'k1.0.k2')

    :param data: complex object. Dict with nested list and dict
    :param key: complex key to search. Ex key1.0.key2
    :param separator: [default=.] key1 / list index separator
    :return: value that meet nested key
    """
    keys = key.split(separator)
    res = data
    for k in keys:
        if isinstance(res, list):
            try:
                res = res[int(k)]
            except:
                res = {}
        else:
            res = res.get(k, {})
    if isinstance(res, list):
        res = json.dumps(res)
    if res is None or res == {}:
        res = u'-'

    return res


def nround(number, decimal=4):
    """Round a given number

    Example: decimal = 2

        3.5643 -> u'3.60'
        3.5343 -> u'3.55'

    :param number: number to round
    :param decimal: number of decimal to keep
    :return: rounded number in UNICODE format
    """
    factor = 10 * decimal
    convert = u'%.' + str(decimal) + u'f'
    return convert % (ceil(number * factor) / factor)


def merge_dicts(*dict_args):
    """Given any number of dicts, shallow copy and merge into a new dict, precedence goes to key value pairs in latter
    dicts.

    :param *dict_args arbitrary number of dictionaries (1 to N)
    :return dict union of the N dict arguments
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def random_password(length=10, strong=False):
    """Generate random password
    inspired to: https://pynative.com/python-generate-random-string/

    :param length: length of string to generate
    :param strong: True for generate strong password (include upper/lowercase, digits and random_password character)
    :return: generated password in UNICODE format
    """
    chars = string.ascii_uppercase + string.digits + string.ascii_lowercase

    if strong is True:
        punctuation = u'()#_-.'
        randomSource = string.ascii_letters + string.digits + punctuation
        password = random.SystemRandom().choice(string.ascii_lowercase)
        password += random.SystemRandom().choice(string.ascii_uppercase)
        password = random.SystemRandom().choice(string.ascii_lowercase)
        password += random.SystemRandom().choice(string.ascii_uppercase)
        password += random.SystemRandom().choice(string.digits)
        password += random.SystemRandom().choice(punctuation)
        password += random.SystemRandom().choice(punctuation)

        for i in range(length - 7):
            password += random.SystemRandom().choice(randomSource)

        passwordList = list(password)
        random.SystemRandom().shuffle(passwordList)
        password = u''.join(passwordList)
    else:
        password = u''
        for i in range(length):
            password += chars[ord(os.urandom(1)) % len(chars)]

    return password


def run_command(command):
    """Run a shell command as an external process and return response or error.

    :param command: unix command: list like ['ls', '-l', 'ps']
    :param stdout: pipe to the standard out stream should be opened, default subprocess.PIPE
    :param stderr: pipe to the standard error stream should be opened, default subprocess.PIPE
    :returns tuple of 0 and the output of the command if there is no error, code error and error message otherwise
    """
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode == 0:
        return 0, out
    else:
        return p.returncode, err


def str2uni(value):
    """Converts a string in a UNICODE format.

    :param value: string to convert
    :return: UNICODE string
    """
    if type(value) is str:
        return value.decode('UTF8')
    return value


class AttribException(Exception): pass


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
            raise AttribException(u'Attribute %s is missing' % key)
    else:
        value = default_value
        if key in value_dict:
            value = value_dict[key]

    # check type
    if vtype is not None:
        if not isinstance(value, vtype):
            raise AttribException(u'Attribute type is wrong')

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


def print_table(fields, data):
    """print a list of value and header like a table in string format

    :param fields: list like ["City name", "Area", "Population", "Annual Rainfall"]
    :param data: list like ["Adelaide",1295, 1158259, 600.5]
    :return: table string formatted
    """

    tab = PrettyTable(fields)
    tab.align = "l"  # Left align city names
    tab.padding_width = 1  # One space between column edges and contents (default)
    for item in data:
        tab.add_row(item)
    return tab


def print_table_from_dict(list, order_field=None):
    """print a list of dictionary like a table in string format and eventually order a determined column

    :param list: list of dictionary
    :param order_field: column to order
    :return: None if list
    """
    if len(list) > 0:
        fields = list[0].keys()
        data = []
        for item in list:
            data.append(item.values())
        tab = print_table(fields, data)

        if order_field:
            print(tab.get_string(sortby=order_field))
        else:
            print(tab)
    else:
        return None


def query_python_object(obj):
    import pprint
    import inspect

    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(inspect.getmembers(obj))


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
    components = name.split(u'.')
    mod = __import__(u'.'.join(components[:-1]), globals(), locals(), [components[-1]], -1)
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
    return getattr(m, classname)


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


def id_gen(length=10, parent_id=None):
    """Generate unique uuid according to RFC 4122

    :param length: length of id to generate
    :param parent_id: root to append in the id
    :return: oid generated
    """
    oid = binascii.hexlify(os.urandom(int(length / 2)))
    if parent_id is not None:
        oid = u'%s//%s' % (parent_id, oid)
    return oid


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

    chars = string.ascii_letters + string.digits
    random.seed = (os.urandom(1024))
    return u''.join(random.choice(chars) for i in range(length))


def get_remote_ip(request):
    """Get a remote id

    :param request: request to do
    :return:  remote ip
    """

    try:
        try:
            # get remote ip when use nginx as balancer
            ipaddr = request.environ[u'HTTP_X_REAL_IP']
        except:
            ipaddr = request.environ[u'REMOTE_ADDR']

        return ipaddr
    except RuntimeError:
        return None


def truncate(msg, size=200):
    """Truncate message to fixed size.

    :param str msg: message to truncate
    :param size: max message length [default=400]
    :return: truncated Message with ...
    """
    msg = str(msg)
    msg = msg.replace('\n', ' | ')

    if len(msg) > size:
        return msg[0:size] + '...'
    else:
        return msg


def set_dict_item(in_dict, key, value):
    """Set item in input dictionary if item is not None

    :param in_dict: input dictionary
    :param value: key value to add
    :param key: dictionary key to add
    :return dictionary modified
    """
    if value is not None:
        in_dict[key] = value
    return in_dict


def parse_redis_uri(uri):
    """Parse redis uri.

    :param uri: redis connection uri. Ex
            ``redis://localhost:6379/1``
            ``localhost:6379:1``
            ``redis-cluster://localhost:6379,localhost:6380``

    :return:

        {u'type':u'single', u'host':host, u'port':port, u'db':db}

        or

        {u'type':u'cluster', u'nodes':[
            {u'host': u'10.102.184.121', u'port': u'6379'},
            {u'host': u'10.102.91.23', u'port': u'6379'}
        ]}

    """

    # redis cluster
    if uri.find(u'redis-cluster') >= 0:
        redis_uri = uri.replace(u'redis-cluster://', u'')
        host_ports = redis_uri.split(u',')
        cluster_nodes = []
        for host_port in host_ports:
            host, port = host_port.split(u':')
            cluster_nodes.append({u'host': host, u'port': port})
        res = {u'type': u'cluster', u'nodes': cluster_nodes}

    # single redis node
    elif uri.find(u'redis') >= 0:
        pwd = None
        if uri.find(u'@') > 0:
            redis_uri = uri.replace(u'redis://:', u'')
            pwd, redis_uri = redis_uri.split(u'@')
        else:
            redis_uri = uri.replace(u'redis://', u'')
        host, port = redis_uri.split(u':')
        port, db = port.split(u'/')
        res = {u'type': u'single', u'host': host, u'port': int(port), u'db': int(db), u'pwd': pwd}

    # single redis node
    else:
        host, port, db = uri.split(";")
        res = {u'type': u'single', u'host': host, u'port': int(port), u'db': int(db)}

    return res


def str2bool(value):
    """Convert value from string to bool

    :param value: value to convert
    :return: converted value
    """

    res = None
    if value in [u'False', u'false', 0, u'no', False]:
        res = False
    elif value in [u'True', u'true', 1, u'yes', u'si', True]:
        res = True
    return res


def bool2str(value):
    """Convert value from bool to string

    :param value: value to convert
    :return: converted value
    """

    res = None
    if value in [False, 0, u'no']:
        res = u'false'
    elif value in [True, 1, u'yes', u'si']:
        res = u'true'
    return res


def parse_date(data_str, format=None):
    """Parse string to date

    :param data_str: date in string format
    :param format: format date ex: %Y-%m-%dT%H:%M
    :return: date
    """
    if format is None:
        time_format = u'%Y-%m-%dT%H:%M:%SZ'
    else:
        time_format = format

    res = None
    if data_str is not None:
        res = datetime.datetime.strptime(data_str, time_format)
    return res


def format_date(date, format=None, microsec=False):
    """Format date as rfc3339.

    Ref. https://xml2rfc.tools.ietf.org/public/rfc/html/rfc3339.html

    :param date: datetime object
    :param format: ormat date ex: %Y-%m-%dT%H:%M
    :return: formatted date
    """

    if format is None:
        time_format = u'%Y-%m-%dT%H:%M:%SZ'
        if microsec is True:
            time_format += u'.%f'
    else:
        time_format = format
    res = None
    if date is not None:
        res = str2uni(date.strftime(time_format))
    return res


def compat(data):
    if isinstance(data, list):
        for item in data:
            item = compat(item)
    if isinstance(data, dict):
        for k, v in data.items():
            data[k] = compat(v)
    else:
        data = truncate(data, 30)
    return data


def isBlank(myString):
    """Test if string is blank

    :param myString: string to test
    :return: True if blank, False otherwhise
    """

    return not (myString and myString.strip())


def isNotBlank(myString):
    """Test if string is not blank

    :param myString: string to test
    :return: True if not blank, False otherwhise
    """

    return bool(myString and myString.strip())


def obscure_data(data, fields=[u'password', u'pwd', u'passwd', u'pass']):
    """Obscure some fields in data, fields can be password.

    :param data: data to check
    :param fields: list of fields to obfuscate. default=[u'password', u'pwd', u'passwd']
    :return: obscured data
    """
    if isinstance(data, str) or isinstance(data, unicode):
        return obscure_string(data, fields)

    for key, value in data.items():
        if isinstance(value, dict):
            obscure_data(value, fields)
        elif isinstance(value, str) or isinstance(value, unicode):
            for field in fields:
                if key.lower().find(field) >= 0:
                    data[key] = u'xxxxxx'
    return data


def obscure_string(data, fields=[u'password', u'pwd', u'passwd', u'pass']):
    """Obscure entire string if it contains passwords.

    :param data: data to check
    :param fields: list of fields to obfuscate. default=[u'password', u'pwd', u'passwd']
    :return: obscured strinng
    """
    for field in fields:
        if data.lower().find(field) >= 0:
            data = u'xxxxxx'
    return data


def dict_get(data, key, separator=u'.', default=None):
    """Get a value from a dict. Key can be composed to get a field in a complex dict that contains other dict, list and
    string.

    :param data: dictionary to query
    :param key: key to search
    :param separator: key depth separator
    :param default: default value [default=None]
    :return:
    """
    keys = key.split(separator)
    res = data
    for k in keys:
        if isinstance(res, list):
            try:
                res = res[int(k)]
            except:
                res = {}
        else:
            if res is not None:
                res = res.get(k, {})
    if res is None or res == {}:
        res = default

    return res


def dict_set(data, key, value, separator=u'.'):
    """Set a key in a dict. Key can be a composition of different keys separated by a separator.

    :param data: dictionary to query
    :param key: key to update
    :param value: key new value
    :param separator: key depth separator
    :return:
    """
    def __dict_set(data):
        k = keys.pop()
        if len(keys) == 0:
            data[k] = value
        else:
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data[k] = __dict_set(data[k])
        return data

    keys = key.split(separator)
    keys.reverse()
    data = __dict_set(data)

    return data


def dict_unset(data, key, separator=u'.'):
    """Unset a key in a dict. Key can be a composition of different keys separated by a separator.

    :param data: dictionary to query
    :param key: key to remove
    :param separator: key depth separator
    :return:
    """
    def __dict_unset(data):
        k = keys.pop()
        if len(keys) == 0:
            if k in data:
                data.pop(k, None)
        else:
            if k in data:
                data[k] = __dict_unset(data[k])
        return data

    keys = key.split(separator)
    keys.reverse()
    data = __dict_unset(data)

    return data


def prefixlength_to_netmask(prefixlength):
    """Convert a cidr prefix length in subnet mask. Ex. 24 to 255.255.255.0.

    Inspired from: https://stackoverflow.com/questions/33750233/convert-cidr-to-subnet-mask-in-python

    :param prefixlength: cidr prefix length. Ex. 24, 21
    :return:
    """
    host_bits = 32 - int(prefixlength)
    netmask = inet_ntoa(pack('!I', (1 << 32) - (1 << host_bits)))
    return netmask
