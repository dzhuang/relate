# -*- coding: utf-8 -*-

import numpy as np
from collections import OrderedDict
from scipy.optimize._linprog import OptimizeResult
import networkx as nx
import copy
import networkx.algorithms.shortest_paths.weighted as shortest_path
try:
    import shortest_path_weighted as shortest_path_tweaked
except:
    pass


ALLOWED_SHORTEST_PATH_METHOD = ['dijkstra', 'bellman_ford']

class shortest_path_result(OptimizeResult):
    def __init__(self, **kwargs):
        super(shortest_path_result, self).__init__(**kwargs)
        assert kwargs["dist_list"]
        assert kwargs["final_pred"]
        assert kwargs["node_label_dict"]
        self.dist_list = kwargs["dist_list"]
        self.final_pred = kwargs["final_pred"]
        self.node_label_dict = kwargs["node_label_dict"]

    def as_latex(self):
        raise NotImplementedError()

def trans_node_list_tex(node_list, node_label_dict, empty_list_alt="", sout=True, wrap=True):
    # sout 是指使用删除线\st{}
    assert isinstance(node_list, list)
    assert isinstance(node_label_dict, dict)
    if not node_list and empty_list_alt:
        return empty_list_alt

    node_label_tex =  "&".join(["%s" % str(node_label_dict[node]) for node in node_list])

    if sout:
        node_label_tex = "\\st{%s}" % node_label_tex
    if wrap:
        node_label_tex = "$%s$" % node_label_tex

    return node_label_tex


class dijkstra_result(shortest_path_result):
    def __init__(self, **kwargs):
        super(dijkstra_result, self).__init__(**kwargs)
        assert kwargs["pred_list"]
        assert kwargs["seen_list"]
        assert kwargs["p_node_list"]
        self.pred_list = kwargs["pred_list"]
        self.seen_list = kwargs["seen_list"]
        self.p_node_list = kwargs["p_node_list"]
        self.tex_pred_list = []
        self.tex_L_list = []
        self.tex_result = ""
        self.as_latex()

    def as_latex(self):
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

        print n_pred_lines

        simplified_pred_list = [{node:[] for node in self.final_pred},] * n_pred_lines
        print simplified_pred_list
        print simplified_pred_dict

        for i in reversed(range(n_pred_lines)):
            print i
            for node in self.final_pred:
                sout = True
                if i != pred_size_dict[node]:
                    sout = False
                try:
                    simplified_pred_list[i][node] = simplified_pred_dict[node][i]
                    if i == 2:
                        print node, simplified_pred_dict[node][i]
                        print simplified_pred_list[i][node]
                except:
                    pass
            print simplified_pred_list
                #print "simplified_pred_list[i][node]", simplified_pred_list[i][node]


        print simplified_pred_list







        #print simplified_pred_dict



        simplified_pred_list = copy.deepcopy(self.pred_list)
        for i, pred_dict_iter_i in enumerate(simplified_pred_list):
            for node in pred_dict_iter_i:
                if i > pred_size_dict[node] - 1:
                    pred_dict_iter_i[node] =[]

        #print simplified_pred_list


        # tex_pred_list = []
        # #print self.node_label_dict
        # for i, pred_dict_iter_i in enumerate(simplified_pred_list):
        #     tex_pred_list_i = []
        #     empty_list_alt = "-" if i==0 else ""
        #     for node, pred_list in pred_dict_iter_i.items():
        #         sout = False
        #         if i < pred_size_dict[node] - 1:
        #             sout = True
        #         tex_pred_list_i.append(trans_node_list_tex(pred_list, self.node_label_dict, empty_list_alt=empty_list_alt, sout=sout))
        #     try:
        #         for j, pred in enumerate(pred_dict_iter_i):
        #             if pred == self.pred_list[i-1][j]
        #                 tex_pred_list_i = ""
        #     tex_pred_list.append(tex_pred_list_i)
        #
        #     #if i == 0:
        #     #    tex_pred_list.append([trans_node_list_tex(node_list, self.node_label_dict) for node_list in p])
        #
        # print tex_pred_list

        # pred_list_size = 0
        # for node, pred in self.final_pred.items():
        #     if len(pred) > pred_list_size:
        #         pred_list_size = len(pred)


        #print pred_list_size

class bellman_ford_result(shortest_path_result):
    def __init__(self, **kwargs):
        super(bellman_ford_result, self).__init__(**kwargs)
        assert not kwargs.get("pred_list", None)
        assert kwargs["dist_list"]
        assert not kwargs.get("seen_list", None)
        assert kwargs["final_pred"]
        assert not kwargs.get("p_node_list")
        #self.pred_list = kwargs["pred_list"]
        self.dist_list = kwargs["dist_list"]
        #self.seen_list = kwargs["seen_list"]
        self.final_pred = kwargs["final_pred"]
        #self.p_node_list = kwargs["p_node_list"]


class network(object):
    def __init__(self, graph, directed=True, node_label_dict=None, edge_label_style_dict=None, node_tex_prefix="v"):
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

        for node in range(len(graph)):
            if node not in self.node_label_dict:
                self.node_label_dict[node] = (
                    "%(prefix)s_%(subscript)s"
                    % {"prefix": node_tex_prefix,
                       "subscript": node + 1
                       }
                    if node_tex_prefix else node + 1
                )

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

        self.final_dist = dist
        if method == "dijkstra":
            final_pred = pred_list[-1]
            return dijkstra_result(
                pred_list=pred_list, dist_list=dist_list, seen_list=seen_list,
                p_node_list=p_node_list, final_pred=final_pred,
                node_label_dict=self.node_label_dict)
        elif method == "bellman_ford":
            final_pred = pred
            assert not self.pred_list
            assert not self.seen_list
            assert not self.p_node_list
            return bellman_ford_result(final_pred=final_pred, dist_list=dist_list,
                                       node_label_dict=self.node_label_dict)

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