# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte

from inspect import isclass
from re import compile as re_compile


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


def query_python_object(obj):
    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(getmembers(obj))


def dynamic_import(name):
    """Import dynamically a python library

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


def get_class_methods_by_decorator(cls, decorator_name):
    """get class methods by decorator name

    source: https://newbedev.com/how-to-get-all-methods-of-a-python-class-with-given-decorator

    :param cls: class
    :param decorator_name: decorator name
    :return:
    """
    import inspect
    res = []
    sourcelines = inspect.getsourcelines(cls)[0]
    for i, line in enumerate(sourcelines):
        line = line.strip()
        if line.split('(')[0].strip() == '@'+decorator_name: # leaving a bit out
            nextLine = sourcelines[i+1]
            name = nextLine.split('def')[1].split('(')[0].strip()
            # full_name = '%s.%s.%s' % (cls.__module__, cls.__name__, name)
            res.append(name)
    return res
