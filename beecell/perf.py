# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

from time import time
import logging
from multiprocessing import current_process
from threading import current_thread
from functools import wraps
from beecell.simple import id_gen, get_member_class, nround


def mem_usage(factor=1048576):
    """Memory usage

    Vss = virtual set size
    Rss = resident set size
    Pss = proportional set size
    Uss = unique set size

    Uss is the set of pages that are unique to a process. This is the amount of memory that would be freed if
    the application was terminated right now.
    Pss is the amount of memory shared with other processes, accounted in a way that the amount is divided evenly between
    the processes that share it. This is memory that would not be released if the process was terminated, but is indicative
    of the amount that this process is "contributing"

    :return: pfullmem(rss=10199040, vms=52133888, shared=3887104, text=2867200, lib=0, data=5967872, dirty=0,
                      uss=6545408, pss=6872064, swap=0)
    """
    from psutil import Process
    from os import getpid

    p = Process(getpid())
    mem = p.memory_full_info()

    format = lambda x: round(x / factor, 1)

    data = {
        "rss": format(mem.rss),
        "vms": format(mem.vms),
        "shared": format(mem.shared),
        "text": format(mem.text),
        "data": format(mem.data),
        "lib": format(mem.lib),
        "dirty": format(mem.dirty),
        "uss": format(mem.uss),
        "pss": format(mem.pss),
        "swap": format(mem.swap),
    }
    print(data)
    return data


def usage(func):
    """Decorator function used to capture process usage. To print result set handler for logger beecell.usage"""

    @wraps(func)
    def inner(*args, **kwargs):
        logger = logging.getLogger("beecell.usage")

        from psutil import Process
        from os import getpid

        p = Process(getpid())

        res = func(*args, **kwargs)

        mem = p.memory_info()
        rss = mem.rss / 1048576
        vms = mem.vms / 1048576
        shared = mem.shared / 1048576
        text = mem.text / 1048576
        data = mem.data / 1048576
        lib = mem.lib / 1048576
        dirty = mem.dirty / 1048576
        tot = rss + vms + shared + text + data + lib + dirty
        items = {
            "rss": {
                "desc": "Resident Set Size - this is the non-swapped physical memory a process has used",
                "value": rss,
            },
            "vms": {
                "desc": "Virtual Memory Size - this is the total amount of virtual memory used by the process",
                "value": vms,
            },
            "shared": {
                "desc": "Memory that could be potentially shared with other processes",
                "value": shared,
            },
            "text": {
                "desc": "TRS (text resident set) the amount of memory devoted to executable code",
                "value": text,
            },
            "data": {
                "desc": "DRS (data resident set) the amount of physical memory devoted to other than executable "
                "code",
                "value": data,
            },
            "lib": {"desc": "The memory used by shared libraries", "value": lib},
            "dirty": {"desc": "The number of dirty pages", "value": dirty},
            "tot": {"desc": "Total memory", "value": tot},
        }
        logger.info("--- Memory usage ---")

        for k, v in items.items():
            logger.info("%8s %10sMB %s" % (k, round(v["value"], 3), v["desc"]))

        return res

    return inner


def watch(func):
    """Decorator function used to capture elapsed time. Configure 'watch' logger to save data."""

    @wraps(func)
    def inner(*args, **kwargs):  # 1
        logger = logging.getLogger(__name__)

        # get runtime info
        cp = current_process()
        ct = current_thread()

        # generate unique task id
        task_id = id_gen()

        # log start
        # classname = get_method_class(func)
        info = "%s:%s - %s - START -  %s:%s" % (
            cp.ident,
            ct.ident,
            task_id,
            func.__module__ + "." + get_member_class(args),
            func.__name__,
        )
        # logger.info(info)

        # get start time
        start = time()

        # execute inner function
        ret = func(*args, **kwargs)  # 2

        # calculate elasped time
        elapsed = round(time() - start, 5)

        # log execution info in watch logger
        info = "%s:%s - %s - STOP  -  %s:%s - %s" % (
            cp.ident,
            ct.ident,
            task_id,
            func.__module__ + "." + get_member_class(args),
            func.__name__,
            elapsed,
        )

        # logger.info(info)
        return ret

    return inner


def watch_test(func):
    """Decorator function used to capture elapsed time. Configure 'test' logger to save data."""

    @wraps(func)
    def inner(*args, **kwargs):  # 1
        logging.getLogger("beecell.test").info("========== %s ==========" % (func.func_name))
        start = time()
        ret = func(*args, **kwargs)  # 2
        elapsed = nround(time() - start, 4)
        logging.getLogger("beecell.test").info("========== %s ========== : %ss\n" % (func.func_name, elapsed))
        return ret

    return inner


class Timer(object):
    """Simple class to use when you need to measure elapsed time"""

    startTime = 0

    def __init__(self):
        self.startTime = time()

    def restart(self):
        self.startTime = time()

    def elapsed(self):
        temp = time()
        stop = temp - self.startTime
        self.startTime = temp
        return stop

    def print_elapsed(self, message):
        elapsed = self.elapsed()
        print("%s - %s s" % (message, elapsed))
