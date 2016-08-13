# -*- coding: utf-8 -*-

import numpy as np
import networkx as nx
import copy
import networkx.algorithms.shortest_paths.weighted as shortest_path
try:
    import shortest_path_weighted as shortest_path_tweaked
except:
    pass


ALLOWED_SHORTEST_PATH_METHOD = ['dijkstra', 'bellman_ford']

class shortest_path_result(object):
    def __init__(self):
        pass


class graph_shortest_path(object):
    def __init__(self, graph, node_label_dict=None, edge_label_style_dict=None, directed=True):
        if node_label_dict:
            if not isinstance(node_label_dict, dict):
                raise ValueError ("node_label_dict must be a dict")
        self.node_label_dict = node_label_dict
        if edge_label_style_dict:
            if not isinstance(edge_label_style_dict, dict):
                raise ValueError ("edge_label_style_dict must be a dict")
        self.edge_label_style_dict = edge_label_style_dict
        if isinstance(graph, np.ndarray):
            graph = np.matrix(graph)
        if isinstance(graph, np.matrix):
            if not graph.shape[0] == graph.shape[1]:
                raise ValueError("The matrix of the graph is not a square matrix")
            for i in range(graph.shape[0]):
                if not graph[i, i] == 0:
                    raise ValueError(
                        "The diagonal of the matrix is not 0 at [%(idx)d, %(idx)d]" % {"idx": i+1})

            if directed:
                graph = nx.from_numpy_matrix(graph, create_using=nx.DiGraph())
            else:
                graph = nx.from_numpy_matrix(graph)

        self.graph = graph
        self.n_node = graph.number_of_nodes()
        self.pred_list = []
        self.seen_list = []
        self.dist_list = []
        self.p_node_list = []
        self.final_pred = []
        self.final_dist = []

    def as_latex(self, layout="spring", use_label=True, no_bidirectional=True):
        return dumps_tikz_doc(g=self.graph, layout=layout,
                              node_label_dict=self.node_label_dict,
                              edge_label_style_dict=self.edge_label_style_dict,
                              use_label=use_label)

    def get_iterated_solution(self, source=0, method="dijkstra"):
        n_node = self.n_node
        pred_list = []
        seen_list = []
        p_node_list = []
        dist_list = []

        def dijkstra_callback(**kwargs):
            pred = copy.deepcopy(kwargs["pred"])
            dist = copy.deepcopy(kwargs["dist"])
            seen = copy.deepcopy((kwargs["seen"]))
            nit = kwargs["nit"]
            p_node = []
            for i in range(n_node):
                if i not in pred:
                    pred[i] = [0]
                if i in dist:
                    p_node.append(i)
                if i not in seen:
                    seen[i] = float('inf')
            pred_list.append(pred)
            dist_list.append(dist)
            seen_list.append(seen)
            p_node_list.append(p_node)

        def bellman_ford_callback(**kwargs):
            dist = copy.deepcopy(kwargs["dist"])
            nit = kwargs["nit"]
            dist_list.append(dist)

        callback = None
        if method == "dijkstra":
            callback = dijkstra_callback
        elif method == "bellman_ford":
            callback = bellman_ford_callback

        pred, dist = self.get_predecessor_and_distance(
            source=source, method=method, callback=callback)
        self.pred_list = pred_list
        self.dist_list = dist_list
        self.seen_list = seen_list
        self.p_node_list = p_node_list

        if method == "dijkstra":
            self.final_pred = pred_list[-1]
        elif method == "bellman_ford":
            self.final_pred = pred
            assert not self.pred_list
            assert not self.seen_list
            assert not self.p_node_list
        self.final_dist = dist

    def get_predecessor_and_distance(self, source=0, method="dijkstra", callback=None):
        if method == "dijkstra":
            return shortest_path_tweaked.dijkstra_predecessor_and_distance(
                self.graph, source=source, callback=callback)
        if method == "bellman_ford":
            dist = {source: 0}
            pred = {source: None}
            if len(self.graph) == 1:
                return pred, dist
            return shortest_path_tweaked.bellman_ford_predecessor_and_distance(
                self.graph, source=0, callback=callback)

    def get_shortest_path(self, target=None):
        # this returns an generator
        if not target:
            target = len(self.graph) - 1
        return shortest_path_tweaked.all_shortest_paths_from_0(self.graph, target=target)

    def get_shortes_distance(self, source=0, target=None, method='dijkstra'):
        if method not in ALLOWED_SHORTEST_PATH_METHOD:
            raise ValueError("Unknown shortest path method: %s" % method)
        if target is None:
            target = self.n_node - 1
        if method == "dijkstra":
            return shortest_path.dijkstra_path_length(
                self.graph, source=source, target=target)


