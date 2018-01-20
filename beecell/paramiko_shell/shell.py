"""
Created on Jan 19, 2018

@author: darkbk
"""
from paramiko.client import SSHClient, MissingHostKeyPolicy
from paramiko import RSAKey
from logging import getLogger
import StringIO

try:
    import interactive
except ImportError:
    from . import interactive

logger = getLogger(__name__)


class ParamikoShell(object):
    def __init__(self, host, user, port=22, pwd=None, keyfile=None, keystring=None):
        self.client = SSHClient()
        self.client.set_missing_host_key_policy(MissingHostKeyPolicy())

        if keystring is not None:
            keystring_io = StringIO.StringIO(keystring)
            pkey = RSAKey.from_private_key(keystring_io)
            keystring_io.close()
        else:
            pkey = None

        self.client.connect(host, port, username=user, password=pwd, key_filename=keyfile, pkey=pkey,
                            look_for_keys=False, compress=True)
        # timeout=None, #allow_agent=True,

    def run(self):
        """Run interactive shell
        """
        channel = self.client.get_transport().open_session()
        channel.get_pty(term=u'vt100', width=0, height=0, width_pixels=0, height_pixels=0)
        channel.invoke_shell()
        interactive.interactive_shell(channel)
        self.client.close()
