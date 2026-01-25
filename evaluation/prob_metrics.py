from rstt import Ranking, Competition

def utility_loss_from_cup(cup: Competition, reference: Ranking, prob: dict[int, float]):
    """Not used - utility loss requires P_fair probabilities."""
    raise NotImplementedError()