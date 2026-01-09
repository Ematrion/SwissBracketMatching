from rstt.stypes import SPlayer
from rstt import Ranking

POINTS = {'win': 1.0,
          'lose': 0.0}


def score(player, results):
    return sum([POINTS[score] for score in results[player]['score']])

def _solkoff(player, results):
    #if len(results[player]['opponent']) == 3 and score(player, results) == 2.0:
    #    print(player.name())
    return sum([score(opponent, results) for opponent in results[player]['opponent']])

def solkoff(results):
    return {player: _solkoff(player, results) for player in results.keys()}

TIEBREAKER = {'solkoff': solkoff,
              }


class TieBreakReSeeder:
    def __init__(self, seeding: Ranking, policies: list[str]):
        self.initial = seeding
        self.policies = policies
        self.operations = [self._method1] #, self._method2, self._method3]

    def seed(self, players: list[SPlayer], initial_seeds: Ranking, results: dict[SPlayer, dict], **kwargs) -> list[SPlayer]:
        # return value, do not impact the original list
        seeds = [p for p in initial_seeds if p in players]

        # compute tiebreakers
        tbs = {policy: TIEBREAKER[policy](results) for policy in self.policies}
        #tbs.update({'initial': {p: self.initial[p] for p in self.initial}})

        # sort
        seeds.sort(key=lambda x: tuple([tbs[policy][x]
                   for policy in self.policies]), reverse=True)
        return seeds

    def eval(self, options: list[list[SPlayer]], initial_seeds: Ranking, results: dict[SPlayer, dict], **kwargs) -> list[list[SPlayer]]:
        # return value, do not impact the original list
        best_options = [option for option in options]

        # compute tiebreakers
        tbs = {policy: TIEBREAKER[policy](results) for policy in self.policies}

        # compute option quality as a tuple
        evaluation = {}
        for option in options:
            eva = []  # store value from different policies
            for policy in self.policies:
                # store value from different game based on same policy
                values = []

                # compute value for each match ups
                for i in range(0, len(option)//2, 2):
                    player1, player2 = option[i], option[i+1]
                    values.append(tbs[policy][player1] - tbs[policy][player2])

            eva += [operation(values) for operation in self.operations]

            evaluation[tuple(option)] = tuple(eva)

        # sort
        best_options.sort(key=lambda x: evaluation[tuple(x)], reverse=True)
        return best_options

    def _method1(self, values: list[float]) -> float:
        return sum(values)

    def _method2(self, values: list[float]) -> float:
        return sum(abs(value) for value in values)

    def _method3(self, values: list[float]) -> float:
        return sum(value*value for value in values)