def dumps_tikz_doc(g, layout='spring', node_label_dict=None,
                   edge_label_style_dict=None, use_label=True, no_bidirectional=True):
    """Return TikZ code as `str` for `networkx` graph `g`."""

    if not node_label_dict:
        node_label_dict={}
        for node in g.node:
            node_label_dict[node] = "$v_{%s}$" % str(node + 1)

    if layout not in ('layered', 'spring'):
        raise ValueError('Unknown layout: {s}'.format(s=layout))
    layout_lib = ""
    if layout == 'layered':
        layout_lib = 'layered'
    elif layout == 'spring':
        layout_lib = 'force'
    s = ''
    for n, d in g.nodes_iter(data=True):
        # label
        label = node_label_dict.get(n, '')
        label = 'as={' + label + '}' if label else ''
        # geometry
        color = d.get('color', '')
        fill = d.get('fill', '')
        shape = d.get('shape', '')
        # style
        style = ', '.join(filter(None, [label, color, fill, shape]))
        style = '[' + style + ']' if style else ''
        # pack them
        s += '{n}{style};\n'.format(n=n, style=style)
    s += '\n'
    if nx.is_directed(g):
        line = ' -> '
    else:
        line = ' -- '
    for u, v, d in g.edges_iter(data=True):
        if use_label:
            label = str(int(g.get_edge_data(u, v).get("weight")))
            #label = d.get('label', '')
            color = d.get('color', '')
        else:
            label = str(d)
            color = ''
        if label:
            label = '"' + label + '"\' above'
        loop = 'loop' if u is v else ''

        custom_style = None
        if edge_label_style_dict:
            if (u,v) in edge_label_style_dict:
                custom_style = edge_label_style_dict[(u,v)]

        # 方向互反的箭头
        bend = ''
        if no_bidirectional:
            bend = 'bend left' if g.has_edge(v, u) else ''
        style = ', '.join(filter(None, [label, color, loop, bend, custom_style]))
        style = ' [' + style + '] ' if style else ''
        s += str(u) + line + style + str(v) + ';\n'
    tikzpicture = (
        r'\begin{{tikzpicture}}[>={{Stealth[length=3mm]}}]' '\n'
        '\graph[{layout} layout, node distance=2.0cm,'
        # 'edge quotes mid,'
        'edges={{nodes={{ sloped, inner sep=1pt }} }},'
        'nodes={{circle, draw}} ]{{\n'
        '{s}'
        '}};\n'
        '\end{{tikzpicture}}\n').format(
            layout=layout,
            s=s)

    preamble = (
        '\documentclass{{standalone}}\n'
        '\usepackage{{amsmath}}\n'
        '\n'
        '\usepackage{{tikz}}\n'
        '\usetikzlibrary{{graphs,graphs.standard,'
        'graphdrawing,quotes,shapes,arrows.meta}}\n'
        '\usegdlibrary{{ {layout_lib} }}\n').format(
            layout_lib=layout_lib)

    return (
        '{preamble}\n'
        r'\begin{{document}}' '\n'
        '\n'
        '{tikz}'
        '\end{{document}}\n').format(
            preamble=preamble,
            tikz=tikzpicture)