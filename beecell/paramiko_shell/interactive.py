import datetime
import string

from gevent.local import local
from gevent.monkey import patch_all
#patch_all(os=True, select=True)

from logging import getLogger
import sys
from gevent import spawn, joinall, sleep, socket, queue
from gevent.os import make_nonblocking, nb_read, nb_write
from gevent.queue import Empty
import re
import string

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

    KEYS = {
        u'arrow-left': 8,
        u'arrow-right': 7,
        u'del': [27, 91, 75],
        u'move': [27, 91, 67],
        u'ctrl': [[27, 91, 49, 80], [27, 91, 50, 80], [27, 91, 51, 80], [27, 91, 52, 80], [27, 91, 53, 80],
                  [27, 91, 54, 80]]

    }

    def trace_cmd(cmd):
        if trace is True:
            # logger.debug(u'Execute ssh command: %s' % cmd)
            # import string
            # filtered_string = filter(lambda x: x in string.printable, cmd)
            logger.debug({u'cmd': cmd})
            if trace_func is not None and len(cmd) > 0:
               trace_func(status=None, cmd=cmd, elapsed=0)

    def string_parser(data):
        """List of ord(character)

        :param data
        :return:
        """
        # logger.warn(u'%s - %s' % (data, [chr(i) for i in data]))
        res = []
        pos = 0
        data_pos = 0
        max_data_pos = len(data)
        while data_pos < max_data_pos:
            item = data[data_pos] # (ord, chr)
            if item == KEYS[u'arrow-left']:
                if pos > 0:
                    pos -= 1
                data_pos += 1
            elif item == KEYS[u'arrow-right']:
                pos += 1
                data_pos += 1
            elif data[data_pos:data_pos+4] in KEYS[u'ctrl']:
                res = res[0:pos]
                data_pos += 4
            elif data[data_pos:data_pos+3] == KEYS[u'del']:
                res = res[0:pos]
                data_pos += 3
            elif data[data_pos:data_pos+3] == KEYS[u'move']:
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
        res = u''.join(res)
        # logger.debug(res)
        return res

    def write_output():
        cmd = u''
        while chan.closed is False:
            if chan is not None:
                try:
                    if chan.recv_ready():
                        x = chan.recv(4096)
                        if log is True:
                            logger.info(u'OUT: %s' % x)
                        nb_write(sys.stdout.fileno(), x)
                        cmd += x
                        # cmd = filter(lambda x: x in string.printable, cmd)

                        # logger.warn(cmd)
                        m = re.search(r'[\#\$]\s.*[\r\n]', cmd)
                        if m is not None:
                            cmd = cmd[-10:]
                            m.group(0)
                            data = m.group(0)
                            data = unicode(data.replace(u'# ', u'').replace(u'$ ', u'').rstrip())
                            # logger.warn({u'p': data})
                            # logger.warn([ord(i) for i in data])
                            data = string_parser([ord(i) for i in data])
                            if len(data) > 0:
                                trace_cmd(data)
                            # data = unicode(data.replace(u'# ', u'').replace(u'$ ', u'').rstrip())
                            # # if len(data) > 0:
                            # logger.warn([(ord(i), i) for i in data])
                            # # for c in data:
                            # #     c = ord(c)
                            # #     if 31 < c < 127:
                            # #         print_cmd = True
                            # #     else:
                            # #         logger.warn(c)
                            # if print_cmd is True:
                            #     # data = data.encode(u'utf-8')
                            #     trace_cmd(data)
                            #     # print_cmd = False
                            # cmd = cmd[-10:]
                except socket.timeout:
                    logger.error(u'', exc_info=1)
                except Exception:
                    logger.error(u'', exc_info=1)
                sleep(0.01)

    def get_input():
        cmd = u''
        cmd_ord = []
        while chan.closed is False:
            try:
                x = nb_read(sys.stdin.fileno(), 1)
                ordx = ord(x)
                cmd_ord.append(ordx)
                # logger.warn(u'%s - %s' % (ordx, cmd))

                # # end of line
                # if ordx == 13:
                #     # cmd_ord.pop()
                #     # cmd = u''.join([chr(d) for d in cmd_ord])
                #     trace_cmd(cmd)
                #     cmd_ord = []
                #     logger.warn(cmd)
                #     cmd = u''
                #
                # # del char
                # elif ordx == 127:
                #     cmd = cmd[:-1]
                #
                # # add new char
                # elif 31 < ordx < 127:
                #     cmd += x
                #
                # # bash_completion
                # if cmd.find(u'[A') >= 0 or cmd.find(u'[B') >= 0 :
                #     cmd = u''
                #     bash_completion.put(True)
                #
                # # remove char
                # if cmd.find(u'[D') >= 0 or cmd.find(u'[C') >= 0 :
                #     cmd = cmd[:-2]

                # single char that should be removed
                # elif ordx <= 31 or ordx >= 127:
                #     cmd_ord.pop()

                # # select command from history
                # elif CMDS[u'arrow-up'] in cmd_ord or CMDS[u'arrow-down'] in cmd_ord:
                #     cmd = u''
                #     # logger.warn(u'in')
                #     # ordx = None
                #     # cmd = u''
                #     cmd_ord = []
                #     bash_completion.put(True)

                # # char sequence that should be removed
                # elif check_cmd(cmd_ord):
                #     # ordx = None
                #     # cmd = u''
                #     cmd_ord = clean_cmd(cmd_ord)

                # # single char that should be removed
                # elif ordx <= 31 or ordx >= 127:
                #     cmd_ord.pop()

                # elif 31 < ordx < 127:
                #     cmd += x
                # # if ordx in [8, 24, 127]:
                # elif ordx <= 31 or ordx >= 127:
                #     cmd = cmd[:-1]
                #     cmd_ord.pop()

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
