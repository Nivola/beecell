# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2026 CSI-Piemonte

import socket
import os
import base64
import ssl
import re
from logging import getLogger
from sys import version_info
from paramiko import SSHClient, MissingHostKeyPolicy
import urllib3
from urllib3.util.ssl_ import create_urllib3_context
import http.client as http_client
from urllib.parse import urlparse
import ujson as json
from beecell.simple import truncate

urllib3.disable_warnings()


class RemoteException(Exception):
    def __init__(self, value, code=400):
        Exception.__init__(self, value)
        try:
            self.value = json.loads(value)
        except:
            self.value = value
        self.code = code

    def __str__(self):
        return "[%s] %s" % (self.code, self.value)


class BadRequestException(RemoteException):
    def __init__(self, value):
        RemoteException.__init__(self, value, 400)


class UnauthorizedException(RemoteException):
    def __init__(self, value):
        RemoteException.__init__(self, value, 401)


class ForbiddenException(RemoteException):
    def __init__(self, value):
        RemoteException.__init__(self, value, 403)


class NotFoundException(RemoteException):
    def __init__(self, value):
        RemoteException.__init__(self, value, 404)


class MethodNotAllowedException(RemoteException):
    def __init__(self, value):
        RemoteException.__init__(self, value, 405)


class NotAcceptableException(RemoteException):
    def __init__(self, value):
        RemoteException.__init__(self, value, 406)


class TimeoutException(RemoteException):
    def __init__(self, value):
        RemoteException.__init__(self, value, 408)


class ConflictException(RemoteException):
    def __init__(self, value):
        RemoteException.__init__(self, value, 409)


class UnsupporteMediaTypeException(RemoteException):
    def __init__(self, value):
        RemoteException.__init__(self, value, 415)


class ServerErrorException(RemoteException):
    def __init__(self, value):
        RemoteException.__init__(self, value, 500)


class RemoteClient(object):
    def __init__(self, conn, user=None, pwd=None, proxy=None, keyfile=None, certfile=None):
        """Create a Remote Client

        :param conn: Request connection.
            Ex. {'host':'10.102.90.30', 'port':22} for ssh request
            Ex. {'host':'10.102.90.30', 'port':80, 'path':'/api', 'proto':'http'}
            Ex. http://10.102.90.30:80/api
        :param proxy: proxy server. Ex. ('proxy.it', 3128) [default=None]
        """
        self.logger = getLogger(self.__class__.__module__ + "." + self.__class__.__name__)
        self.syspath = os.path.expanduser("~")
        self.conn = conn
        self.user = user
        self.pwd = pwd
        self.proxy = proxy

        self.keyfile = keyfile
        self.certfile = certfile

        if isinstance(conn, dict):
            self.conn = conn
        elif isinstance(conn, str):
            c = urlparse(conn)
            host, port = c.netloc.split(":")
            self.conn = {
                "proto": c.scheme,
                "host": host,
                "port": int(port),
                "path": c.path,
            }

    def __parse_connection(self, conn_uri: str):
        """Parse connection http://10.102.160.240:6060/path

        :param conn_uri: an uri like http://10.102.160.240:6060/path
        :return: dictionary with key-value result like {'proto':.., 'host':.., 'port':.., 'path':..}
        :rtype: dict
        """
        try:
            t1 = conn_uri.split("://")
            t2 = t1[1].split("/")
            t3 = t2[0].split(":")
            res = {"proto": t1[0], "host": t3[0], "port": int(t3[1]), "path": t3[1]}
            self.logger.debug("Get connection %s" % res)
        except Exception as ex:
            self.logger.error("Error parsing connection %s: %s", conn_uri, ex)
        return res

    def run_ssh_command(self, cmd, user, pwd, port=22):
        """Run remote command using ssh connection
        Paramiko 1.8 doesn't work with ECDSA key hashing algorithm. Ubuntu 12+ use ECDSA as default.
        To set RSA open /etc/ssh/sshd_config and comment row 'HostKey /etc/ssh/ssh_host_ecdsa_key', then
        restart ssh service

        :param cmd: command to run
        :param user: usename
        :param pwd: password
        :param port: port to connect [default=22]
        """
        try:
            client = SSHClient()
            client.set_missing_host_key_policy(MissingHostKeyPolicy())
            client.connect(
                self.conn.get("host"),
                self.conn.get("port", port),
                username=user,
                password=pwd,
                look_for_keys=False,
                compress=False,
            )
            stdin, stdout, stderr = client.exec_command(cmd)
            res = {"stdout": [], "stderr": stderr.read()}
            for line in stdout:
                res["stdout"].append(line.strip("\n"))
            client.close()
            return res
        except Exception as ex:
            raise RemoteException(ex)

    def run_tcp_command(self, cmd, port):
        """Run remote command using generic tcp socket connection"""
        try:
            response = []
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.conn, port))
            sock.sendall(cmd)
            response.append(sock.recv(1024))
            sock.close()
            return response
        except Exception as ex:
            raise RemoteException(ex)
