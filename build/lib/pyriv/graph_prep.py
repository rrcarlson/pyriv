import os
import numpy as np
import networkx as nx
from river_graph import RiverGraph

class GraphBuilder(object):

    def __init__(self, file_path, coastal_fcode=56600):
        """
        Build a graph from a shapefile and provide methods to prune, or read
        a gpickle file and convert it to a `RiverGraph`.
        """
        self.fcode = coastal_fcode
        if os.path.splitext(file_path)[1] == '.shp':
            self.graph = RiverGraph(data=nx.read_shp(file_path), \
                                    coastal_fcode=self.fcode)
        elif os.path.splitext(file_path)[1] == '.graphml':
            self.graph = RiverGraph(data=nx.read_graphml(file_path), \
                                    coastal_fcode=self.fcode)
        else:
            self.graph = RiverGraph(data=nx.read_gpickle(file_path), \
                                    coastal_fcode=self.fcode)

    def prune_network(self, verbose=False):
        """
        Remove subgraphs of the network that do not connect to the coastline.
        """
        sg = self.graph
        coast_n = 0
        noncoast_n = 0
        g_list = []
        cps = nx.weakly_connected_component_subgraphs(sg)
        for cp in cps:
            if has_coast_node(cp.nodes(), sg, fcode=self.fcode):
                g_list.append(cp)
                coast_n += 1
            else:
                noncoast_n += 1
        if verbose:
            print "{} graphs with coastal nodes, {} without.".format(coast_n, noncoast_n)
        return RiverGraph(data=nx.compose_all(g_list), coastal_fcode=self.fcode)

    def write_gpickle(self, out_file_path):
        """
        This writes the DiGraph to a gpickle.
        """
        nxg = nx.DiGraph(data=self.graph)
        nx.write_gpickle(nxg, out_file_path)

    def write_graphml(self, out_file_path):
        """
        This writes the DiGraph to a GraphML file.
        """
        nxg = nx.DiGraph(data=self.graph)
        nx.write_graphml(nxg, out_file_path)


def has_coast_node(node_list, sg, fcode=56600):
    """
    Given a list of nodes, return `True` if at least one node is
    coastal. Otherwise, return `False`. This is essentially the same as
    `RiverGraph.has_coast_node`, but including this function here stops me
    from having to convert subgraphs to RiverGraphs when I prune the network.
    """
    return np.apply_along_axis(sg.is_coastal_node, 1, np.array(node_list)).any()
