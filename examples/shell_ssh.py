'''
Created on Nov 27, 2017

@author: darkbk
'''
from sh import ssh
import sys

# paramiko 2.4
# install python-gssapi

aggregated = ""
def ssh_interact(char, stdin):
    global aggregated
    print(u'pppp')
    sys.stdout.write(char.encode())
    sys.stdout.flush()
    aggregated += char
    #if aggregated.endswith("password: "):
    #    stdin.put("correcthorsebatterystaple\n")

ssh("root@10.102.184.69", _out=ssh_interact, _out_bufsize=0, _tty_in=True)