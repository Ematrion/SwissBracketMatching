from rstt.stypes import Solver # Seeder, Shuffler, Generator, Evaluator
from rstt import Ranking, SwissBracket
from simulation.systems.tiebreaker import TieBreakReSeeder
import utils

class GenR1R2:
    def generate(self, status: list[int]):
        return [utils.flat_match(status), utils.cross_match(status)]

class Chord6:
    def generate(self, status: list[int]):
        return utils.swiss_bracket_n6(status)

class GrahamPittExample(SwissBracket):
    '''
    Mimics the example:
        https://x.com/messioso/status/1644389658942373899
    '''
    def __init__(self, name: str, seeding: Ranking, solver: Solver):
        tbrs = TieBreakReSeeder(seeding=seeding, policies=['solkoff'])
        chord6 = Chord6()
        generators={(1,1): GenR1R2(),
                    (2,2): chord6,
                    (2,1): chord6,
                    (1,2): chord6,
                   }
        super().__init__(name=name, seeding=seeding, solver=solver,
                         # --- matching --- #
                         generators=generators,
                         def_seeder=tbrs, # type: ignore 
                        )
        self.registration([p for p in seeding])
        
        
from rstt.utils import utils as uu, matching as um, competition as uc

class SpeedUp:
    def generate(self, status: list[int]):
        return [utils.speed_up(status)]

class GrahamPittSolution(GrahamPittExample):
    '''
    Implement the speedup trick proposed at:
        https://x.com/messioso/status/1644391221945683968
    '''
    def __init__(self, name: str, seeding: Ranking, solver: Solver):
        super().__init__(name=name, seeding=seeding, solver=solver)
        #self.def_evaluator = self.def_seeder
        self.generators[(0,0)] = SpeedUp() # type: ignore
        
        