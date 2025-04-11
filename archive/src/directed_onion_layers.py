# SPDX-FileCopyrightText: 2023 Brown, E. M., Nesbitt, A., Hébert-Dufresne, L., Veytsman, B., Pimentel, J. F., Druskat, S., Mietchen, D., Howison, J.
#
# SPDX-License-Identifier: MIT

import networkx as nx

def directed_onion_layers(graph):

    # Dictionaries to register the k-core/onion decompositions. 
    bicoreness_map = {}
    bilayer_map = {}

    # Creates a copy of the graph (to be able to remove vertices and edges)
    the_graph = nx.MultiDiGraph(graph)

    # Performs the inward onion decomposition (low in degree first).
    current_core = 0
    current_layer = 1
    while the_graph.number_of_nodes() > 0:
        # Sets properly the current core.
        degree_sequence = [min(the_graph.in_degree(node),the_graph.in_degree(node)) for node in the_graph.nodes()]
        min_degree =  min(degree_sequence)
        if min_degree >= (current_core+1):
            current_core = min_degree
        # Identifies vertices in the current layer.
        this_layer_ = []
        for v in the_graph.nodes():
            if the_graph.in_degree(v) <= current_core or the_graph.out_degree(v) <= current_core:
                this_layer_.append(v)
        # Identifies the core/layer of the vertices in the current layer.
        for v in this_layer_:
            bicoreness_map[v] = current_core
            bilayer_map[v] = current_layer
            the_graph.remove_node(v)
        # Updates the layer count.
        current_layer = current_layer + 1

    # Returns the dictionaries containing the k-shell and onion layer of each vertices.
    return (bilayer_map, bicoreness_map)

def bidirectional_onion_layers(graph):

    # Dictionaries to register the k-core/onion decompositions. 
    incoreness_map = {}
    inlayer_map = {}
    outcoreness_map = {}
    outlayer_map = {}

    # Creates a copy of the graph (to be able to remove vertices and edges)
    the_graph = nx.MultiDiGraph(graph)

    # Performs the inward onion decomposition (low in degree first).
    current_core = 0
    current_layer = 1
    while the_graph.number_of_nodes() > 0:
        # Sets properly the current core.
        indegree_sequence = [the_graph.in_degree(node) for node in the_graph.nodes()]
        min_degree =  min(indegree_sequence)
        if min_degree >= (current_core+1):
            current_core = min_degree
        # Identifies vertices in the current layer.
        this_layer_ = []
        for v in the_graph.nodes():
            if the_graph.in_degree(v) <= current_core:
                this_layer_.append(v)
        # Identifies the core/layer of the vertices in the current layer.
        for v in this_layer_:
            incoreness_map[v] = current_core
            inlayer_map[v] = current_layer
            the_graph.remove_node(v)
        # Updates the layer count.
        current_layer = current_layer + 1

    # Creates a 2nd copy of the graph (to be able to remove vertices and edges)
    the_graph = nx.MultiDiGraph(graph)

    # Performs the outward onion decomposition (low out degree first).
    current_core = 0
    current_layer = 1
    while the_graph.number_of_nodes() > 0:
        # Sets properly the current core.
        outdegree_sequence = [the_graph.out_degree(node) for node in the_graph.nodes()]
        min_degree =  min(outdegree_sequence)
        if min_degree >= (current_core+1):
            current_core = min_degree
        # Identifies vertices in the current layer.
        this_layer_ = []
        for v in the_graph.nodes():
            if the_graph.out_degree(v) <= current_core:
                this_layer_.append(v)
        # Identifies the core/layer of the vertices in the current layer.
        for v in this_layer_:
            outcoreness_map[v] = current_core
            outlayer_map[v] = current_layer
            the_graph.remove_node(v)
        # Updates the layer count.
        current_layer = current_layer + 1


    # Returns the dictionaries containing the k-shell and onion layer of each vertices.
    return (inlayer_map, incoreness_map, outlayer_map, outcoreness_map)