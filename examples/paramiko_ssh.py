'''
Created on Nov 27, 2017

from : https://daanlenaerts.com/blog/2016/07/01/python-and-ssh-paramiko-shell/

@author: darkbk
'''
import threading, paramiko
 
class Ssh:
    shell = None
    client = None
    transport = None
 
    def __init__(self, address, username, password):
        print("Connecting to server on ip", str(address) + ".")
        self.client = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
        self.client.connect(address, username=username, password=password, look_for_keys=False)
        self.transport = paramiko.Transport((address, 22))
        self.transport.connect(username=username, password=password)
 
        thread = threading.Thread(target=self.process)
        thread.daemon = True
        thread.start()
 
    def closeConnection(self):
        if(self.client != None):
            self.client.close()
            self.transport.close()
 
    def openShell(self):
        self.shell = self.client.invoke_shell()
 
    def sendShell(self, command):
        if(self.shell):
            self.shell.send(command + "\n")
        else:
            print("Shell not opened.")
 
    def process(self):
        global connection
        while True:
            # Print data when available
            if self.shell != None and self.shell.recv_ready():
                alldata = self.shell.recv(1024)
                while self.shell.recv_ready():
                    alldata += self.shell.recv(1024)
                strdata = str(alldata)#, "utf8")
                strdata.replace('\r', '')
                print(strdata)#, end = "")
                if(strdata.endswith("$ ")):
                    print("\n$ ")#, end = "")
 
 
sshUsername = "root"
sshPassword = ""
sshServer = "10.102.184.69"

connection = Ssh(sshServer, sshUsername, sshPassword)
connection.openShell()
while True:
    command = input('$ ')
    if command.startswith(" "):
        command = command[1:]
    connection.sendShell(command)