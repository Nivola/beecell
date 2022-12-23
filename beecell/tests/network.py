# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

from beecell.network import InternetProtocol
from beecell.sendmail import Mailer
from beecell.tests.test_util import runtest
from beecell.tests.test_util import BeecellTestCase


tests = [
    'test_get_name_from_number',
    'test_get_number_from_name',
    'test_get_names'
]


class NetworkTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

        self.client = InternetProtocol()

    def tearDown(self):
        BeecellTestCase.tearDown(self)

    def test_get_name_from_number(self):
        res = self.client.get_name_from_number(6)
        self.assertEqual(res, 'tcp')

    def test_get_number_from_name(self):
        res = self.client.get_number_from_name('tcp')
        self.assertEqual(res, 6)

    def test_get_names(self):
        res = self.client.get_names()


if __name__ == '__main__':
    runtest(NetworkTestCase, tests)
