# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte
import logging

from beecell.logger import LoggerHelper
from beecell.paramiko_shell.shell import ParamikoShell
from beecell.tests.test_util import runtest
from beecell.tests.test_util import BeecellTestCase
from beecell.paramiko_shell.shell import logger

tests = [
    'test_run_tunnel_with_password',
    # 'test_run_with_password',
    # 'test_run_with_keyfile',
    # 'test_run_with_keystring'
]


class ShellTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

        self.port = self.conf('shell.port')
        self.user = self.conf('shell.user')
        self.pwd = self.conf('shell.pwd')
        self.host = self.conf('shell.host')
        self.keyfile = self.conf('shell.keyfile')
        self.key_string = '\n'.join(self.conf('shell.key_string').split('\\n'))

        self.port = 22
        self.user = 'root'
        self.pwd = '.00y._BH'
        self.host = '192.168.201.12'

        self.tunnel = {'host': '84.240.174.190', 'port': 11100, 'user': 'gateway', 'pwd': 'MoqJZWfHEApOqh2NeLJD'}
        LoggerHelper.simple_handler([logger, logging.getLogger('paramiko')], logging.DEBUG)

    def tearDown(self):
        BeecellTestCase.tearDown(self)

    def test_run_tunnel_with_password(self):
        self.client = ParamikoShell(self.host, self.user, pwd=self.pwd, tunnel=self.tunnel)
        self.client.create_tunnel()
        res = self.client.cmd('ls', timeout=5.0)
        self.logger.info(res)
        self.client.close_tunnel()

    def test_run_with_password(self):
        self.client = ParamikoShell(self.host, self.user, pwd=self.pwd)
        res = self.client.cmd('ls', timeout=5.0)
        self.logger.info(res)

    def test_run_with_keyfile(self):
        self.client = ParamikoShell(self.host, self.user, keyfile=self.keyfile)
        res = self.client.cmd('ls', timeout=5.0)
        self.logger.info(res)

    def test_run_with_keystring(self):
        self.client = ParamikoShell(self.host, self.user, keystring=self.key_string)
        res = self.client.cmd('ls', timeout=5.0)
        self.logger.info(res)


if __name__ == '__main__':
    runtest(ShellTestCase, tests)
