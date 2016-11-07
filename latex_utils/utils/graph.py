# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import numpy as np
from collections import OrderedDict
from scipy.optimize._linprog import OptimizeResult
import networkx as nx
import copy
import networkx.algorithms.shortest_paths.weighted as shortest_path
from networkx.exception import NetworkXException

try:
    from shortest_path_weighted import dijkstra_predecessor_and_distance
except ImportError:
    pass

try:
    from shortest_path_weighted import bellman_ford_predecessor_and_distance
except ImportError:
    pass

try:
    from shortest_path_weighted import all_shortest_paths_from_0
except ImportError:
    pass


ALLOWED_SHORTEST_PATH_METHOD = ['dijkstra', 'bellman_ford']


class NetworkNegativeWeightUsingDijkstra(NetworkXException):
    """Using dijkstra to solve shortest path with negative weight"""


class shortest_path_result(OptimizeResult):
    def __init__(self, **kwargs):
        super(shortest_path_result, self).__init__(**kwargs)
        assert kwargs["dist_list"]
        assert kwargs["final_pred"]
        assert kwargs["node_label_dict"]
        assert kwargs["shortest_path_list"]
        self.dist_list = kwargs["dist_list"]
        self.final_pred = kwargs["final_pred"]
        self.node_label_dict = kwargs["node_label_dict"]
        shortest_path_list = kwargs["shortest_path_list"]
        self.shortest_path_tex_list=[]
        for sp_list in shortest_path_list:
            shortest_path_tex_list = []
            for node in sp_list:
                shortest_path_tex_list.append(self.node_label_dict[node])
            self.shortest_path_tex_list.append(shortest_path_tex_list)
        self.tex_node_list = ["$%s$" % self.node_label_dict[node] for node in self.node_label_dict]

    def as_latex(self):
        raise NotImplementedError()


def trans_node_list_tex(node_list, node_label_dict, empty_list_alt="", sout=True, wrap=True):
    # sout is latex macro \st{}
    if node_list is not None:
        assert isinstance(node_list, list)
    assert isinstance(node_label_dict, dict)
    if not node_list and empty_list_alt:
        return empty_list_alt

    node_label_tex = "\&".join(
        ["%s" % str(node_label_dict[node]) for node in node_list])

    if node_label_tex and sout:
        return r"\st{$%s$}" % node_label_tex
    if node_label_tex and wrap:
        node_label_tex = "$%s$" % node_label_tex

    return node_label_tex


class DijkstraResult(shortest_path_result):
    def __init__(self, **kwargs):
        super(DijkstraResult, self).__init__(**kwargs)
        assert kwargs["pred_list"]
        assert kwargs["seen_list"]
        assert kwargs["p_node_list"]
        self.pred_list = kwargs["pred_list"]
        self.seen_list = kwargs["seen_list"]
        self.p_node_list = kwargs["p_node_list"]
        self.tex_pred_list = []
        self.tex_L_list = []
        self.tex_result = ""
        self.n_pred_lines = 0
        self.as_latex()

    def as_latex(self):

        # {{{ get pred part tex in simplified dijkstra result
        pred_size_dict = {}

        simplified_pred_dict = {node:[] for node in self.final_pred}
        for i, pred_dict_iter_i in enumerate(self.pred_list):
            for node in self.final_pred:
                if not pred_dict_iter_i[node] in simplified_pred_dict[node]:
                    simplified_pred_dict[node].append(pred_dict_iter_i[node])

        n_pred_lines = 0
        for node, pred in simplified_pred_dict.items():
            pred_size_dict[node] = len(pred)
            if len(pred) > n_pred_lines:
                n_pred_lines = len(pred)

        for node in self.final_pred:
            simplified_pred_dict[node].extend(
                [[],] * (n_pred_lines-len(simplified_pred_dict[node])))

        simplified_pred_list = [
            {node:[] for node in self.final_pred}
            for i in list(range(n_pred_lines))]

        for i in reversed(list(range(n_pred_lines))):
            for node in self.final_pred:
                sout = True
                empty_list_alt = ""
                if i == pred_size_dict[node] - 1:
                    sout = False
                if i == 0:
                    empty_list_alt = "-"
                simplified_pred_list[i][node] = trans_node_list_tex(
                    simplified_pred_dict[node][i],
                    self.node_label_dict,
                    empty_list_alt=empty_list_alt,
                    sout=sout,
                )
        self.n_pred_lines = n_pred_lines
        simplified_pred_list.reverse()
        self.tex_pred_list = simplified_pred_list
        #print self.tex_pred_list
        # }}}

        #self.tex_L_list

        tex_L_list = copy.deepcopy(self.seen_list)
        for i, L in enumerate(tex_L_list):
            for node, dist in L.items():
                is_p_node = False
                if node in self.p_node_list[i]:
                    is_p_node = True
                if is_p_node:
                    L[node] = r"$\dlab {%s}*$" % trans_latex_fraction(L[node], wrap=False)
                else:
                    L[node] = r"$%s$" % trans_latex_fraction(L[node], wrap=False)

        self.tex_L_list = tex_L_list


