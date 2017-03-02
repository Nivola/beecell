'''
Created on Jul 18, 2012

@author: darkbk
'''
import sys
import os, string, random
import time
import logging
import subprocess
from prettytable import PrettyTable
#import M2Crypto
import string
import binascii
from uuid import uuid4

def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def random_password(length=10):
    chars = string.ascii_uppercase + string.digits + string.ascii_lowercase
    password = ''
    for i in range(length):
        #password += chars[ord(M2Crypto.m2.rand_bytes(1)) % len(chars)]
        password += chars[ord(os.urandom(1)) % len(chars)]
        
    return password

def run_command(command):
    """Run a shell command as an external process and return response or error.
    
    :param command: list like ['ls', '-l']
    """
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode == 0:
        return (0, out)
    else:
        return (p.returncode, err)

def str2uni(value):
    if type(value) is str:
        return value.decode('UTF8')
    return value

'''
def get_attrib(value_dict, key, default_value):
    """ """
    value = default_value
    if key in value_dict:
        value = value_dict[key]

    return value'''

class AttribException(Exception): pass

def get_attrib(value_dict, key, default_value, exception=False):
    """ """
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
    """Get value from dictionary and apply some controls.
    
    :param value_dict: dictionary to query
    :param key: key to search
    :param default_value: value to return if key was not found and exception is 
            False
    :param exception: if True raise exceptione whne key was not foud [default=False]
    :param vtype: if not None verify value is of type 'vtype'
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
    """ """
    value = default_value
    if inst.__dict__.has_key(key):
        value = inst.__dict__[key]

    return value

def getmembers(obj, predicate=None):
    """Return all members of an object as (name, value) pairs sorted by name.
    Optionally, only return members that satisfy a given predicate."""
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
    """
    :param fields:list like ["City name", "Area", "Population", "Annual Rainfall"]
    :param dat:list like ["Adelaide",1295, 1158259, 600.5]
    """
    tab = PrettyTable(fields)
    tab.align = "l" # Left align city names
    tab.padding_width = 1 # One space between column edges and contents (default)
    for item in data:
        tab.add_row(item)
    return tab

def print_table_from_dict(list, order_field=None):
    if len(list) > 0:
        fields = list[0].keys()
        data = []
        for item in list:
            data.append(item.values())
        tab = print_table(fields, data)
    
        if order_field:
            print tab.get_string(sortby=order_field)
        else:
            print tab
    else:
        return None

def query_python_object(obj):
    """ """
    import pprint
    import inspect
    
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(inspect.getmembers(obj))

def dynamic_import(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod

def import_class(cl):
    cl = str(cl)
    d = cl.rfind(".")
    classname = cl[d+1:len(cl)]
    m = __import__(cl[0:d], globals(), locals(), [classname])
    return getattr(m, classname)

def get_class_props(cls):
    return [i for i in cls.__dict__.keys() if i[:1] != '_']    

def get_member_class(args):
    """"""
    try: classname = args[0].__class__.__name__
    except: classname = ''
    return classname

def get_class_name(classref):
    """"""
    name = str(classref).split('.')[-1].rstrip("'>").lower()
    return "%s.%s" % (classref.__module__, name)

def id_gen(length = 10):
    """Generate unique uuid according to RFC 4122
    """
    '''
    #print random.seed()
    #random.seed(time.time())
    num = 1
    for i in xrange(1, length):
        num = num * 10
    return str(int(round(random.random()*num, 0)))
    #return binascii.b2a_hex(os.urandom(length))
    '''
    #oid = str(uuid4())
    oid = binascii.hexlify(os.urandom(length))
    return oid

def transaction_id_generator(length = 20):
    '''
    Generate random string to use as transaction id
    return : random string
    '''
    chars = string.ascii_letters + string.digits
    random.seed = (os.urandom(1024)) 
    return u''.join(random.choice(chars) for i in range(length))

def get_remote_ip(request):
    try:
        # get remote ip when use nginx as balancer
        ipaddr = request.environ['HTTP_X_REAL_IP']
    except:
        ipaddr = request.environ['REMOTE_ADDR']
    
    return ipaddr

def truncate(msg, size=400):
    """Truncate message to fixed size.
    
    :param str msg: message to truncate
    :param size: max message length [default=200]
    :return: truncated Message
    """
    msg = str(msg)
    if len(msg) > size:
        return msg[0:size] + '...'
    else:
        return msg
    
def set_dict_item(in_dict, key, value):
    """Set item in input dictionary if item is not None
    
    :param in_dict: input dictionary
    :param value: key value to add
    :param key: dictionary key to add
    """
    if value is not None:
        in_dict[key] = value
    return in_dict

def parse_redis_uri(uri):
    """Parse redis uri.
    
    :param uri: can be redis://localhost:6379/1 or localhost;6379;1
    :return: (host, port, db)
    :rtype: tupla
    """
    # parse redis uri
    if uri.find('redis') >= 0:
        redis_uri = uri.lstrip('redis://')
        host, port = redis_uri.split(':')
        port, db = port.split('/')
    else:
        host, port, db = uri.split(";")
        
    return host, port, db
    