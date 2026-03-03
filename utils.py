from typing import Callable
import itertools

import ema.algorithm as ema_alg
from ema.coverings import FLAT, STAR

_K33_MATCHINGS = {**FLAT, **STAR}


def make_k44_coloring(pm: str, alg: str, order: list[int]) -> Callable[[list[int]], list[list]]:
    """
    Dynamically generate a K4,4 coloring function from its parameters.

    Parameters
    ----------
    pm : str
        Starting K3,3 perfect matching ('F1','F2','F3','S1','S2','S3')
    alg : str
        Extension algorithm ('CROSS' or 'ROT')
    order : list[int]
        Permutation of [0,1,2,3] specifying round ordering

    Returns
    -------
    Callable: (players: list[int]) -> list[list]
        Same signature as F1_CROSS_0123 / F1_ROT_0132
    """
    matching = _K33_MATCHINGS[pm]
    u, v = ema_alg.new_vertex()

    if alg == 'ROT':
        extended = ema_alg.one_more_edge(matching, u, v)
        cover = ema_alg.roll_match(extended)
        rounds = [ema_alg.relabelling(m) for m in cover.values()]
    elif alg == 'CROSS':
        opposite = STAR if pm.startswith('F') else FLAT
        rounds = [ema_alg.relabelling(ema_alg.one_more_edge(matching, u, v))]
        rounds += [ema_alg.relabelling(ema_alg.mixture(matching, op, u, v))
                   for op in opposite.values()]
    else:
        raise ValueError(f"alg must be 'ROT' or 'CROSS', got {alg}")

    rounds = [rounds[i] for i in order]

    # Pre-compute index patterns: ema is 1-indexed, utils is 0-indexed
    patterns = []
    for round_edges in rounds:
        sorted_edges = sorted(round_edges, key=lambda e: e[0])
        patterns.append([idx for left, right in sorted_edges for idx in (left - 1, right - 1)])

    def coloring(players: list[int]) -> list[list]:
        return [[players[i] for i in pattern] for pattern in patterns]

    return coloring


def flat_match(elems: list[int]) -> list:
    # [1,2,3,4,5,6,7,8] -> [1,8,2,7,3,6,4,5]
    l = len(elems)
    return [x for i in range(0, l//2) for x in (elems[i], elems[l-(i+1)])]

def cross_match(elems: list[int]) -> list:
    # [1,2,3,4,5,6,7,8] -> [1,7,2,8,3,5,4,6]
    l = len(elems)
    return [x for i in range(0, l//2) for x in (elems[i], elems[l-i] if i%2==1 else elems[l-(i+2)])]

def speed_up(elems: list[int]) -> list:
    # [1,2,3,4,5,6,7,8] -> [1,5,2,6,3,7,4,8]
    l = len(elems)
    return [x for i in range(0, l//2) for x in (elems[i], elems[l//2 + i])]

def swiss_bracket_n6(players: list[int]) -> list[list]:
    '''
    https://github.com/ValveSoftware/counter-strike_rules_and_regs/blob/main/major-supplemental-rulebook.md
    Look for the 'Priority' table in section 'Swiss Bracket'
    '''
    matchings = [
        [players[0], players[5], players[1], players[4], players[2], players[3]],
        [players[0], players[5], players[1], players[3], players[2], players[4]],
        [players[0], players[4], players[1], players[5], players[2], players[3]],
        [players[0], players[4], players[1], players[3], players[2], players[5]],
        [players[0], players[3], players[1], players[5], players[2], players[4]],

        [players[0], players[3], players[1], players[4], players[2], players[5]],
        [players[0], players[5], players[1], players[2], players[3], players[4]],
        [players[0], players[4], players[1], players[2], players[3], players[5]],
        [players[0], players[2], players[1], players[5], players[3], players[4]],
        [players[0], players[2], players[1], players[4], players[3], players[5]],

        [players[0], players[3], players[1], players[2], players[4], players[5]],
        [players[0], players[2], players[1], players[3], players[4], players[5]],
        [players[0], players[1], players[2], players[5], players[3], players[4]],
        [players[0], players[1], players[2], players[4], players[3], players[5]],
        [players[0], players[1], players[2], players[3], players[4], players[5]],
    ]
    return matchings

def F1_CROSS_0123(players: list[int]) -> list[list]:
    matchings = [
        [players[0], players[7], players[1], players[6], players[2], players[5], players[3], players[4]], # red
        [players[0], players[6], players[1], players[7], players[2], players[4], players[3], players[5]], # green
        [players[0], players[5], players[1], players[4], players[2], players[7], players[3], players[6]], # blue
        [players[0], players[4], players[1], players[5], players[2], players[6], players[3], players[7]], # yellow
    ]
    return matchings

def F1_ROT_0132(players: list[int]) -> list[list]:
    matchings = [
        [players[0], players[7], players[1], players[6], players[2], players[5], players[3], players[4]], # red
        [players[0], players[4], players[1], players[7], players[2], players[6], players[3], players[5]], # green
        [players[0], players[6], players[1], players[5], players[2], players[4], players[3], players[7]], # yellow
        [players[0], players[5], players[1], players[4], players[2], players[7], players[3], players[6]], # blue
    ]
    return matchings


class SimpleGen:
    def __init__(self, pairings:  Callable[[list[int]], list[int]]):
        self.pairings = pairings
        
    def generate(self, status: list[int]):
        return self.pairings(status)
    
class R1Ema:
    def __init__(self, generator, split1: list[int], split2: list[int]):
        self.generator = generator
        self.split1 = split1
        self.split2 = split2
    
    def generate(self, status: list[int]):
        group1 = self.generator.generate([status[i] for i in self.split1])
        group2 = self.generator.generate([status[i] for i in self.split2])
        return [ins + outs for ins, outs in itertools.product(group1, group2)]