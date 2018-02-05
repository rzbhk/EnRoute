from itertools import islice
import networkx as nx


def k_shortest_paths(no_of_cameras,k,G):
    """
    :param no_of_cameras: number of cameras
    :param k: number of shortest paths to extract
    :param G: the networkx graph on which the shortest paths are extracted
    :return: a 2d list, a[i][j] = list of k shortest paths and their total weight (in a tuple format)
    """
    a = [[list() for i in range(no_of_cameras)] for j in range(no_of_cameras)]
    for i in range(no_of_cameras):
        for j in range(no_of_cameras):
            if j != i:
                k_shortest = islice(nx.shortest_simple_paths(G, i, j, weight="weight"), k)
                for path in k_shortest:
                    a[i][j].append((path, sum([G.get_edge_data(path[l], path[l + 1])["weight"] for l in range(len(path) - 1)])))
    return a