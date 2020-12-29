# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte
# (C) Copyright 2020-2021 CSI-Piemonte

from beecell.auth import LdapAuth, SystemUser
from beecell.tests.test_util import BeecellTestCase, runtest

tests = [
    'test_login_ldap',
    'test_login_ad_ldap'
]


class LdapAuthTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

    def tearDown(self):
        BeecellTestCase.tearDown(self)

    def test_login_ldap(self):
        self.auth_provider = LdapAuth(self.conf('ldap.host'), SystemUser,
                                      port=self.conf('ldap.port'), timeout=self.conf('ldap.timeout'),
                                      ssl=self.conf('ldap.ssl'), dn=self.conf('ldap.dn'),
                                      search_filter=self.conf('ldap.search_filter'),
                                      search_id=self.conf('ldap.search_id'),
                                      bind_user=self.conf('ldap.bind_user'), bind_pwd=self.conf('ldap.bind_pwd'))
        user = self.auth_provider.login(self.conf('ldap.user'), self.conf('ldap.pwd'))
        self.logger.debug(user.get_groups())
        for k, v in user.get_attributes().items():
            self.logger.debug('%s: %s' % (k, v))

    def test_login_ad_ldap(self):
        self.auth_provider = LdapAuth(self.conf('ldap_ad.host'), SystemUser,
                                      port=self.conf('ldap_ad.port'), timeout=self.conf('ldap_ad.timeout'),
                                      ssl=self.conf('ldap_ad.ssl'), dn=self.conf('ldap_ad.dn'),
                                      search_filter=self.conf('ldap_ad.search_filter'),
                                      search_id=self.conf('ldap_ad.search_id'),
                                      bind_user=self.conf('ldap_ad.bind_user'), bind_pwd=self.conf('ldap_ad.bind_pwd'))
        user = self.auth_provider.login(self.conf('ldap_ad.user'), self.conf('ldap_ad.pwd'))
        self.logger.debug(user.get_groups())
        for k, v in user.get_attributes().items():
            self.logger.debug('%s: %s' % (k, v))


if __name__ == '__main__':
    runtest(LdapAuthTestCase, tests)