class BellmanFordResult(shortest_path_result):
    def __init__(self, **kwargs):
        super(BellmanFordResult, self).__init__(**kwargs)
        assert not kwargs.get("pred_list", None)
        assert kwargs["dist_list"]
        assert kwargs["graph_matrix"] is not None
        assert not kwargs.get("seen_list", None)
        assert kwargs["final_pred"]
        assert not kwargs.get("p_node_list")
        self.dist_list = kwargs["dist_list"]
        self.graph_matrix = kwargs["graph_matrix"]
        self.final_pred = kwargs["final_pred"]
        self.matrix= []
        self.dist_list_by_node = []
        self.final_pred_tex_dict = {}
        self.nit = len(self.dist_list)
        self.as_latex()

    def as_latex(self):
        matrix = copy.deepcopy(self.graph_matrix)
        matrix = matrix.tolist()
        for i in list(range(len(matrix))):
            for j in list(range(len(matrix[i]))):
                if matrix[i][j] == 0:
                    matrix[i][j] = ""
                elif matrix[i][j] == int(matrix[i][j]):
                    matrix[i][j] = int(matrix[i][j])
        self.matrix = matrix

        dist_list_by_node_npmatrix = np.matrix(self.dist_list).transpose()
        dist_list_by_node = dist_list_by_node_npmatrix.tolist()
        for i in list(range(len(dist_list_by_node))):
            for j in list(range(len(dist_list_by_node[i]))):
                if dist_list_by_node[i][j] == float("inf"):
                    dist_list_by_node[i][j] = ""
                elif int(dist_list_by_node[i][j]) == dist_list_by_node[i][j]:
                    dist_list_by_node[i][j] = int(dist_list_by_node[i][j])
        self.dist_list_by_node = dist_list_by_node

        final_pred_tex_dict = {}
        for node in self.final_pred:
            final_pred_tex_dict[node] = trans_node_list_tex(
                self.final_pred[node], node_label_dict=self.node_label_dict,
                sout=False, wrap=True, empty_list_alt="-")

        self.final_pred_tex_dict = final_pred_tex_dict


