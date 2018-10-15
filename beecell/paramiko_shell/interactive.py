import datetime

from gevent.monkey import patch_all
#patch_all(os=True, select=True)

from logging import getLogger
import sys
from gevent import spawn, joinall, sleep, socket
from gevent.os import make_nonblocking, nb_read, nb_write
from paramiko.py3compat import u

from beecell.simple import format_date

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
    logger.info(u'Run shell to ssh channel: %s' % chan)
    old_stdin = termios.tcgetattr(sys.stdin.fileno())
    tty.setraw(sys.stdin.fileno())
    tty.setcbreak(sys.stdin.fileno())
    chan.settimeout(0.0)
    chan.setblocking(0)
    make_nonblocking(sys.stdin.fileno())

    def write_output():
        while chan.closed is False:
            if chan is not None:
                try:
                    if chan.recv_ready():
                        x = chan.recv(4096)
                        if log is True:
                            logger.info(u'OUT: %s' % x)
                        nb_write(sys.stdout.fileno(), x)
                except socket.timeout:
                    logger.error(u'', exc_info=1)
                except Exception:
                    logger.error(u'', exc_info=1)
                sleep(0.01)

    def get_input():
        cmd = u''
        while chan.closed is False:
            try:
                x = nb_read(sys.stdin.fileno(), 1)
                ordx = ord(x)

                if 31 < ordx < 127:
                    cmd += x
                if ordx in [8, 24, 127]:
                    cmd = cmd[:-1]
                if ordx == ord(u'\r'):
                    if trace is True:
                        logger.debug(u'Execute ssh command: %s' % cmd)
                        if trace_func is not None:
                            trace_func(status=None, cmd=cmd, elapsed=u'')

                    cmd = u''

                if log is True:
                    logger.debug(u'IN : %s' % x)
                if chan.send_ready():
                    chan.send(x)
            except socket.timeout:
                logger.error(u'', exc_info=1)
            except Exception:
                logger.error(u'', exc_info=1)
                break
            sleep(0.01)

    joinall([
        spawn(get_input),
        spawn(write_output)
    ])

    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_stdin)
    nb_write(sys.stdout.fileno(), u'\n')
    logger.info(u'Close shell to ssh channel: %s' % chan)


def windows_shell(chan, log, trace, trace_func):
    raise NotImplementedError()
