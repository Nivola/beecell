# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2026 CSI-Piemonte
import sys
from typing import Type, Any

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


def dynamic_import(name: str):
    """Import dynamically a python library

    :param name: name of the library
    :return:
    """
    mod = __import__(name)
    components = name.split(".")
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def import_func(name: str):
    """Import dinamically a function

    :param name: name of the function
    :return:
    """
    components = name.split(".")
    mod = __import__(".".join(components[:-1]), globals(), locals(), [components[-1]], -1)
    func = getattr(mod, components[-1], None)
    return func


def import_class(cl)-> Type[Any]:
    """Import dinamically a class

    :param cl: name of the class
    :return:
    """

    cl = str(cl)
    d = cl.rfind(".")
    classname = cl[d + 1 : len(cl)]
    m = __import__(cl[0:d], globals(), locals(), [classname])
    return getattr(m, classname, None)

def import_class_safe(fq_class_path: str) -> Type[Any]:
    """
    Import a class from a fully-qualified class path.

    Example:
        cls = import_class("mypackage.mymodule.MyClass")

    :param path: Fully qualified class name.
    :return: The imported class object.
    :raises ValueError: If the path is invalid.
    :raises ImportError: If the module cannot be imported.
    :raises AttributeError: If the class is not in the module.
    """
    from importlib import import_module
    module_path, _, class_name = fq_class_path.rpartition(".")

    if not module_path:
        raise ValueError(f"invalid class path '{fq_class_path}'. Expected 'module.submodule.ClassName' format.")

    module = import_module(module_path)
    try:
        return getattr(module, class_name)
    except AttributeError as e:
        raise AttributeError(
            f"class '{class_name}' not found in module '{module_path}'."
        ) from e



def get_class_props(cls: Type[Any]):
    return [i for i in cls.__dict__.keys() if i[:1] != "_"]


def get_member_class(args):
    """"""
    try:
        classname = args[0].__class__.__name__
    except:
        classname = ""
    return classname


def get_class_name(classref):
    """"""
    name = str(classref).split(".")[-1].rstrip("'>").lower()
    return "%s.%s" % (classref.__module__, name)


def get_class_fullname(cls: Type[Any]) -> str:
    """
    Return the fully-qualified class name, including module and nested scopes.
    Handles nested classes, classes defined inside functions, and dynamic classes.
    """
    module = cls.__module__
    name = cls.__qualname__
    if module is not None and module != "__builtin__":
        name = module + "." + name
    return name

def get_class_fullname_safe(cls: Type[Any]) -> str:
    """
    Return the fully-qualified class name, including module and nested scopes.
    Handles nested classes, classes defined inside functions, and dynamic classes.
    """
    module = cls.__module__
    # qualname = cls.__qualname__ # __qualname__
    qualname = getattr(cls, "__qualname__", getattr(cls, "__name__", str(cls))) # fallback for PY2 and edge cases

    PY2 = sys.version_info[0] == 2
    if (
        not module or (PY2 and module=="__builtin__")
        or (module == "builtins")
    ):
        return qualname

    return f"{module}.{qualname}"

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
    find = False
    for i, line in enumerate(sourcelines):
        line = line.strip()
        # find main decorator
        if line.split("(")[0].strip() == "@" + decorator_name:
            find = True
            continue

        # find secondary decorator
        elif line.split("(")[0].strip().find("@") == 0:
            continue

        elif find is True:
            name = line.split("def")[1].split("(")[0].strip()
            res.append(name)
            find = False
    return res
