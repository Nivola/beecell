# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2023 CSI-Piemonte

import networkx as nx
from beecell.networkx.layout import GridLayout
from beecell.tests.test_util import runtest
from beecell.tests.test_util import BeecellTestCase

tests = ["test_grid_layout"]


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
        with open("graph.svg", "w") as text_file:
            text_file.write(res)


if __name__ == "__main__":
    runtest(LayoutTestCase, tests)
