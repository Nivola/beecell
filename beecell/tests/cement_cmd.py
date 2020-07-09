# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte
# (C) Copyright 2019-2020 CSI-Piemonte

import sys

from cement.ext.ext_argparse import expose
from beecell.cement_cmd.foundation import CementCmdBaseController, CementCmd
from beecell.tests.test_util import runtest
from beecell.tests.test_util import BeecellTestCase

tests = [
    'test_create'
]


class MyBaseController(CementCmdBaseController):
    class Meta:
        label = 'base'
        description = "Beehive cli"
        arguments = []

    @expose(help="this command does relatively nothing useful")
    def c1(self):
        self.app.log.info("Inside MyBaseController.command1()")

    @expose(aliases=['cmd2'], help="more of nothing")
    def c2(self):
        self.app.log.info("Inside MyBaseController.command2()")


class MySecondController(CementCmdBaseController):
    class Meta:
        label = 'second'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = "Authorization management"
        arguments = []

    @expose(help='this is some command', aliases=['some-cmd'])
    def c3(self):
        self.app.log.info("Inside MySecondController.second_cmd1")


class MyApp(CementCmd):
    class Meta:
        label = 'beehive'
        base_controller = 'base'
        handlers = [MyBaseController, MySecondController]
        prompt = 'beehive> '
        ignore_unknown_arguments = True


class CementTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

    def tearDown(self):
        BeecellTestCase.tearDown(self)

    def test_create(self):
        app = MyApp('prova')
        # app.setup()
        app.run()
        # app.run_forever()
        app.close()


if __name__ == '__main__':
    runtest(CementTestCase, tests)
