from typing import Dict, List
from rstt.stypes import SPlayer, Solver
from rstt import BetterWin, Duel, Ranking, Competition, RoundRobin

    
    
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
        return {player: group.standing()[player]*4 for group in self.groups for player in group.participants()}

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
        # for example: each first of group becomes a top4 of the competition
        return {player: group.standing()[player]*2 for group in self.groups for player in group.participants()}

    def generate_games(self) -> List[Duel]:
        raise NotImplementedError
    
    def _end_of_stage(self) -> bool:
        raise NotImplementedError
    
    def _update(self) -> None:
        raise NotImplementedError
        
    
