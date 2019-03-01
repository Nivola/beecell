# SPDX-License-Identifier: GPL-3.0-or-later
#
# (C) Copyright 2018-2019 CSI-Piemonte

import networkx as nx
from beecell.networkx.layout import GridLayout
from beecell.tests.test_util import runtest
from beecell.tests.test_util import BeecellTestCase

tests = [
    u'test_grid_layout'
]


class LayoutTestCase(BeecellTestCase):
    def setUp(self):
        BeecellTestCase.setUp(self)

        self.G = nx.karate_club_graph()

    def tearDown(self):
        BeecellTestCase.tearDown(self)

    def test_grid_layout(self):
        layout = GridLayout(self.G)
        layout.generate_grid(1000, 500, 160, 70)
        layout.place_nodes()
        res = layout.print_grid()
        with open(u'graph.svg', u'w') as text_file:
            text_file.write(res)


if __name__ == u'__main__':
    runtest(LayoutTestCase, tests)
