"""
Simple Directed Graph
"""

__author__  = "Parantapa Bhattacharya <pb@parantapa.net>"
__all__ = ["DiGraph", "load", "save", "make"]

from os import mkdir
from os.path import join, exists
import cPickle as pk

import numpy as np
import staticgraph._edgelist as edgelist

class DiGraph(object):
    """
    Simple Directed Graph

    n_nodes   - # nodes
    n_edges   - # edges
    p_indptr  - index pointers for predecessors
    p_indices - indices of predecessors
    s_indptr  - index pointers for successors
    s_indices - indices for successors
    """

    def __init__(self, n_nodes, n_edges,
                       p_indptr, p_indices,
                       s_indptr, s_indices):

        self.n_nodes   = n_nodes
        self.n_edges   = n_edges
        self.p_indptr  = p_indptr
        self.p_indices = p_indices
        self.s_indptr  = s_indptr
        self.s_indices = s_indices

    def nbytes(self):
        """
        Total bytes used to store internal arrays
        """

        nbytes  = self.p_indptr.nbytes
        nbytes += self.p_indices.nbytes
        nbytes += self.s_indptr.nbytes
        nbytes += self.s_indices.nbytes
        return nbytes

    def successors(self, u):
        """
        Successors of node u
        """

        start = self.s_indptr[u]
        stop  = self.s_indptr[u + 1]
        return self.s_indices[start:stop]

    def predecessors(self, v):
        """
        Predecessors of node v
        """

        start = self.p_indptr[v]
        stop  = self.p_indptr[v + 1]
        return self.p_indices[start:stop]

    def in_degree(self, v):
        """
        In-degree of node v
        """

        start = self.p_indptr[v]
        stop  = self.p_indptr[v + 1]
        return int(stop - start)

    def out_degree(self, u):
        """
        Out-degree of node u
        """

        start = self.s_indptr[u]
        stop  = self.s_indptr[u + 1]
        return int(stop - start)

    def order(self):
        """
        Number of nodes in the graph
        """

        return self.n_nodes

    def size(self):
        """
        Number of edges in the graph
        """

        return self.n_edges

    def nodes(self):
        """
        Iterable that generates the nodes of the graph
        """

        return xrange(self.n_nodes)

    def edges(self):
        """
        Iterable that generates the edges of the graph
        """

        for u in self.nodes():
            for v in self.successors(u):
                yield int(u), int(v)

    def has_node(self, u):
        """
        Check if node u exists
        """

        return (0 <= u < self.n_nodes)

    def has_edge(self, u, v):
        """
        Check if edge (u, v) exists
        """

        return (v in self.successors(u))

def load(store):
    """
    Load a graph from disk
    """

    # Load basic info
    fname = join(store, "base.pickle")
    with open(fname, "rb") as fobj:
        n_nodes, n_arcs = pk.load(fobj)

    # define load shortcut
    do_load = lambda fname : np.load(join(store, fname), "r")

    # Make the arrays
    p_indptr  = do_load("p_indptr.npy")
    p_indices = do_load("p_indices.npy")
    s_indptr  = do_load("s_indptr.npy")
    s_indices = do_load("s_indices.npy")

    # Create the graph
    G = DiGraph(n_nodes, n_arcs, p_indptr, p_indices, s_indptr, s_indices)
    return G

def save(store, G):
    """
    Save the graph G to disk
    """

    # Create the directory
    if not exists(store):
        mkdir(store)

    # Save basic info
    fname = join(store, "base.pickle")
    with open(fname, "wb") as fobj:
        pk.dump((G.n_nodes, G.n_edges), fobj, -1)

    # define save shortcut
    do_save = lambda fname, arr : np.save(join(store, fname), arr)

    # Make the arrays
    do_save("p_indptr.npy", G.p_indptr)
    do_save("p_indices.npy", G.p_indices)
    do_save("s_indptr.npy", G.s_indptr)
    do_save("s_indices.npy", G.s_indices)

def make(n_nodes, edges, count):
    """
    Make a DiGraph

    n_nodes - # nodes in the graph.
              The graph contains all nodes form 0 to (n_nodes - 1)
    edges   - An iterable producing the edges of the graph.
    count   - An over estimate of the number of edges.
    """

    # Create the edgelist
    es = edgelist.make(n_nodes, edges, count)

    # Compact the edgelist
    s_indptr, s_indices = edgelist.compact(n_nodes, es)

    # Swap and sort for getting compact predecessors
    edgelist.swap(es)
    es.sort()

    # Compact the edgelist
    p_indptr, p_indices = edgelist.compact(n_nodes, es)

    # Create the graph
    G = DiGraph(n_nodes, len(es), p_indptr, p_indices, s_indptr, s_indices)
    return G