class network(object):
    def __init__(self, graph, directed=True, node_label_dict=None, edge_label_style_dict=None, node_tex_prefix="v", id=None):
        if node_label_dict:
            if not isinstance(node_label_dict, dict):
                raise ValueError ("node_label_dict must be a dict")
        else:
            node_label_dict = {}
        self.node_label_dict = node_label_dict
        self.node_tex_prefix = node_tex_prefix
        if edge_label_style_dict:
            if not isinstance(edge_label_style_dict, dict):
                raise ValueError ("edge_label_style_dict must be a dict")
        self.edge_label_style_dict = edge_label_style_dict
        self.graph_matrix = None
        if isinstance(graph, np.ndarray):
            graph = np.matrix(graph)
        if isinstance(graph, np.matrix):
            if not graph.shape[0] == graph.shape[1]:
                raise ValueError("The matrix of the graph is not a square matrix")
            for i in list(range(graph.shape[0])):
                if not graph[i, i] == 0:
                    raise ValueError(
                        "The diagonal of the matrix is not 0 at [%(idx)d, %(idx)d]" % {"idx": i+1})

            self.graph_matrix = np.copy(graph)
            if directed:
                graph = nx.from_numpy_matrix(graph, create_using=nx.DiGraph())
            else:
                graph = nx.from_numpy_matrix(graph)

        self.has_negative_edge_weight = False
        if self.graph_matrix is None:
            self.graph_matrix = nx.to_numpy_matrix(graph)
        if self.graph_matrix.min() < 0:
            self.has_negative_edge_weight = True

        self.has_6_9_edge_weight = False
        if np.any(np.where(self.graph_matrix==6)) or np.any(np.where(self.graph_matrix==9)):
            self.has_6_9_edge_weight = True

        self.graph = graph
        self.n_node = graph.number_of_nodes()
        self.pred_list = []
        self.seen_list = []
        self.dist_list = []
        self.p_node_list = []
        self.final_pred = []
        self.final_dist = []
        self.shortest_path_list = []
        self.id = id

        for node in list(range(len(graph))):
            if node not in self.node_label_dict:
                self.node_label_dict[node] = (
                    "%(prefix)s_{%(subscript)s}"
                    % {"prefix": node_tex_prefix,
                       "subscript": node + 1
                       }
                    if node_tex_prefix else node + 1
                )

    def as_latex(self, layout="spring", use_label=True, no_bidirectional=True):
        return dumps_tikz_doc(g=self.graph, layout=layout,
                              node_label_dict=self.node_label_dict,
                              edge_label_style_dict=self.edge_label_style_dict,
                              use_label=use_label,
                              no_bidirectional=no_bidirectional
                              )

    def get_iterated_solution(self, source=0, method="dijkstra"):
        n_node = self.n_node
        pred_list = []
        seen_list = []
        p_node_list = []
        dist_list = []

        if self.has_negative_edge_weight and method=="dijkstra":
            raise NetworkNegativeWeightUsingDijkstra(
                "Graph with negative edge weight not suitable for dijkstra")

        def dijkstra_callback(**kwargs):
            pred = copy.deepcopy(kwargs["pred"])
            dist = copy.deepcopy(kwargs["dist"])
            seen = copy.deepcopy((kwargs["seen"]))
            nit = kwargs["nit"]
            p_node = []
            for i in list(range(n_node)):
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

        if isinstance(dist, dict):
            self.final_dist = dist
        else:
            dist_dict = {}
            for idx, v in enumerate(dist[-1]):
                dist_dict[idx] = v
            self.final_dist = dist_dict

        if method == "dijkstra":
            final_pred = pred_list[-1]
            return DijkstraResult(
                pred_list=pred_list, dist_list=dist_list, seen_list=seen_list,
                p_node_list=p_node_list, final_pred=final_pred,
                shortest_path_list=list(self.get_shortest_path()),
                node_label_dict=self.node_label_dict)
        elif method == "bellman_ford":
            final_pred = pred
            assert not self.pred_list
            assert not self.seen_list
            assert not self.p_node_list
            return BellmanFordResult(graph_matrix=self.graph_matrix, final_pred=final_pred, dist_list=dist_list,
                                     node_label_dict=self.node_label_dict,
                                     shortest_path_list=list(self.get_shortest_path()),
                                     )

    def get_predecessor_and_distance(self, source=0, method="dijkstra", callback=None):
        if method == "dijkstra":
            return dijkstra_predecessor_and_distance(
                self.graph, source=source, callback=callback)
        if method == "bellman_ford":
            dist = {source: 0}
            pred = {source: None}
            if len(self.graph) == 1:
                return pred, dist
            return bellman_ford_predecessor_and_distance(
                self.graph, source=0, callback=callback)

    def get_shortest_path(self, target=None):
        # this returns an generator
        if not target:
            target = len(self.graph) - 1
        return all_shortest_paths_from_0(self.graph, target=target)

    def get_shortes_distance(self, source=0, target=None, method='dijkstra'):
        if method not in ALLOWED_SHORTEST_PATH_METHOD:
            raise ValueError("Unknown shortest path method: %s" % method)
        if target is None:
            target = self.n_node - 1
        if method == "dijkstra":
            return shortest_path.dijkstra_path_length(
                self.graph, source=source, target=target)

    def as_capacity_graph(self):
        capacity_network = nx.DiGraph()
        n = self.graph.number_of_nodes
        for edge in self.graph.edges():
            capacity_network.add_edge(
                edge[0],edge[1], capacity=self.graph[edge[0]][edge[1]]['weight'])

        return capacity_network


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
        label = 'as={$' + label + '$}' if label else ''
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
            label = '"$' + label + '$"\' above'
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
        r'\documentclass{{standalone}}' '\n'
        '\\usepackage{{amsmath}}\n'
        '\n'
        '\\usepackage{{tikz}}\n'
        '\\usetikzlibrary{{graphs,graphs.standard,'
        'graphdrawing,quotes,shapes,arrows.meta}}\n'
        '\\usegdlibrary{{ {layout_lib} }}\n').format(
            layout_lib=layout_lib)

    return (
        '{preamble}\n'
        r'\begin{{document}}' '\n'
        '\n'
        '{tikz}'
        r'\end{{document}}\n').format(
            preamble=preamble,
            tikz=tikzpicture)


def trans_latex_fraction(f, wrap=True):
    from fractions import Fraction
    if not isinstance(f, str):
        try:
            f = str(f)
        except:
            pass
    try:
        frac = str(Fraction(f).limit_denominator())
    except ValueError:
        if f == "inf":
            return r"\infty"
        else:
            return f
    negative = False
    if frac.startswith("-"):
        negative = True
        frac = frac[1:]
    if "/" in frac:
        frac_list = frac.split("/")
        frac = r"\frac{%s}{%s}" % (frac_list[0], frac_list[1])
    if not wrap:
        if negative:
            frac = r"-" + frac
        return "%s" % frac
    else:
        if negative:
            frac = r"\mbox{$-$}" + frac
        return "$%s$" % frac
