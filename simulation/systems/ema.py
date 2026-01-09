from typing import Dict, Tuple
from rstt.scheduler.tournament.swissbracket import DummyParam
from rstt.stypes import Evaluator, Generator, Seeder, Shuffler, Solver# Seeder, Shuffler, Generator, Evaluator
from rstt import BetterWin, Ranking, SwissBracket
from systems.tiebreaker import TieBreakReSeeder

from systems.csmajor import Chord6

from ema.gtypes import Matching
import ema.algorithm as alg
from ema.coverings import FLAT, STAR

class K44:
    def __init__(self, expected: Matching = [(1, 6), (2, 5), (3, 4)]):
        self.expected = expected
        extended = alg.one_more_edge(expected, *alg.new_vertex())
        covering = alg.roll_match(extended)
        self.matchings = [alg.relabelling(matching) for matching in covering.values()]
        
    def generate(self, status: list[int]):
        # fix formats of returns and labels from status
        return self.matchings


class InOutGen:
    def __init__(self, inside: Generator, outside: Generator, size: int):
        self.size = size
        self.inside = inside
        self.outside = outside
        
    def generate(self, status: list[int]):
        n = len(status)
        start = (n - self.size) // 2
        end = start + self.size
        inners = self.inside.generate(status=status[start: end])
        outers = self.outside.generate(status=status[:start]+status[end:])
        return [inner+outer for inner, outer in zip(inners, outers)]
        

class EMA(SwissBracket):
    def __init__(self, name: str, seeding: Ranking, solver: Solver):
        k44 = K44(Chord6().generate(list(range(6)))[0]) # Valve Priority
        super().__init__(name=name, seeding=seeding, solver=solver,
                         generators={(0,0): InOutGen(k44), # type: ignore
                                     (1,1): k44},
                         )