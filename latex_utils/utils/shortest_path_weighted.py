# -*- coding: utf-8 -*-
"""
Shortest path algorithms for weighed graphs.
"""

from heapq import heappush, heappop
from itertools import count
import networkx as nx
import numpy as np


def _dijkstra(G, source, get_weight, pred=None, paths=None, cutoff=None,
              target=None, callback=None):
    """Implementation of Dijkstra's algorithm

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

    get_weight: function
        Function for getting edge weight

    pred: list, optional(default=None)
        List of predecessors of a node

    paths: dict, optional (default=None)
        Path from the source to a target node.

    target : node label, optional
       Ending node for path

    cutoff : integer or float, optional
       Depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    distance,path : dictionaries
       Returns a tuple of two dictionaries keyed by node.
       The first dictionary stores distance from the source.
       The second stores the path from the source to that node.

    pred,distance : dictionaries
       Returns two dictionaries representing a list of predecessors
       of a node and the distance to each node.

    distance : dictionary
       Dictionary of shortest lengths keyed by target.
    """
    G_succ = G.succ if G.is_directed() else G.adj

    push = heappush
    pop = heappop
    dist = {}  # dictionary of final distances
    seen = {source: 0}
    c = count()
    fringe = []  # use heapq with (distance,label) tuples
    push(fringe, (0, next(c), source))

    iterations = 0
    while fringe:
        (d, _, v) = pop(fringe)
        if v in dist:
            continue  # already searched this node.
        dist[v] = d
        if v == target:
            break

        for u, e in G_succ[v].items():
            cost = get_weight(v, u, e)
            if cost is None:
                continue
            vu_dist = dist[v] + get_weight(v, u, e)
            if cutoff is not None:
                if vu_dist > cutoff:
                    continue
            if u in dist:
                if vu_dist < dist[u]:
                    raise ValueError('Contradictory paths found:',
                                     'negative weights?')
            elif u not in seen or vu_dist < seen[u]:
                seen[u] = vu_dist
                push(fringe, (vu_dist, next(c), u))
                if paths is not None:
                    paths[u] = paths[v] + [u]
                if pred is not None:
                    pred[u] = [v]
            elif vu_dist == seen[u]:
                if pred is not None:
                    pred[u].append(v)

        # callback
        if callback is not None:
            # print"iterations", iterations
            # print "pred", pred
            # print "dist", dist
            # print "seen", seen
            # #solution[:] = 0

            kwargs ={
                "nit": iterations,
                "pred": pred,
                "dist": dist,
                "seen": seen
            }

            callback(**kwargs)
        iterations += 1

    if paths is not None:
        return (dist, paths)
    if pred is not None:
        return (pred, dist)
    return dist


def dijkstra_predecessor_and_distance(G, source, cutoff=None, weight='weight', callback=None):
    """Compute shortest path length and predecessors on shortest paths
    in weighted graphs.

    Parameters
    ----------
    G : NetworkX graph

    source : node label
       Starting node for path

    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight

    cutoff : integer or float, optional
       Depth to stop the search. Only paths of length <= cutoff are returned.

    Returns
    -------
    pred,distance : dictionaries
       Returns two dictionaries representing a list of predecessors
       of a node and the distance to each node.

    Notes
    -----
    Edge weight attributes must be numerical.
    Distances are calculated as sums of weighted edges traversed.

    The list of predecessors contains more than one element only when
    there are more than one shortest paths to the key node.
    """
    if G.is_multigraph():
        get_weight = lambda u, v, data: min(
            eattr.get(weight, 1) for eattr in data.values())
    else:
        get_weight = lambda u, v, data: data.get(weight, 1)

    pred = {source: []}  # dictionary of predecessors
    return _dijkstra(G, source, get_weight, pred=pred, cutoff=cutoff, callback=callback)


def bellman_ford_predecessor_and_distance(G, source=None, weight='weight', callback=None):

    # currently only support the following problem:
    # 1. non-multigraph
    # 2. source is 0
    # 3. directed graph
    assert not G.is_multigraph()
    #assert source == 0
    assert G.is_directed()

    if not source == 0:
        raise ValueError("This method currently only support source=0")

    pred = {source: None}

    def get_weight(edge_dict):
        return edge_dict.get(weight, 1)

    G_succ = G.succ if G.is_directed() else G.adj
    inf = float('inf')
    g_mat = nx.to_numpy_matrix(G)
    g_mat[g_mat==0] = inf
    n = len(G)

    dist_j = []
    iterations = 0
    while True:
        iterations += 1
        dist_j_i = np.full(n, inf)
        dist_j_i[0] = 0

        dist_last = dist_j[-1] if dist_j else None
        if iterations == 1:
            for v, e in G_succ[0].items():
                dist_j_i[v] = get_weight(e)
        else:
            for v in range(n):
                dist_j_i_array = dist_last + np.array(g_mat.transpose()[v, :][0])
                dist_j_i[v] = min(dist_last[v], np.min(dist_j_i_array))

        dist_j.append(dist_j_i.tolist())

        if dist_last is not None:
            if np.array_equal(dist_j_i, dist_last):
                break

        if iterations == n:
            raise nx.NetworkXUnbounded(
                "Negative cost cycle detected.")

        if callback is not None:
            # print"iterations", iterations
            # print "pred", pred
            # print "dist", dist
            # print "seen", seen
            # #solution[:] = 0

            kwargs ={
                "nit": iterations,
                "pred": None,
                "dist": dist_j,
                "seen": None
            }

            callback(**kwargs)


    for v in range(n):
        if not v in pred:
            pred[v] = []

        dist_j_i_array = dist_j_i + np.array(g_mat.transpose()[v, :])
        final_array = dist_j_i_array.tolist()
        final_array = final_array[0]

        if pred[v] is not None:
            for u in range(n):
                if dist_j_i[v] == final_array[u]:
                    pred[v].append(u)

    return pred, dist_j


def all_shortest_paths_from_0(G, target, weight="weight"):
    source = 0
    if weight is not None:
        pred,dist = bellman_ford_predecessor_and_distance(G, source, weight=weight)
    else:
        pred = nx.predecessor(G,source)
    if target not in pred:
        raise nx.NetworkXNoPath()
    stack = [[target,0]]
    top = 0
    while top >= 0:
        node,i = stack[top]
        if node == source:
            yield [p for p,n in reversed(stack[:top+1])]
        if pred[node] is None:
            pred[node] = []
        if len(pred[node]) > i:
            top += 1
            if top == len(stack):
                stack.append([pred[node][i],0])
            else:
                stack[top] = [pred[node][i],0]
        else:
            stack[top-1][1] += 1
            top -= 1