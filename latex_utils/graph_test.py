# import networkx as nx
# import numpy as np
import matplotlib.pyplot as plt
# import pylab
#
# G = nx.DiGraph()
#
# G.add_edges_from([('A', 'B'),('C','D'),('G','D')], weight=1)
# G.add_edges_from([('D','A'),('D','E'),('B','D'),('D','E')], weight=2)
# G.add_edges_from([('B','C'),('E','F')], weight=3)
# G.add_edges_from([('C','F')], weight=4)
#
#
# val_map = {'A': 1.0,
#                    'D': 0.5714285714285714,
#                               'H': 0.0}
#
# values = [val_map.get(node, 0.45) for node in G.nodes()]
# edge_labels=dict([((u,v,),d['weight'])
#                  for u,v,d in G.edges(data=True)])
# red_edges = [('C','D'),('D','A')]
# edge_colors = ['black' if not edge in red_edges else 'red' for edge in G.edges()]
#
# pos=nx.spring_layout(G)
# nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_labels)
# nx.draw(G,pos, node_color = values, node_size=1500,edge_color=edge_colors,edge_cmap=plt.cm.Reds)
# pylab.show()

import networkx as nx
from nx2tikz import nx2tikz


def _preamble(layout='layered'):
    """Return preamble and begin/end document."""
    if layout == 'layered':
        layout_lib = 'layered'
    elif layout == 'spring':
        layout_lib = 'force'
    else:
        raise ValueError(
            'Unknown which library contains layout: {s}'.format(s=layout))
    document = (
        '\documentclass{{standalone}}\n'
        '\usepackage{{amsmath}}\n'
        '\n'
        '\usepackage{{tikz}}\n'
        '\usetikzlibrary{{graphs,graphs.standard,'
        'graphdrawing,quotes,shapes}}\n'
        '\usegdlibrary{{ {layout_lib} }}\n').format(
            layout_lib=layout_lib)
    return document

def write_tikz():
    fname = 'mygraph.tex'
    g = graph()
    tikz = nx2tikz.dumps_tikz(g, layout="spring")
    print(tikz)
    #tex = nx2tikz.dump_tex()
    # with open(fname, 'w') as f:
    #     f.write(tikz)
    #     #f.write(tex)
    #     f.close()


def graph():
    #g = nx.DiGraph()
    # nodes
    # g.add_node(1, label='$a$', color='yellow', shape='ellipse')
    # g.add_node(2, label='$b$', color='blue', fill='orange', shape='circle')
    # g.add_node(3, label='$c$', shape='rectangle')
    # g.add_node(4, label='$E=mc^2$')
    # g.add_node(5, label=r'$\begin{bmatrix} x_1\\ x_2\\ x_3\end{bmatrix}$')
    # # edges
    # g.add_edge(1, 2, label='$\{p\}$')
    # g.add_edge(1, 3, label='$\{a,b\}$', color='purple')
    # g.add_edge(3, 4, label=r'$\begin{matrix} x=1\\ y=2\\ z=10 \end{matrix}$')
    # g.add_edge(4, 5)
    # g.add_edge(5, 4, color='red')
    # g.add_edge(2, 2, color='blue')
    # g.add_edge(4, 1)
    G = nx.DiGraph()
    for i in range(8):
        G.add_node(i+1, label='$v_{%d}$' % int(i+1))

    G.add_edge(1, 2, label='2')
    G.add_edge(1, 3, label='6')
    G.add_edge(1, 4, label='5')
    G.add_edge(2, 4, label='3')
    G.add_edge(2, 6, label='9')
    G.add_edge(3, 7, label='4')
    G.add_edge(4, 3, label='4')
    G.add_edge(4, 5, label='6')
    G.add_edge(4, 6, label='7')
    G.add_edge(4, 7, label='2')
    G.add_edge(5, 6, label='2')
    G.add_edge(6, 8, label='3')
    G.add_edge(7, 8, label='7')



    # G.add_edges_from([('A', 'B'), ('C', 'D'), ('G', 'D')], weight=1)
    # G.add_edges_from([('D', 'A'), ('D', 'E'), ('B', 'D'), ('D', 'E')], weight=2)
    # G.add_edges_from([('B', 'C'), ('E', 'F')], weight=3)
    # G.add_edges_from([('C', 'F')], weight=4)
    #
    # val_map = {'A': 1.0,
    #            'D': 0.5714285714285714,
    #            'H': 0.0}
    #
    # values = [val_map.get(node, 0.45) for node in G.nodes()]
    # edge_labels = dict([((u, v,), d['weight'])
    #                     for u, v, d in G.edges(data=True)])
    # red_edges = [('C', 'D'), ('D', 'A')]
    # edge_colors = ['black' if not edge in red_edges else 'red' for edge in G.edges()]
    #
    # pos = nx.spring_layout(G)
    # nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    # nx.draw(G, pos, node_color=values, node_size=1500, edge_color=edge_colors, edge_cmap=plt.cm.Reds)
    #
    # #plt.show()

    return G


if __name__ == '__main__':
    write_tikz()