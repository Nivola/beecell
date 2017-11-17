'''
Created on Sep 2, 2013

@author: darkbk
'''
import unittest
from beecell.auth import extract
from beecell.db.manager import RedisManager, MysqlManager
from tests.test_util import run_test, UtilTestCase
import pprint
import networkx as nx
from networkx.readwrite import json_graph
from random import randint
from beecell.networkx.layout import GridLayout

class LayoutTestCase(UtilTestCase):
    """
    """
    def setUp(self):
        UtilTestCase.setUp(self)
        
        self.G = nx.karate_club_graph()
        #data = json_graph.node_link_data(G)
        #print data
        
    def tearDown(self):
        UtilTestCase.tearDown(self)

    #
    # grid layout
    #
    def test_grid_layout(self):   
        layout = GridLayout(self.G)
        layout.generate_grid(1000, 500, 160, 70)
        layout.place_nodes()
        res = layout.print_grid()
        with open("graph.svg", "w") as text_file:
            text_file.write(res)        
        

def test_suite():
    tests = [
             'test_grid_layout',
            ]
    return unittest.TestSuite(map(LayoutTestCase, tests))

if __name__ == '__main__':
    run_test([test_suite()])