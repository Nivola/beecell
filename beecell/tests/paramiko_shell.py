# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

from beecell.paramiko_shell.shell import ParamikoShell
from beecell.tests.test_util import runtest
from beecell.tests.test_util import BeecellTestCase

tests = [
    u'test_run_with_password',
    u'test_run_with_keyfile',
    u'test_run_with_keystring'
]


class ShellTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

        self.port = self.conf(u'shell.port')
        self.user = self.conf(u'shell.user')
        self.pwd = self.conf(u'shell.pwd')
        self.host = self.conf(u'shell.host')
        self.keyfile = self.conf(u'shell.keyfile')
        self.key_string = u'\n'.join(self.conf(u'shell.key_string').split(u'\\n'))

    def tearDown(self):
        BeecellTestCase.tearDown(self)

    def test_run_with_password(self):
        self.client = ParamikoShell(self.host, self.user, pwd=self.pwd)
        res = self.client.cmd(u'ls', timeout=5.0)
        self.logger.info(res)

    def test_run_with_keyfile(self):
        self.client = ParamikoShell(self.host, self.user, keyfile=self.keyfile)
        res = self.client.cmd(u'ls', timeout=5.0)
        self.logger.info(res)

    def test_run_with_keystring(self):
        self.client = ParamikoShell(self.host, self.user, keystring=self.key_string)
        res = self.client.cmd(u'ls', timeout=5.0)
        self.logger.info(res)


if __name__ == u'__main__':
    runtest(ShellTestCase, tests)
