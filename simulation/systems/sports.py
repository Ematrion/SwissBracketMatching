from typing import Dict, List
from rstt.stypes import SPlayer, Solver
from rstt import Duel, Ranking, Competition, RoundRobin
import random

def qualify(standing: dict[SPlayer, int], top: int):
    if len(standing) < top:
        raise ValueError(f"standing to small: {len(standing)}, top={top}")
    qualified = []
    place=0
    while len(qualified) != top:
        place += 1
        candidates = [team for team, stand in standing.items() if stand == place]
        if len(candidates) + len(qualified) <= top:
            qualified += candidates
        else:
            candidates = random.sample(candidates, top-len(qualified))
            qualified += candidates
    return qualified    
        
    
    
class GroupStage4(Competition):
    # !!! Not a clean reusable implementation
    def __init__(self, name: str, seeding: Ranking, solver: Solver):
        super().__init__(name, seeding, solver)
        self.groups = [RoundRobin(f"{name} group {i+1}", seeding, solver) for i in range(4)]
        self.groups[0].registration(seeding[[0,7,8,15]]) # type: ignore
        self.groups[1].registration(seeding[[1,6,9,14]]) # type: ignore
        self.groups[2].registration(seeding[[2,5,10,13]]) # type: ignore
        self.groups[3].registration(seeding[[3,4,11,12]]) # type: ignore
        
        self.current: int = 0
        
    def run(self):
        for group in self.groups:
            group.run()
        self.trophies()   
        
    def games(self, by_rounds=False):
        return [game for group in self.groups for game in group.games(by_rounds)]
    
    def _standing(self) -> Dict[SPlayer, int]:
        # for example: each first of group becomes a top4 of the competition
        mult = 4
        nb_per_group = 2
        standing = {}
        for group in self.groups:
            for team, place in group.standing().items():
                standing[team]= place*mult
            qualified = qualify(group.standing(), nb_per_group)
            for team in qualified:
                standing[team] = min(mult*group.standing()[team], 8)
            
        
        return standing

    def generate_games(self) -> List[Duel]:
        raise NotImplementedError
    
    def _end_of_stage(self) -> bool:
        raise NotImplementedError
    
    def _update(self) -> None:
        raise NotImplementedError
    

class GroupStage8(Competition):
    # !!! Not a clean reusable implementation
    def __init__(self, name: str, seeding: Ranking, solver: Solver):
        super().__init__(name, seeding, solver)
        self.groups = [RoundRobin(f"{name} group {i+1}", seeding, solver) for i in range(2)]
        self.groups[0].registration(seeding[[0,7,8,15]+[3,4,11,12]]) # type: ignore
        self.groups[1].registration(seeding[[1,6,9,14]+[2,5,10,13]]) # type: ignore

        self.current: int = 0
        
    def run(self):
        for group in self.groups:
            group.run()
        self.trophies()   
    
    def games(self, by_rounds=False):
        return [game for group in self.groups for game in group.games(by_rounds)]

    def _standing(self) -> Dict[SPlayer, int]:
        mult = 2
        nb_per_group = 4
        standing = {}
        for group in self.groups:
            for team, place in group.standing().items():
                standing[team]= place*mult
            qualified = qualify(group.standing(), nb_per_group)
            for team in qualified:
                standing[team] = min(mult*group.standing()[team], 8)
        return standing

    def generate_games(self) -> List[Duel]:
        raise NotImplementedError
    
    def _end_of_stage(self) -> bool:
        raise NotImplementedError
    
    def _update(self) -> None:
        raise NotImplementedError
        
    


if __name__ == "__main__":
    from rstt import BasicPlayer, BTRanking, LogSolver
    from simulation.baseline import load_population, qualification_probabilities
    from evaluation.prob_metrics import top8_index
    
    testModel = 'Pareto'
    
    pop = load_population("/Users/dbucher/Documents/GitHub/SwissBracketMatching/simulation/population")
    gt = pop[testModel]
    solver = LogSolver()
    qp = qualification_probabilities({testModel: gt}, 10)
    
    for i in range(1000):
        g44 = GroupStage4(f'test_{i}', gt, solver)
        g44.run()
        g28 = GroupStage8(f'test_{i}', gt, solver)
        g28.run()

        assert len(top8_index(g44.standing(), gt)) == 8, f"{i}, {len(top8_index(g44.standing(), gt))}"
        assert len(top8_index(g28.standing(), gt)) == 8, f"{i}, {len(top8_index(g28.standing(), gt))}"
        
    print("test succeed !!!")