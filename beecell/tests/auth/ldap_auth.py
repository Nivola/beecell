# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

from beecell.auth import LdapAuth, SystemUser
from beecell.tests.test_util import BeecellTestCase, runtest

tests = [
    u'test_login_ldap',
    u'test_login_ad_ldap'
]


class LdapAuthTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

    def tearDown(self):
        BeecellTestCase.tearDown(self)

    def test_login_ldap(self):
        self.auth_provider = LdapAuth(self.conf(u'ldap.host'), SystemUser,
                                      port=self.conf(u'ldap.port'), timeout=self.conf(u'ldap.timeout'),
                                      ssl=self.conf(u'ldap.ssl'), dn=self.conf(u'ldap.dn'),
                                      search_filter=self.conf(u'ldap.search_filter'),
                                      search_id=self.conf(u'ldap.search_id'),
                                      bind_user=self.conf(u'ldap.bind_user'), bind_pwd=self.conf(u'ldap.bind_pwd'))
        user = self.auth_provider.login(self.conf(u'ldap.user'), self.conf(u'ldap.pwd'))
        self.logger.debug(user.get_groups())
        for k, v in user.get_attributes().items():
            self.logger.debug(u'%s: %s' % (k, str(v).decode(errors=u'ignore')))

    def test_login_ad_ldap(self):
        self.auth_provider = LdapAuth(self.conf(u'ldap_ad.host'), SystemUser,
                                      port=self.conf(u'ldap_ad.port'), timeout=self.conf(u'ldap_ad.timeout'),
                                      ssl=self.conf(u'ldap_ad.ssl'), dn=self.conf(u'ldap_ad.dn'),
                                      search_filter=self.conf(u'ldap_ad.search_filter'),
                                      search_id=self.conf(u'ldap_ad.search_id'),
                                      bind_user=self.conf(u'ldap_ad.bind_user'), bind_pwd=self.conf(u'ldap_ad.bind_pwd'))
        user = self.auth_provider.login(self.conf(u'ldap_ad.user'), self.conf(u'ldap_ad.pwd'))
        self.logger.debug(user.get_groups())
        for k, v in user.get_attributes().items():
            self.logger.debug(u'%s: %s' % (k, str(v).decode(errors=u'ignore')))


if __name__ == u'__main__':
    runtest(LdapAuthTestCase, tests)
