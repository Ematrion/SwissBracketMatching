from evaluation import cup_metrics as cm
from evaluation import prob_metrics as pm
from rstt import SwissBracket

import pandas as pd

class TournamentAnalyzer:
    def __init__(self, results, models_probabilities, ground_truth_rankings):
        """
        Parameters:
        -----------
        results : dict
            Nested dict structure: results[system][generator][population][seeding_class][seed] = cup
        models_probabilities : dict
            Pre-computed round-robin qualification probabilities per population
            Format: {population: {level_rank: probability}}
            Where level_rank is 0-15 based on true skill ranking
        ground_truth_rankings : dict
            Ground truth rankings per population: {population: BTRanking}
            Used to map players to their true level rank (0=best, 15=worst)
        """
        self.results = results
        self.models_probabilities = models_probabilities
        self.ground_truth_rankings = ground_truth_rankings
        self.metrics_df = None

    # ==================== MAIN COMPUTATION METHOD ====================
    def compute_metrics(self):
        """
        Compute all fairness metrics for each configuration.
        Returns DataFrame with one row per (system, generator, population, seeding_class, seed).
        """

        records = []

        for system, gen_dict in self.results.items():
            for generator, pop_dict in gen_dict.items():
                for population, seed_class_dict in pop_dict.items():
                    prob = self.models_probabilities[population]
                    gt = self.ground_truth_rankings[population]

                    for seeding_class, seed_dict in seed_class_dict.items():
                        for seed, cup in seed_dict.items():

                            metrics_level = self._compute_single_run_metrics(cup, gt, prob)
                            metrics_seed = self._compute_single_run_metrics(cup, cup.seeding, prob)

                            metrics = {
                                **{f'level_{k}': v for k, v in metrics_level.items()},
                                **{f'seed_{k}': v for k, v in metrics_seed.items()},
                                'system': system,
                                'generator': generator,
                                'population': population,
                                'seeding_class': seeding_class,
                                'seed': str(seed),
                            }

                            records.append(metrics)

        self.metrics_df = pd.DataFrame(records)
        return self.metrics_df

    def _compute_single_run_metrics(self, cup, reference, prob):
        """
        Compute all metrics for a single run.

        Parameters:
        -----------
        cup : Competition
            Tournament object
        reference : Ranking
            Ground truth ranking (level perspective) or seeding (seed perspective)
        prob : dict[int, float]
            Fair qualification probabilities indexed by level rank

        Returns:
        --------
        dict : All computed metrics
        """
        metrics = {
            'utility_loss': pm.utility_loss(cup, reference, prob),
            'normalized_utility_loss': pm.normalized_utility_loss(cup, reference, prob),
            'top8_precision': pm.top8_precision(cup, reference, prob),
            'weighted_precision': pm.weighted_precision(cup, reference, prob),
            'spearman_corr': pm.spearman_correlation(cup, reference, prob),
            'kendall_corr': pm.kendall_correlation(cup, reference, prob),
            'misclass_cost': pm.misclassification_cost(cup, reference, prob),
        }

        metrics['fairness'] = cm.fairness_from_cup(cup, reference)
        metrics['balance'] = cm.balance_from_cup(cup, reference)
        metrics['upset_rate'] = cm.upset_rate_from_cup(cup, reference)
        metrics['frustration'] = cm.frustration_from_cup(cup, reference)
        metrics['avg_competitiveness'] = cm.avg_competitiveness_from_cup(cup, reference, prob)

        # last_round_matching only applies to Swiss brackets
        if isinstance(cup, SwissBracket):
            metrics['last_round_matching'] = cm.last_round_matching_index(cup, reference)
            metrics['last_round_fairness'] = cm.last_round_fairness_from_cup(cup, reference)
            metrics['last_round_balance'] = cm.last_round_balance_from_cup(cup, reference)
        else:
            metrics['last_round_matching'] = None
            metrics['last_round_fairness'] = None
            metrics['last_round_balance'] = None

        return metrics
