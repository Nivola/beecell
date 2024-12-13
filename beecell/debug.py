# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2024 CSI-Piemonte
import traceback
import os
import sys
import logging

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


def debug_cmp():
    """Check configurations for debugging and enable debug if needed"""
    # debugpy_enabled = uwsgi_util.opt.get("debugpy_enabled", None)

    debugpy_uwsgi = os.environ.get("DEBUG_UWSGI", "NO") == "YES"
    debugpy_worker = os.environ.get("DEBUG_WORKER", "NO") == "YES"
    debugpy_enabled = debugpy_uwsgi or debugpy_worker
    ####################################
    # if debugpy_enabled != None and debugpy_enabled and not bool(uwsgi_util.opt.get("master", False)):
    if debugpy_enabled:
        dbgport: int = int(os.environ.get("DEBUG_PORT", 5680))
        dbgtimeout: int = int(os.environ.get("DEBUG_TIMEOUT", 120))
        # 1-ENABLE GEVENT SUPPORT
        os.environ["GEVENT_SUPPORT"] = "True"
        # 2-GET POD NAME
        hostname = os.environ["HOSTNAME"]
        try:
            # 4- SETUP A LOGGER FOR DEBUGPY
            debugpy_logger = logging.getLogger("debugpy")
            debugpy_logger.setLevel(logging.DEBUG)
            stdout_handler = logging.StreamHandler(sys.stdout)
            debugpy_logger.addHandler(stdout_handler)
            # 5- IMPORTING MODULE
            debugpy_logger.debug("🐞⚡️debugpy⚡️ ❱❱❱ - Importing module...")
            import debugpy

            debugpy_logger.debug("🐞⚡️debugpy⚡️ ❱❱❱ debugging mode ENABLED for POD %s", hostname)
            debugpy.listen(("0.0.0.0", dbgport))
            debugpy_logger.debug("🐞⚡️debugpy⚡️ ❱❱❱ Listening at 0.0.0.0:%s 🤔 ❌", dbgport)
            # 6- TASK TIME FOR WAITING CLIENT TO CONNECT
            # debugpy.wait_for_client()
            # class T(threading.Thread):
            #     def run(self):
            #         timeout = subsystem.get('timeout_connection', '120')
            #         time.sleep(float(timeout))
            #         debugpy_logger.debug("🐞⚡️debugpy⚡️ ❱❱❱ Cancelling debug wait task after %s sec of waiting client to connect ❌", timeout)
            #         debugpy.wait_for_client.cancel()
            # T().start()
            debugpy_logger.debug("🐞⚡️debugpy⚡️ ❱❱❱ Debugger Client Connected 🤓 ✅")
        except RuntimeError:
            debugpy_logger.error("🐞⚡️debugpy⚡️ ❱❱❱ - Got Runtime error.")


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
            print("exception", type(value), value, sep=":")
            traceback.print_exc()
        else:
            print(label, type(value), value, sep=":")

    for arg in args:
        p("", arg)
    for k in kwargs.keys():
        p(k, kwargs[k])
        # print(k, type(kwargs[k]), kwargs[k], sep=":")
    print("||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||")


if os.environ.get("DEBUG_ENABLED") == "YES":
    debug_cmp()
