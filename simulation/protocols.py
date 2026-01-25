from rstt import BasicPlayer, BTRanking, SwissBracket, Duel, WIN, LOSE
from rstt.solver import ScoreProb, LogSolver
from rstt.stypes import Solver, SPlayer, Score  

import warnings



class MinEffort(LogSolver):
    def __init__(self, teams: list[SPlayer], levels: list[float], base: float | None = None, lc: float | None = None,):
        super().__init__(base, lc)
        self.total_round_games = 0
        self.rounds = 0
        
        self.minimalist_teams = {team: BasicPlayer(team.name(), level) for team, level in zip(teams, levels)}
        
    def reset(self):
        self.total_round_games = 0
        self.rounds = 0
        
    def solve(self, duel: Duel, *args, **kwars) -> None:
        if self.rounds < 2:
            # create a replacement game with "underperfoming team instances"
            p1, p2 = duel.players()
            dummy1 = self.minimalist_teams.get(p1, p1)
            dummy2 = self.minimalist_teams.get(p2, p2)
            lazy_duel = Duel(dummy1, dummy2)
            
            # solve the replacement game and transpose result
            super().solve(lazy_duel, *args, **kwars)
            outcome = lazy_duel.scores()
            duel._Match__set_result(result=outcome) # type: ignore
            
            # update round counter
            self.total_round_games += 1
            if self.total_round_games == 8:
                self.total_round_games = 0
                self.rounds += 1
            
        else:
            super().solve(duel, *args, **kwars)
        


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
                    fairsolver = FairCompare(solver=solver) # type: ignore
                    
                    # run for each system alternatives
                    for v, variant in systems.items():
                        seeding = BTRanking(f'{seed}', model.players())
                        seeding.rerank(seed)
                        
                        cup = variant(f'{v}-{s}-{m}-{seed_class}-{seed}', seeding, fairsolver) #type: ignore
                        cup.registration(model.players())
        
                        with warnings.catch_warnings(record=True) as w:
                            warnings.simplefilter("always")
                            cup.run()
        
                        if w:
                            warned.append(seed)
                        results[v][s][m][seed_class][seed] = cup

    return results, warned