from rstt import Ranking, Competition


def fairness_from_cup(cup: Competition, reference: Ranking):
    """
    Compute fairness: average rank of winners across all games.
    Lower is better (stronger teams winning).
    
    Parameters:
    -----------
    cup : Competition
        Tournament object with .games() method
    reference : Ranking
        Either ground truth ranking (level perspective) or seeding (seed perspective)
    
    Returns:
    --------
    float : Average winner rank
    """
    fairness_sum = sum([reference[duel.winner()] for duel in cup.games(by_rounds=False)]) # type: ignore
    return fairness_sum / len(cup.games(by_rounds=False))

def balance_from_cup(cup: Competition, reference: Ranking):
    """
    Compute balance: average rank difference between opponents.
    Lower is better (more evenly matched games).
    
    Parameters:
    -----------
    cup : Competition
    reference : Ranking
    
    Returns:
    --------
    float : Average rank difference
    """
    balance_sum = sum([abs(reference[duel.winner()] - reference[duel.loser()]) for duel in cup.games(by_rounds=False)]) # type: ignore
    return balance_sum / len(cup.games(by_rounds=False))

def last_round_fairness_from_cup(cup: Competition, reference: Ranking):
    """
    Compute fairness for last round only.
    
    Parameters:
    -----------
    cup : Competition
    reference : Ranking
    
    Returns:
    --------
    float : Average winner rank in last round
    """
    last_round = cup.games(by_rounds=True)[-1]
    fairness_sum = sum(reference[duel.winner()] for duel in last_round) # type: ignore
    return fairness_sum / len(last_round) # type: ignore

def last_round_balance_from_cup(cup: Competition, reference: Ranking):
    """
    Compute balance for last round only.
    
    Parameters:
    -----------
    cup : Competition
    reference : Ranking
    
    Returns:
    --------
    float : Average rank difference in last round
    """
    last_round = cup.games(by_rounds=True)[-1]        
    balance_sum = sum([abs(reference[duel.winner()] - reference[duel.loser()]) for duel in last_round]) # type: ignore
    return balance_sum / len(last_round) # type: ignore

def upset_rate_from_cup(cup: Competition, reference: Ranking):
    """
    Compute upset rate: fraction of games where lower-ranked team won.
    
    Parameters:
    -----------
    cup : Competition
    reference : Ranking
    
    Returns:
    --------
    float : Upset rate (0-1)
    """
    all_games = cup.games(by_rounds=False)
    upsets = [duel for duel in all_games if reference[duel.winner()] > reference[duel.loser()]] # type: ignore
    return len(upsets) / len(all_games)

def frustration_from_cup(cup, reference):
    """
    Compute frustration: count of pairs where better team beat worse team but didn't qualify.
    
    A frustration occurs when:
    - Team A beats Team B in a game
    - Team A has better rank than Team B (in reference ranking)
    - Team B qualifies but Team A does not
    
    Parameters:
    -----------
    cup : Competition
        Tournament object with .games() and .standing() methods
    reference : Ranking
        Either ground truth ranking (level perspective) or seeding (seed perspective)
    
    Returns:
    --------
    int : Number of frustrating pairs
    """
    all_games = cup.games(by_rounds=False)
    standing = cup.standing()
    
    # Get qualified teams (final rank <= 8)
    qualified = {player for player, rank in standing.items() if rank <= 8}
    
    frustrations = 0
    
    for duel in all_games:
        winner = duel.winner()
        loser = duel.loser()
        
        winner_rank = reference[winner]
        loser_rank = reference[loser]
        
        # Check if winner has better (lower) rank than loser
        if winner_rank < loser_rank:
            # Frustration: better team won but didn't qualify, while worse team did
            if loser in qualified and winner not in qualified:
                frustrations += 1
    
    return frustrations

def avg_competitiveness_from_cup(cup: Competition, reference: Ranking, qprob: dict[int, float]):
    """
    Compute average game competitiveness using model probabilities.
    Only meaningful for level perspective.
    
    Parameters:
    -----------
    cup : Competition
    population : str
        Population name to get model probabilities
    
    Returns:
    --------
    float : Average win probability of winners
    """
    all_games = cup.games(by_rounds=False)

    competitiveness_sum = 0
    for duel in all_games:
        winner_level_rank = reference[duel.winner()] # type: ignore
        loser_level_rank = reference[duel.loser()] # type:ignore
        
        qualif_prob_winner = qprob[winner_level_rank] # type:ignore
        qualif_prob_loser = qprob[loser_level_rank] # type:ignore
        
        total_strength = qualif_prob_winner + qualif_prob_loser
        win_prob = qualif_prob_winner / total_strength if total_strength > 0 else 0.5
        
        competitiveness_sum += win_prob
    
    return competitiveness_sum / len(all_games)
