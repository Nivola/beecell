from gevent.monkey import patch_all
patch_all(os=True, select=True)

from logging import getLogger
import sys
from gevent import spawn, joinall, sleep, socket
from gevent.os import make_nonblocking, nb_read, nb_write
from paramiko.py3compat import u


logger = getLogger(__name__)

# windows does not have termios...
try:
    import termios
    import tty
    has_termios = True
except ImportError:
    has_termios = False


def interactive_shell(chan, log=False):
    if has_termios:
        posix_shell(chan, log)
    else:
        windows_shell(chan, log)


def posix_shell(chan, log):
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
                        x = u(chan.recv(4096))
                        if log is True:
                            logger.debug(u'OUT: %s' % x)
                        # if len(x) == 0:
                        #     nb_write(sys.stdout.fileno(), "\r\n*** EOF\r\n")
                        #     #sys.stdout.write("\r\n*** EOF\r\n")
                        #     break
                        nb_write(sys.stdout.fileno(), x)
                    #sys.stdout.write(x)
                    #sys.stdout.flush()
                except socket.timeout:
                    logger.error(u'', exc_info=1)
                sleep(0.01)

    def get_input():
        while chan.closed is False:
            try:
                x = nb_read(sys.stdin.fileno(), 1024)
                if log is True:
                    logger.debug(u'IN : %s' % x)
                chan.send(x)
            except socket.timeout:
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


def windows_shell(chan, log):
    raise NotImplementedError()