# SPDX-License-Identifier: EUPL-1.2
#
# (C) Copyright 2018-2022 CSI-Piemonte

import networkx as nx
from random import randint


class GridLayout(object):
    """ """

    def __init__(self, graph):
        self._nodes = nx.nodes(graph)
        self._empty_cells = []
        self._busy_cells = []

        self._width = None
        self._height = None
        self._rows = None
        self._cols = None
        self._node_width = None
        self._node_height = None

        self._nodes_pos = {}

    def generate_grid(self, width, height, node_width, node_height):
        self._width = width
        self._height = height
        self._node_width = node_width
        self._node_height = node_height
        self._rows = int(height / node_height)
        self._cols = int(width / node_width)
        w = 0.5 * node_width
        h = 0.5 * node_height

        for i in range(0, self._rows):
            for j in range(0, self._cols):
                cw = int(round(w * (1 + 2 * j)))
                ch = int(round(h * (1 + 2 * i)))
                self._empty_cells.append((cw, ch))

        return self._empty_cells

    def print_grid(self, nodes=None):
        """ """
        w = self._node_width
        h = self._node_height
        res = [
            '<svg width="%s" height="%s"' % (self._width, self._height),
            'xmlns="http://www.w3.org/2000/svg" ',
            'style="fill:white;stroke:black;stroke-width:1;">',
        ]
        for i in range(0, self._rows):
            for j in range(0, self._cols):
                res.append(
                    '<rect x="%s" y="%s" width="%s" height="%s" />'
                    % (w * j, h * i, w, h)
                )

        # print nodes
        iw = self._node_width
        ih = self._node_height
        ix = -0.5 * iw
        iy = -0.5 * ih

        for k, v in self._nodes_pos.items():
            oid = k
            x = v[0]
            y = v[1]
            res.append('<g id="%s" transform="translate(%s,%s)">' % (oid, x, y))
            res.append(
                '<rect x="%s" y="%s" width="%s" height="%s" style="fill:red;" />'
                % (ix, iy, iw, ih)
            )
            res.append("</g>")

        res.append("</svg>")
        return "\n".join(res)

    def get_random_cell(self):
        """ """
        pos = randint(0, len(self._empty_cells) - 1)
        cell = self._empty_cells.pop(pos)
        return cell

    def place_nodes(self):
        """ """
        for n in self._nodes:
            self._nodes_pos[n] = self.get_random_cell()
        return self._nodes_pos
