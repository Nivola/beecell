# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2022 CSI-Piemonte

from os import popen
from tempfile import NamedTemporaryFile
from paramiko.client import SSHClient, MissingHostKeyPolicy
from paramiko import RSAKey
from logging import getLogger
from six import StringIO, ensure_text, ensure_binary
import fcntl
import termios
import struct
import sys
from gevent.os import make_nonblocking, nb_read, nb_write
from sshtunnel import SSHTunnelForwarder

try:
    from scp import SCPClient
except:
    pass

try:
    import interactive
except ImportError:
    from . import interactive

logger = getLogger(__name__)


class ParamikoShell(object):
    def __init__(self, host, user, port=22, pwd=None, keyfile=None, keystring=None, pre_login=None, post_logout=None,
                 post_action=None, tunnel=None, **kwargs):
        self.pre_login = pre_login
        self.post_logout = post_logout
        self.post_action = post_action

        self.client = SSHClient()
        self.client.set_missing_host_key_policy(MissingHostKeyPolicy())

        self.timeout = 10.0
        self.host_user = user # user used to connect in the host
        self.keepalive = 30

        self.host = host
        self.user = user
        self.port = port
        self.pwd = pwd
        self.keyfile = keyfile
        self.tunnel_conf = tunnel
        self.tunnel = None

        if keystring is not None:
            key = ensure_text(keystring)
            keystring_io = StringIO(key)
            self.pkey = RSAKey.from_private_key(keystring_io)
            keystring_io.close()
        else:
            self.pkey = None

        if self.tunnel_conf is None:
            self.__create_client(**kwargs)

    def __create_client(self, **kwargs):
        if self.pre_login is not None:
            self.pre_login()
        try:
            host = kwargs.pop('host', self.host)
            port = kwargs.pop('port', self.port)
            self.client.connect(host, port, username=self.user, password=self.pwd, key_filename=self.keyfile,
                                pkey=self.pkey, look_for_keys=False, compress=True, timeout=self.timeout,
                                auth_timeout=self.timeout, banner_timeout=self.timeout, **kwargs)
        except Exception as ex:
            if self.post_logout is not None:
                self.post_logout(status=str(ex))
            raise

    def terminal_size(self):
        th, tw, hp, wp = struct.unpack('HHHH', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0)))
        return tw, th

    def __run(self):
        """Run interactive shell
        """
        tw, th = self.terminal_size()
        self.client.get_transport().set_keepalive(self.keepalive)
        channel = self.client.get_transport().open_session()
        channel.get_pty(term='xterm', width=tw, height=th, width_pixels=0, height_pixels=0)
        # channel.get_pty(term='xterm')
        channel.invoke_shell()
        interactive.interactive_shell(channel, log=False, trace=True, trace_func=self.post_action)
        channel.close()
        self.client.close()
        if self.post_logout is not None:
            self.post_logout()

    def close(self):
        self.client.close()

    def run(self):
        """Run interactive shell
        """
        if self.tunnel_conf is not None:
            self.create_tunnel()

        self.__run()

        if self.tunnel_conf is not None:
            self.close_tunnel()

    def create_tunnel(self):
        self.tunnel = SSHTunnelForwarder(
            logger=logger,
            ssh_address_or_host=(self.tunnel_conf.get('host'), self.tunnel_conf.get('port')),
            ssh_username=self.tunnel_conf.get('user'),
            ssh_password=self.tunnel_conf.get('pwd'),
            remote_bind_address=(self.host, 22),
        )
        self.tunnel.start()
        self.__create_client(port=self.tunnel.local_bind_port, host='127.0.0.1')

    def close_tunnel(self):
        self.tunnel.stop()

    def cmd1(self, cmd):
        from six import b, u, ensure_text
        try:
            import termios
            import tty
            has_termios = True
        except ImportError:
            has_termios = False

        channel = self.client.get_transport().open_session()
        channel.settimeout(5)
        channel.setblocking(1)
        send_ready = channel.send_ready()
        print(send_ready)
        while send_ready is False:
            send_ready = channel.send_ready()
            print(send_ready)
        channel.send(cmd)
        print(cmd)
        # while channel.closed is False:
        if channel.recv_ready():
            x = channel.recv(1024)
            print(x)
        channel.close()

        # old_stdin = termios.tcgetattr(sys.stdin.fileno())
        # tty.setraw(sys.stdin.fileno())
        # tty.setcbreak(sys.stdin.fileno())
        # channel.settimeout(0.0)
        # channel.setblocking(0)
        # make_nonblocking(sys.stdin.fileno())
        # termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_stdin)
        # # nb_write(sys.stdout.fileno(), b('\n'))
        # channel.send(cmd)
        #
        # if chan.recv_ready():
        #     x = chan.recv(1024)
        #     if log is True:
        #         logger.info('OUT: %s' % x)
        #     nb_write(sys.stdout.fileno(), x)

    def __cmd(self, cmd, timeout=1.0, **kwargs):
        """Execute command in shell
        """
        stdin, stdout, stderr = self.client.exec_command(cmd, timeout=timeout, **kwargs)
        res = {'stdout': [], 'stderr': ensure_text(stderr.read())}
        for line in stdout:
            res['stdout'].append(line.strip('\n'))
        # self.client.close()
        if self.post_action is not None:
            self.post_action(status=None, cmd=cmd, elapsed=0)
        if self.post_logout is not None:
            self.post_logout()
        return res

    def cmd(self, cmd, timeout=1.0, **kwargs):
        """Execute command in shell
        """
        if self.tunnel_conf is not None:
            self.create_tunnel()

        res = self.__cmd(cmd, timeout=timeout, **kwargs)

        if self.tunnel_conf is not None:
            self.close_tunnel()

        return res

    def mkdir(self, dirname):
        """Create e directory in remote server

        :param dirname: nameof the directory
        :return: True if all is ok
        """
        res = self.cmd('mkdir -p %s' % dirname, timeout=5.0)
        if res.get('stderr') != '':
            return False
        return True

    def chown(self, dirname, user='root', group='root'):
        """Change owner of a directory in remote server

        :param dirname: nameof the directory
        :param user: directory user owner
        :param group: directory group owner
        :return: True if all is ok
        """
        res = self.cmd('chown -R $(id -u %s):%s %s' % (user, group, dirname), timeout=5.0)
        # res = self.cmd('chown -R $(id -u %s) %s' % (user, dirname), timeout=5.0)
        if res.get('stderr') != '':
            return False
        return True

    def chmod(self, dirname, acl='700'):
        """Change acl of a directory in remote server

        :param dirname: nameof the directory
        :param acl: directory acl
        :return: True if all is ok
        """
        res = self.cmd('chmod -R %s %s' % (acl, dirname), timeout=5.0)
        if res.get('stderr') != '':
            return False
        return True

    def file_put(self, source, dest):
        """Put a local file to remote server

        :param source: local file name
        :param dest: remote file name
        :return:
        """
        ftp_client = self.client.open_sftp()
        res = ftp_client.put(source, dest)
        ftp_client.close()
        return res

    def file_get(self, source, dest):
        """Get a file from remote server

        :param source: remote file name
        :param dest: local file name
        :return:
        """
        ftp_client = self.client.open_sftp()
        res = ftp_client.get(source, dest)
        ftp_client.close()
        return res

    def file_list_dir(self, path):
        """Get the content of a directory on the remote server

        :param path: directory path
        :return:
        """
        ftp_client = self.client.open_sftp()
        res = ftp_client.listdir_attr(path)
        ftp_client.close()
        if self.post_action is not None:
            self.post_action(status=None, cmd='ls -al %s' % path, elapsed=0)
        if self.post_logout is not None:
            self.post_logout()
        return res

    def open_file(self, filename):
        """Get a file from remote server

        :param source: remote file name
        :param dest: local file name
        :return:
        """

        transport = self.client.get_transport()
        transport.set_keepalive(self.keepalive)
        channel = transport.open_session()
        channel.settimeout(self.timeout)

        cmd = 'tail -f %s' % filename
        channel.exec_command(cmd)

        make_nonblocking(sys.stdin.fileno())
        while channel.closed is False:
            if channel is not None:
                if channel.recv_ready():
                    x = channel.recv(4096)
                    nb_write(sys.stdout.fileno(), x)

        channel.close()
        self.client.close()

    def __scp_progress(self, filename, size, sent):
        """Define progress callback that prints the current percentage completed for the file"""
        status = float(sent) / float(size)
        newline = '\n'
        if status < 1:
            newline = '\r'
        sys.stdout.write('%s progress: %.2f%% %s' % (ensure_text(filename), status * 100, newline))

    def scp(self, local_package_path, remote_package_path):
        ssh = self.client
        with SCPClient(ssh.get_transport(), progress=self.__scp_progress) as scp:
            scp.put(local_package_path, recursive=True, remote_path=remote_package_path)


