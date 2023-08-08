# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte
import traceback
import os
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
    debugpy_enabled = True

    # if debugpy_enabled != None and debugpy_enabled and not bool(uwsgi_util.opt.get("master", False)):
    if os.environ.get("DEBUG_ENABLED")== "YES":
        import sys
        import time
        import threading
        import yaml

        ####################################
        # TODO valutare se spostare su un configmap con un file YAML
        ####################################
        debugpy_yaml = yaml.safe_load(
            """
            debugpy:
              enabled: true
              subsystems:
                - name: auth
                  port: 5678
                  timeout_connection: 60
                - name: service
                  port: 5679
                  timeout_connection: 120
                - name: resource
                  port: 5680
                  timeout_connection: 120
            """
        )
        debugpy_opt = debugpy_yaml.get("debugpy", {})
        if bool(debugpy_opt.get("enabled", False)) and debugpy_opt.get("subsystems", None) != None:
            # 1-ENABLE GEVENT SUPPORT
            os.environ["GEVENT_SUPPORT"] = "True"
            # 2-GET POD NAME
            hostname = os.environ["HOSTNAME"]
            for subsystem in debugpy_opt["subsystems"]:
                # 3- IS SUBSYSTEM ENABLED FOR LOGGING?
                if (
                    subsystem != None
                    and hostname != None
                    and subsystem.get("name", None) != None
                    and subsystem.get("port", None) != None
                    and f'uwsgi-{subsystem["name"]}' in hostname
                ):
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
                        debugpy.listen(("0.0.0.0", subsystem["port"]))
                        debugpy_logger.debug("🐞⚡️debugpy⚡️ ❱❱❱ Listening at 0.0.0.0:%s 🤔 ❌", subsystem["port"])
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

if os.environ.get("DEBUG_ENABLED")== "YES":
    debug_cmp()