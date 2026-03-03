from functools import wraps

import numpy as np
from scipy.stats import spearmanr, kendalltau
from rstt import Ranking, Competition



# ---- Utility ---- #
def _extract_qualification_data(cup: Competition, reference: Ranking, prob: dict[int, float]):
    """Shared extraction: P_fair, Q_observed, qualified_indices from cup results."""
    standing = cup.standing()
    P_fair = np.array([prob[i] for i in range(16)])

    qualified_indices = []
    for player, final_rank in standing.items():
        if final_rank <= 8:
            qualified_indices.append(reference[player])

    Q_observed = np.array([1 if i in qualified_indices else 0 for i in range(16)])
    return P_fair, Q_observed, qualified_indices

# ---- Metrics ---- #
def utility_loss(cup: Competition, reference: Ranking, prob: dict[int, float]):
    """Utility Loss = max_score - actual_score. 0 when top 8 qualify."""
    P_fair, Q_observed, _ = _extract_qualification_data(cup, reference, prob)
    max_score = np.sum(P_fair[:8])
    actual_score = np.sum(P_fair * Q_observed)
    return max_score - actual_score

def normalized_utility_loss(cup: Competition, reference: Ranking, prob: dict[int, float]):
    """Normalized Utility Loss = utility_loss / max_score."""
    P_fair, Q_observed, _ = _extract_qualification_data(cup, reference, prob)
    max_score = np.sum(P_fair[:8])
    actual_score = np.sum(P_fair * Q_observed)
    return (max_score - actual_score) / max_score

def top8_precision(cup: Competition, reference: Ranking, prob: dict[int, float]):
    """Fraction of qualified teams that are from the reference top 8."""
    _, _, qualified_indices = _extract_qualification_data(cup, reference, prob)
    true_top8 = set(range(8))
    return len(true_top8 & set(qualified_indices)) / 8

def weighted_precision(cup: Competition, reference: Ranking, prob: dict[int, float]):
    """Sum of P_fair for qualified teams, normalized by total P_fair."""
    P_fair, _, qualified_indices = _extract_qualification_data(cup, reference, prob)
    return np.sum([P_fair[i] for i in qualified_indices]) / np.sum(P_fair)

def spearman_correlation(cup: Competition, reference: Ranking, prob: dict[int, float]):
    """Spearman rank correlation between fair ranks and observed qualification ranks."""
    P_fair, Q_observed, _ = _extract_qualification_data(cup, reference, prob)
    fair_ranks = np.argsort(np.argsort(P_fair)[::-1])
    observed_ranks = np.argsort(np.argsort(Q_observed)[::-1])
    corr, _ = spearmanr(fair_ranks, observed_ranks)
    return corr

def kendall_correlation(cup: Competition, reference: Ranking, prob: dict[int, float]):
    """Kendall tau correlation between fair ranks and observed qualification ranks."""
    P_fair, Q_observed, _ = _extract_qualification_data(cup, reference, prob)
    fair_ranks = np.argsort(np.argsort(P_fair)[::-1])
    observed_ranks = np.argsort(np.argsort(Q_observed)[::-1])
    corr, _ = kendalltau(fair_ranks, observed_ranks)
    return corr

def misclassification_cost(cup: Competition, reference: Ranking, prob: dict[int, float]):
    """Weighted count of false negatives (P_fair > 0.5 not qualified) and false positives (P_fair < 0.5 qualified)."""
    P_fair, _, qualified_indices = _extract_qualification_data(cup, reference, prob)
    false_negatives = np.sum([P_fair[i] for i in range(16) if P_fair[i] > 0.5 and i not in qualified_indices])
    false_positives = np.sum([1 - P_fair[i] for i in qualified_indices if P_fair[i] < 0.5])
    return false_negatives + false_positives
