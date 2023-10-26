# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

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
from six.moves import http_client
from six.moves.urllib.parse import urlparse
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

    def __parse_connection(self, conn_uri):
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
            self.logger.error("Error parsing connection %s: %s" % (conn_uri, ex))
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

    def run_http_request2(self, path, method, data="", headers={}, timeout=30):
        """Http client.
        Usage:

            res = http_client2('https', '/api', 'POST', port=443, data='', headers={})

        :param proto: Request proto. Ex. http, https
        :param host: Request host. Ex. 10.102.90.30
        :param port: Request port. [default=80]
        :param path: Request path. Ex. /api/
        :param method: Request method. Ex. GET, POST, PUT, DELETE
        :param headers: Request headers. [default={}]. Ex.
            {"Content-type": "application/x-www-form-urlencoded", Accept": "text/plain"}
        :param data: Request data. [default={}]. Ex.
            {'@number': 12524, '@type': 'issue', '@action': 'show'}
        :param timeout: Request timeout. [default=30s]
        :raise RemoteException:
        """
        try:
            path = self.conn["path"] + path
            proto = self.conn["proto"]
            host = self.conn["host"]
            if "port" not in self.conn:
                if proto == "http":
                    port = 80
                else:
                    port = 443
            else:
                port = self.conn["port"]

            # set simple authentication
            if self.user is not None:
                auth = base64.encodestring("%s:%s" % (self.user, self.pwd)).replace("\n", "")
                headers["Authorization"] = "Basic %s" % auth

            self.logger.info("Send http %s api request to %s://%s:%s%s" % (method, proto, host, port, path))
            if data.lower().find("password") < 0:
                self.logger.debug("Send [headers=%s] [data=%s]" % (headers, data))
            else:
                self.logger.debug("Send [headers=%s] [data=%s]" % (headers, "xxxxxxx"))

            _host = host
            _port = port
            _headers = headers
            if self.proxy is not None:
                _host = self.proxy[0]
                _port = self.proxy[1]
                _headers = {}
                path = "%s://%s:%s%s" % (proto, host, port, path)

            if proto == "http":
                conn = http_client.HTTPConnection(_host, _port, timeout=timeout)
            else:
                if self.keyfile is None:
                    # python >= 2.7.9
                    if version_info.major == 2 and version_info.minor == 7 and version_info.micro > 8:
                        ssl._create_default_https_context = ssl._create_unverified_context
                    # python < 2.7.8
                    elif version_info.major == 2 and version_info.minor == 7 and version_info.micro < 9:
                        ssl._create_default_https_context = create_urllib3_context(cert_reqs=ssl.CERT_NONE)
                    else:
                        ssl._create_default_https_context = None

                conn = http_client.HTTPSConnection(
                    _host,
                    _port,
                    timeout=timeout,
                    key_file=self.keyfile,
                    cert_file=self.certfile,
                )
            if self.proxy is not None:
                conn.set_tunnel(host, port=port, headers=headers)
                self.logger.debug("set proxy %s" % self.proxy)
                headers = None

            conn.request(method, path, data, _headers)
            response = conn.getresponse()
            content_type = response.getheader("content-type")
            self.logger.info("Response status: %s %s" % (response.status, response.reason))

        except http_client.HTTPException as ex:
            self.logger.error(ex, exc_info=True)
            raise BadRequestException(ex)
        except Exception as ex:
            self.logger.error(ex, exc_info=True)
            raise BadRequestException(ex)

        # evaluate response status
        # BAD_REQUEST     400     HTTP/1.1, RFC 2616, Section 10.4.1
        if response.status == 400:
            res = response.read()
            self.logger.error(
                "Response [content-type=%s] [data=%s]" % (content_type, truncate(res)),
                exc_info=True,
            )
            raise BadRequestException(res)

        # UNAUTHORIZED           401     HTTP/1.1, RFC 2616, Section 10.4.2
        elif response.status == 401:
            res = response.read()
            self.logger.error(
                "Response [content-type=%s] [data=%s]" % (content_type, truncate(res)),
                exc_info=True,
            )
            raise UnauthorizedException(res)

        # PAYMENT_REQUIRED       402     HTTP/1.1, RFC 2616, Section 10.4.3

        # FORBIDDEN              403     HTTP/1.1, RFC 2616, Section 10.4.4
        elif response.status == 403:
            res = response.read()
            self.logger.error(
                "Response [content-type=%s] [data=%s]" % (content_type, truncate(res)),
                exc_info=True,
            )
            raise ForbiddenException(res)

        # NOT_FOUND              404     HTTP/1.1, RFC 2616, Section 10.4.5
        elif response.status == 404:
            res = response.read()
            self.logger.error(
                "Response [content-type=%s] [data=%s]" % (content_type, truncate(res)),
                exc_info=True,
            )
            raise NotFoundException(res)

        # METHOD_NOT_ALLOWED     405     HTTP/1.1, RFC 2616, Section 10.4.6
        elif response.status == 405:
            res = response.read()
            self.logger.error(
                "Response [content-type=%s] [data=%s]" % (content_type, truncate(res)),
                exc_info=True,
            )
            raise MethodNotAllowedException(res)

        # NOT_ACCEPTABLE         406     HTTP/1.1, RFC 2616, Section 10.4.7
        elif response.status == 406:
            res = response.read()
            self.logger.error(
                "Response [content-type=%s] [data=%s]" % (content_type, truncate(res)),
                exc_info=True,
            )
            raise NotAcceptableException(res)

        # PROXY_AUTHENTICATION_REQUIRED     407     HTTP/1.1, RFC 2616, Section 10.4.8

        # REQUEST_TIMEOUT        408
        elif response.status == 408:
            self.logger.error("REQUEST_TIMEOUT - 408", exc_info=True)
            raise TimeoutException("Timeout")

        # CONFLICT               409
        elif response.status == 409:
            res = response.read()
            self.logger.error(
                "Response [content-type=%s] [data=%s]" % (content_type, truncate(res)),
                exc_info=True,
            )
            raise ConflictException(res)

        # UNSUPPORTED_MEDIA_TYPE 415
        elif response.status == 415:
            res = response.read()
            self.logger.error(
                "Response [content-type=%s] [data=%s]" % (content_type, truncate(res)),
                exc_info=True,
            )
            raise UnsupporteMediaTypeException(res)

        # INTERNAL SERVER ERROR  500
        elif response.status == 500:
            self.logger.error("SERVER_ERROR - 500", exc_info=True)
            raise ServerErrorException("Internal server error")

        # NO_CONTENT             204    HTTP/1.1, RFC 2616, Section 10.2.5
        elif response.status == 204:
            res = None
            conn.close()
            return res

        # OK                     200    HTTP/1.1, RFC 2616, Section 10.2.1
        # CREATED                201    HTTP/1.1, RFC 2616, Section 10.2.2
        # ACCEPTED               202    HTTP/1.1, RFC 2616, Section 10.2.3
        # NON_AUTHORITATIVE_INFORMATION    203    HTTP/1.1, RFC 2616, Section 10.2.4
        # RESET_CONTENT          205    HTTP/1.1, RFC 2616, Section 10.2.6
        # PARTIAL_CONTENT        206    HTTP/1.1, RFC 2616, Section 10.2.7
        # MULTI_STATUS           207    WEBDAV RFC 2518, Section 10.2
        elif re.match("20[0-9]+", str(response.status)):
            res = response.read()
            self.logger.debug("Response [content-type=%s] [data=%s]" % (content_type, truncate(res)))
            if content_type == "application/json":
                res_dict = json.loads(res)
                conn.close()
                return res_dict
            else:
                conn.close()
                return res

        return None
