from rstt import BTRanking, SwissBracket, Duel, WIN, LOSE
from rstt.solver import ScoreProb
from rstt.stypes import Solver, SPlayer, Score  

import warnings


class FairCompare:
    def __init__(self, solver: Solver):
        self._solver = solver
        self.past: dict[SPlayer, dict[SPlayer, Score]] = {}
        
    def solve(self, duel: Duel, *args, **kwargs):
        p1, p2 = duel.players()
        score = self._past_score(p1, p2)
        if score:
            self._assign_score(duel, score)
        else:
            # never seen matchups, get a result
            self._solver.solve(duel)
            # remember it
            if not p1 in self.past:
                self.past[p1] = {}
            self.past[p1][p2] = duel.scores()
            
    def _past_score(self, p1: SPlayer, p2: SPlayer) -> Score | None:
        score = None
        if p1 in self.past:
            if p2 in self.past[p1]:
                score = self.past[p1][p2]
        elif p2 in self.past:
            if p1 in self.past[p2]:
                score = self.past[p2][p1]
                score = WIN if score == LOSE else LOSE # inverse outcome
        return score
    
    def _assign_score(self, duel: Duel, score: Score) -> None:
        duel._Match__set_result(result=score) # type: ignore
    

def protocol(systems: dict[str, type[SwissBracket]], models: dict[str, BTRanking], solvers: dict[str, Solver], seedings: dict[str, tuple[int]]):
    results = {variant: {solver: {model: {seed_cat: {} 
                                       for seed_cat in seedings} 
                               for model in models} 
                      for solver in solvers}
            for variant in systems}
    warned = []
    
    for s, solver in solvers.items(): 
        for m, model in models.items():
            for seed_class, seeds in seedings.items():
                for seed in seeds:
                    # fix rng between systems
                    solver = FairCompare(solver=solver) # type: ignore
                    
                    # run for each system alternatives
                    for v, variant in systems.items():
                        seeding = BTRanking(f'{seed}', model.players())
                        seeding.rerank(seed)
                        
                        cup = variant(f'{v}-{s}-{m}-{seed_class}-{seed}', seeding, solver) #type: ignore
                        cup.registration(model.players())
        
                        with warnings.catch_warnings(record=True) as w:
                            warnings.simplefilter("always")
                            cup.run()
        
                        if w:
                            warned.append(seed)
                        results[v][s][m][seed_class][seed] = cup

    return results, warned