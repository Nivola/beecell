# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2024 CSI-Piemonte

import re
import sys
from logging import getLogger
from six import b, u, ensure_text
from gevent import spawn, joinall, sleep, socket
from gevent.os import make_nonblocking, nb_read, nb_write

logger = getLogger(__name__)

# windows does not have termios...
try:
    import termios
    import tty

    has_termios = True
except ImportError:
    has_termios = False


def interactive_shell(chan, log=False, trace=False, trace_func=None):
    if has_termios:
        posix_shell(chan, log, trace, trace_func)
    else:
        windows_shell(chan, log, trace, trace_func)


def posix_shell(chan, log, trace, trace_func):
    logger.info("Run shell to ssh channel: %s" % chan)
    old_stdin = termios.tcgetattr(sys.stdin.fileno())
    tty.setraw(sys.stdin.fileno())
    tty.setcbreak(sys.stdin.fileno())
    chan.settimeout(0.0)
    chan.setblocking(0)
    make_nonblocking(sys.stdin.fileno())

    KEYS = {
        "arrow-left": 8,
        "arrow-right": 7,
        "del": [27, 91, 75],
        "move": [27, 91, 67],
        "ctrl": [
            [27, 91, 49, 80],
            [27, 91, 50, 80],
            [27, 91, 51, 80],
            [27, 91, 52, 80],
            [27, 91, 53, 80],
            [27, 91, 54, 80],
        ],
    }

    def trace_cmd(cmd):
        if trace is True:
            # logger.debug('Execute ssh command: %s' % cmd)
            # import string
            # filtered_string = filter(lambda x: x in string.printable, cmd)
            logger.debug({"cmd": cmd})
            if trace_func is not None and len(cmd) > 0:
                spawn(trace_func, status=None, cmd=cmd, elapsed=0)
                # trace_func(status=None, cmd=cmd, elapsed=0)

    def string_parser(data):
        """List of ord(character)

        :param data
        :return:
        """
        # logger.warn('%s - %s' % (data, [chr(i) for i in data]))
        res = []
        pos = 0
        data_pos = 0
        max_data_pos = len(data)
        while data_pos < max_data_pos:
            item = data[data_pos]  # (ord, chr)
            if item == KEYS["arrow-left"]:
                if pos > 0:
                    pos -= 1
                data_pos += 1
            elif item == KEYS["arrow-right"]:
                pos += 1
                data_pos += 1
            elif data[data_pos : data_pos + 4] in KEYS["ctrl"]:
                res = res[0:pos]
                data_pos += 4
            elif data[data_pos : data_pos + 3] == KEYS["del"]:
                res = res[0:pos]
                data_pos += 3
            elif data[data_pos : data_pos + 3] == KEYS["move"]:
                pos += 1
                data_pos += 3
            elif 31 < item < 127:
                try:
                    res[pos] = chr(item)
                except:
                    res.append(chr(item))
                pos += 1
                data_pos += 1
            else:
                res = []
                pos = 0
                data_pos += 1
        res = "".join(res)
        # logger.debug(res)
        return res

    def write_output():
        cmd = ""
        while chan.closed is False:
            if chan is not None:
                try:
                    if chan.recv_ready():
                        x = chan.recv(1024)
                        if log is True:
                            logger.info("OUT: %s" % x)
                        nb_write(sys.stdout.fileno(), x)
                        cmd += ensure_text(x)

                        m = re.search(r"[\#\$]\s.*[\r\n]", cmd)
                        if m is not None:
                            cmd = cmd[-10:]
                            m.group(0)
                            data = m.group(0)
                            data = u(data.replace("# ", "").replace("$ ", "").rstrip())
                            data = string_parser([ord(i) for i in data])

                            if len(data) > 0:
                                trace_cmd(data)
                                cmd = ""
                except socket.timeout:
                    logger.error("", exc_info=True)
                except:
                    logger.error("", exc_info=True)
                sleep(0.005)
            if chan.exit_status_ready() is True:
                break

    def get_input():
        while chan.closed is False:
            if chan is not None:
                try:
                    x = nb_read(sys.stdin.fileno(), 1024)
                    if log is True:
                        logger.debug("IN : %s" % x)
                    if chan.send_ready():
                        chan.send(x)
                except socket.timeout:
                    logger.error("", exc_info=True)
                except Exception:
                    logger.error("", exc_info=True)
                    break
                sleep(0.005)
            if chan.exit_status_ready() is True:
                break

    joinall([spawn(get_input), spawn(write_output)])

    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_stdin)
    nb_write(sys.stdout.fileno(), b("\n"))
    logger.info("Close shell to ssh channel: %s" % chan)


def windows_shell(chan, log, trace, trace_func):
    raise NotImplementedError()
