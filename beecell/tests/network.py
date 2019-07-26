# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

from beecell.network import InternetProtocol
from beecell.sendmail import Mailer
from beecell.tests.test_util import runtest
from beecell.tests.test_util import BeecellTestCase


tests = [
    u'test_get_name_from_number',
    u'test_get_number_from_name',
    u'test_get_names'
]


class NetworkTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

        self.client = InternetProtocol()

    def tearDown(self):
        BeecellTestCase.tearDown(self)

    def test_get_name_from_number(self):
        res = self.client.get_name_from_number(6)
        self.assertEqual(res, u'tcp')

    def test_get_number_from_name(self):
        res = self.client.get_number_from_name(u'tcp')
        self.assertEqual(res, 6)

    def test_get_names(self):
        res = self.client.get_names()
        print res


if __name__ == u'__main__':
    runtest(NetworkTestCase, tests)