class Rsync(object):
    def __init__(self, user='root', pwd=None, keyfile=None, keystring=None, **kwargs):
        self.user = user
        self.pwd = pwd
        self.keystring = keystring
        self.cmd = None
        self.excludes = []
        self.fp = None

    def __create_temp_file(self, data):
        fp = NamedTemporaryFile()
        fp.write(ensure_binary(data))
        fp.seek(0)
        self.fp = fp

    def __close_temp_file(self):
        if self.fp is not None:
            self.fp.close()

    def __set_base_command(self):
        self.cmd = ['rsync -r --delete']
        if self.pwd is not None:
            rsh_cmd = '/usr/bin/sshpass -p {sshpass} ssh -o StrictHostKeyChecking=no -l {sshuser}'\
                .format(sshpass=self.pwd, sshuser=self.user)
            self.cmd.append("--rsh='{cmd}'".format(cmd=rsh_cmd))
        elif self.keystring is not None:
            self.__create_temp_file(self.keystring)
            rsh_cmd = 'ssh -o StrictHostKeyChecking=no -l {sshuser} -i {sshkey}'\
                .format(sshkey=self.fp.name, sshuser=self.user)
            self.cmd.append("--rsh='{cmd}'".format(cmd=rsh_cmd))

    def __get_plain_command(self, from_path, to_path):
        self.cmd.extend(self.excludes)
        self.cmd.append(from_path)
        self.cmd.append(to_path)
        cmd = ' '.join(self.cmd)
        return cmd

    def add_exclude(self, pattern):
        """add exclude file pattern

        :param pattern: file pattern. Ex. *.pyc or *.pyo
        :return:
        """
        self.excludes.append('--exclude={exclude}'.format(exclude=pattern))

    def run(self, from_path, to_path):
        """Sync local folder with remote folder using rsync protocol

        :param from_path: origin path. Ex. /tmp
        :param to_path: destination path. Ex. root@localhost:/tmp
        :return:
        """
        self.__set_base_command()
        cmd = self.__get_plain_command(from_path, to_path)
        stream = popen(cmd)
        output = stream.read()
        self.__close_temp_file()
        logger.debug('run rsync from {fp} to {tp}: {out}'.format(fp=from_path, tp=to_path, out=output))
        return output
