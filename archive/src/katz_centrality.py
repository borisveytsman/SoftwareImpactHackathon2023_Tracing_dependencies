# SPDX-FileCopyrightText: 2023 Brown, E. M., Nesbitt, A., Hébert-Dufresne, L., Veytsman, B., Pimentel, J. F., Druskat, S., Mietchen, D., Howison, J.
#
# SPDX-License-Identifier: MIT

import networkx as nx

def get_katz_centrality(graph):
    
    # Calculate max eigenvalue of adjacency matrix for convergence
    phi = max(nx.adjacency_spectrum(graph, weight= 'weight'))
    # Iterative calculation of Katz centrality (beta is the importance of papers)
    centrality = nx.katz_centrality(G, alpha = 1 / phi - 0.01, beta=1.0,  weight= 'weight',  max_iter = 100000)

    # Returns the dictionary containing the centrality of each node
    return centrality