# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

import time
import logging
import multiprocessing
import threading
from beecell.uwsgi_sys.wrapper import uwsgi_util

def watch(func):
    """Decorator function used to capture elapsed time.
    Configure 'watch' logger to save data."""
    def inner(*args, **kwargs): #1
        # get start time
        start = time.time()
        # get runtime info
        cp = multiprocessing.current_process()
        ct = threading.current_thread()
        uw_pid = uwsgi_util.worker_id()
        uw_mid = uwsgi_util.mule_id()
        uw_rid = uwsgi_util.request_id()
        # execute inner function
        ret = func(*args, **kwargs) #2
        # calculate elasped time
        elapsed = round(time.time() - start, 5)
        # log execution info in watch logger 
        info = "%s:%s - %s %s %s - %s:%s - %s" % (
            cp.ident, ct.ident, uw_pid, uw_mid, uw_rid,
            func.__module__, func.func_name, elapsed)
        # log info in runtime logger
        logging.getLogger('gibbon.util.watch').info(info)
        return ret
    return inner