from typing import Dict, Tuple
from rstt.scheduler.tournament.swissbracket import DummyParam
from rstt.stypes import Evaluator, Generator, Seeder, Shuffler, Solver# Seeder, Shuffler, Generator, Evaluator
from rstt import BetterWin, Ranking, SwissBracket
from systems.tiebreaker import TieBreakReSeeder

from systems.csmajor import Chord6

from ema.gtypes import Matching
import ema.algorithm as alg
from ema.coverings import FLAT, STAR

import itertools


K33_PM = {}
K33_PM .update(FLAT)
K33_PM .update(STAR)



class InOutGen:
    def __init__(self, inside: Generator, outside: Generator, size: int):
        self.size = size
        self.gen_inside = inside
        self.gen_outside = outside
        
    def generate(self, status: list[int]):
        n = len(status)
        start = (n - self.size) // 2
        end = start + self.size
        inners = self.gen_inside.generate(status=status[start: end])
        outers = self.gen_outside.generate(status=status[:start]+status[end:])
        return [ins + outs for ins, outs in itertools.product(inners, outers)]


class K44:
    def __init__(self, expected: Matching = [(1, 6), (2, 5), (3, 4)]):
        self.expected = expected
        extended = alg.one_more_edge(expected, *alg.new_vertex())
        covering = alg.roll_match(extended)
        self.matchings = [alg.relabelling(matching) for matching in covering.values()]
        
    def generate(self, status: list[int]):
        # fix formats of returns and labels from status
        return self.matchings

class EMA:
    def __init__(self, approach: str, perfect_matching: str, ordering: list[int]):
        self.name = perfect_matching
        self.approach = approach
        self.matching = K33_PM[perfect_matching]
        self.options = self.expected_matching_approach()
            
    def expected_matching_approach(self):
        u, v = alg.new_vertex()
        extended = alg.one_more_edge(self.matching, u, v)
        
        if self.approach == 'ROT':
            round_pairings = {k: alg.relabelling(v) for k,v in alg.roll_match(extended).items()}
        elif self.approach == 'CROSS':
            opposite = STAR if self.name.startswith('F') else FLAT
            round_pairings = [alg.relabelling(extended)]
            round_pairings += [alg.relabelling(alg.mixture(self.matching, op2, u, v)) for op2 in opposite.values()]
        else:
            msg = f"Invalide value of approach, received: {self.approach}, must be in \"ROT\" or \"CROSS\""
            raise ValueError(msg)
        
        return round_pairings

"""class EMA(SwissBracket):
    def __init__(self, name: str, seeding: Ranking, solver: Solver):
        k44 = K44(Chord6().generate(list(range(6)))[0]) # Valve Priority
        super().__init__(name=name, seeding=seeding, solver=solver,
                         generators={(0,0): InOutGen(k44), # type: ignore
                                     (1,1): k44},
                         )
"""
        
class EMARound(SwissBracket):
    def __init__(self, name, seeding):
        super().__init__(name, seeding)