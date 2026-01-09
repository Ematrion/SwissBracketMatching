from ema.gtypes import Covering #Edge, Matching, 
from ema.completebipartite import CompleteBiPartite as CBG

import networkx as nx
import itertools


def get_cycles_per_nb_colors(graph: nx.Graph, nbc: int):
    ...
    
def same_coverings(covering1: Covering, covering2: Covering):
    rounds_1 = set([tuple(round) for round in covering1.values()])
    rounds_2 = set([tuple(round) for round in covering2.values()])
    return rounds_1 == rounds_2

def cycle_basis_analysis(covering: Covering):
    graph = CBG(n=8)
    graph.set_edges_color(covering)
    cycles = nx.cycle_basis(graph.graph)
    
    results = []
    for cycle in cycles:
        colors = []
        for i, node in enumerate(cycle):
            c = graph.coloring[(node, cycle[(i+1)%len(cycle)])]
            colors.append(c)
        results.append((cycle, colors, len(set(colors))))
    return results

def bad_scenarios(top, bot, c_top, c_bot) -> list[tuple[int, int]]:
    scenarios = list(itertools.product(top, bot)) + list(itertools.product(c_top, c_bot))
    scenarios.sort()
    return scenarios

def predictions(name: str, edges: list[int], colors: list[int]):
    # K4,4 context
    all_colors = {0,1,2,3}
    all_tops = {1,2,3,4}
    all_bottoms = {5,6,7,8}

    # input process
    edges.sort()
    top, bot = set(edges[:2]), set(edges[2:])
    colors = set(colors) # type: ignore
    
    # paired cycle
    c_top = all_tops - top
    c_bot = all_bottoms - bot

    # complementary cycles
    c_colors = all_colors - colors #type: ignore

    # colors notation in dataframe
    c1 = tuple(sorted(colors))
    c2 = tuple(sorted(c_colors))

    # predict problematic scenarios
    scenarios1 = bad_scenarios(top, bot, c_top, c_bot)
    scenarios2 = bad_scenarios(top, c_bot, c_top, bot)

    return {((name, c1), scenario) for scenario in scenarios1}.union({((name, c2), scenario) for scenario in scenarios2})