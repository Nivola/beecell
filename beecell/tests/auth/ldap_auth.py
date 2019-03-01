# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

from beecell.auth import LdapAuth, SystemUser
from beecell.tests.test_util import BeecellTestCase, runtest

tests = [
    u'test_login'
]


class LdapAuthTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

        self.auth_provider = LdapAuth(self.conf(u'ldap.host'), self.conf(u'ldap.domain'), SystemUser,
                                      port=self.conf(u'ldap.port'), timeout=self.conf(u'ldap.timeout'),
                                      ssl=self.conf(u'ldap.ssl'), dn=self.conf(u'ldap.dn'))
        self.user = self.conf(u'ldap.user')
        self.password = self.conf(u'ldap.pwd')

    def tearDown(self):
        BeecellTestCase.tearDown(self)

    def test_login(self):
        user = self.auth_provider.login(self.user, self.password)
        self.logger.debug(user.get_groups())
        for k, v in user.get_attributes().items():
            self.logger.debug(u'%s: %s' % (k, str(v).decode(errors=u'ignore')))


if __name__ == u'__main__':
    runtest(LdapAuthTestCase, tests)
