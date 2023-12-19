# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

from beecell.auth import extract
from beecell.tests.test_util import BeecellTestCase, runtest

tests = ["test_extract"]


class PermTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

    def tearDown(self):
        BeecellTestCase.tearDown(self)

    def test_extract(self):
        perms = [
            "a1//b1//c4//*",
            "a1//b1//c1//*",
            "a1//b1//c2//*",
            "a1//b2//*//*",
            "a2//b3//*//*",
            "a1//b4//c3//d1",
            "a1//*//*//*",
        ]
        res = extract(perms)
        self.logger.debug(res)


if __name__ == "__main__":
    runtest(PermTestCase, tests)
