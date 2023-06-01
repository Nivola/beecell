# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte
import traceback

CODE_DBG_PORT = 5678


def init_pdb(port: int = CODE_DBG_PORT):
    import rpdb

    debugger = rpdb.Rpdb(port=port)
    debugger.set_trace()


def initialize_code_debugger():
    from os import getenv

    if getenv("DEBUG") == "True":
        import multiprocessing

        if multiprocessing.current_process().pid > 1:
            init_debugger()


def init_debugger():
    """initialze debugpy short way"""
    import debugpy

    debugpy.listen(("0.0.0.0", CODE_DBG_PORT))
    print("Debugger is ready to be attached, press F5", flush=True)
    debugpy.wait_for_client()
    print("debugger is now attached", flush=True)


def dbgprint(*args, **kwargs):
    import inspect

    callingframe = inspect.currentframe().f_back
    print(
        "|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||\n",
        inspect.getframeinfo(callingframe, context=1),
        callingframe.f_code.co_filename,
        callingframe.f_code.co_firstlineno,
        "DBG",
        callingframe.f_code.co_name,
        callingframe.f_lineno,
        callingframe.f_locals,
        sep=" | ",
    )

    def p(label, value):
        if isinstance(value, Exception):
            # Print exception information and stack trace entries from traceback object tb to file. This differs from print_tb() in the following ways:
            traceback.print_exception(value)
        else:
            print(label, type(value), value, sep=":")

    for arg in args:
        p("",arg)
    for k in kwargs.keys():
        p(k, kwargs[k])
        # print(k, type(kwargs[k]), kwargs[k], sep=":")
    print("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")
