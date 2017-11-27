'''
Created on Nov 27, 2017

@author: darkbk
'''
from paramiko.client import SSHClient, MissingHostKeyPolicy
try:
    import interactive
except ImportError:
    from . import interactive

port = 22
user = u'root'
pwd = u'cs1$topix'
ipaddress = u'10.102.184.69'
# open ssh client
client = SSHClient()
client.set_missing_host_key_policy(MissingHostKeyPolicy())
client.connect(ipaddress, port, username=user, password=pwd,
    look_for_keys=False, compress=True)
#timeout=None, #allow_agent=True,

channel = client.get_transport().open_session()
channel.get_pty(term=u'vt100', width=0, height=0, 
            width_pixels=0, height_pixels=0)

channel.invoke_shell()
interactive.interactive_shell(channel)
client.close()