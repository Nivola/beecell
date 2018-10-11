"""
Created on Jan 19, 2018

@author: darkbk
"""
from paramiko.client import SSHClient, MissingHostKeyPolicy
from paramiko import RSAKey
from logging import getLogger
import StringIO
import fcntl
import termios
import struct

try:
    import interactive
except ImportError:
    from . import interactive

logger = getLogger(__name__)


class ParamikoShell(object):
    def __init__(self, host, user, port=22, pwd=None, keyfile=None, keystring=None, pre_login=None, post_logout=None,
                 post_action=None):
        self.post_logout = post_logout
        self.post_action = post_action

        self.client = SSHClient()
        self.client.set_missing_host_key_policy(MissingHostKeyPolicy())

        self.timeout = 1.0
        self.host_user = user # user used to connect in the host

        if keystring is not None:
            keystring_io = StringIO.StringIO(keystring)
            pkey = RSAKey.from_private_key(keystring_io)
            keystring_io.close()
        else:
            pkey = None

        if pre_login is not None:
            pre_login()
        try:
            self.client.connect(host, port, username=user, password=pwd, key_filename=keyfile, pkey=pkey,
                                look_for_keys=False, compress=True, timeout=self.timeout, auth_timeout=self.timeout,
                                banner_timeout=self.timeout)
        except Exception as ex:
            if self.post_logout is not None:
                self.post_logout(status=str(ex))
            raise
        # timeout=None, #allow_agent=True,

    def terminal_size(self):
        th, tw, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack(u'HHHH', 0, 0, 0, 0)))
        return tw, th

    def run(self):
        """Run interactive shell
        """
        tw, th = self.terminal_size()
        channel = self.client.get_transport().open_session()
        channel.get_pty(term=u'xterm', width=tw, height=th, width_pixels=0, height_pixels=0)
        # channel.get_pty(term=u'xterm')
        channel.invoke_shell()
        interactive.interactive_shell(channel, log=False, trace=True, trace_func=self.post_action)
        channel.close()
        self.client.close()
        if self.post_logout is not None:
            self.post_logout()

    def cmd(self, cmd, timeout=1.0):
        """Execute command in shell
        """
        stdin, stdout, stderr = self.client.exec_command(cmd, timeout=timeout)
        res = {u'stdout': [], u'stderr': stderr.read()}
        for line in stdout:
            res[u'stdout'].append(line.strip(u'\n'))
        self.client.close()
        if self.post_action is not None:
            self.post_action(cmd=cmd, elapsed=0)
        if self.post_logout is not None:
            self.post_logout()
        return res
