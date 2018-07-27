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
    def __init__(self, host, user, port=22, pwd=None, keyfile=None, keystring=None, pre_login=None, post_logout=None):
        self.post_logout = post_logout

        self.client = SSHClient()
        self.client.set_missing_host_key_policy(MissingHostKeyPolicy())

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
                                look_for_keys=False, compress=True)
        except Exception as ex:
            if self.post_logout is not None:
                self.post_logout(str(ex))
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
        interactive.interactive_shell(channel)
        channel.close()
        self.client.close()
        if self.post_logout is not None:
            self.post_logout(u'OK')
