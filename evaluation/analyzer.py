from evaluation import cup_metrics as cm

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr

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
        
    def extract_qualified_teams(self, cup, population):
        """
        Extract which teams qualified from a cup object.
        Returns two lists:
        - seed_indices: positions in seeding (0-15)
        - level_ranks: positions in true level ranking (0-15)
        
        Parameters:
        -----------
        cup : tournament object
            Has .standing() -> dict {Player: final_rank}
            Has .seeding -> Ranking object
        population : str
            Population name to get correct ground truth ranking
        """
        standing = cup.standing()
        seeding = cup.seeding
        gt_ranking = self.ground_truth_rankings[population]
        
        seed_indices = []
        level_ranks = []
        
        # Get players who qualified (rank <= 8)
        for player, final_rank in standing.items():
            if final_rank <= 8:
                # Get seed position (0-15)
                seed_idx = seeding[player]
                seed_indices.append(seed_idx)
                
                # Get true level rank (0-15)
                level_rank = gt_ranking[player]
                level_ranks.append(level_rank)
        
        return seed_indices, level_ranks
   
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
                    
                    # Get fair probabilities for this population (indexed by level rank)
                    P_fair = np.array([self.models_probabilities[population][i] 
                                        for i in range(16)])
                    
                    for seeding_class, seed_dict in seed_class_dict.items():
                        for seed, cup in seed_dict.items():
                            
                            # Extract qualified teams (both seed and level perspectives)
                            seed_indices, level_ranks = self.extract_qualified_teams(cup, population)
                            
                            # Seed-based: which seed positions (0-7) qualified?
                            Q_seed = np.array([1 if i in seed_indices else 0 
                                                for i in range(16)])
                            
                            # Level-based: which level ranks (0-7 = true best) qualified?
                            Q_level = np.array([1 if i in level_ranks else 0 
                                                for i in range(16)])
                            
                            # In the loop, pass cup and population to _compute_single_run_metrics:
                            metrics_seed = self._compute_single_run_metrics( P_fair, Q_seed,
                                    seed_indices, perspective='seed', cup=cup, population=population)

                            metrics_level = self._compute_single_run_metrics(P_fair, Q_level, level_ranks,
                                perspective='level',cup=cup, population=population)
                            
                            # Combine metrics with prefixes
                            metrics = {
                                **{f'seed_{k}': v for k, v in metrics_seed.items()},
                                **{f'level_{k}': v for k, v in metrics_level.items()}
                            }
                            
                            # Store configuration info
                            metrics.update({
                                'system': system,
                                'generator': generator,
                                'population': population,
                                'seeding_class': seeding_class,
                                'seed': str(seed),  # Convert tuple to string
                            })
                            
                            records.append(metrics)
        
        self.metrics_df = pd.DataFrame(records)
        return self.metrics_df
     
    def _compute_single_run_metrics(self, P_fair, Q_observed, qualified_indices, perspective, cup, population):
        """
        Compute all metrics for a single run using individual metric functions.
        
        Parameters:
        -----------
        P_fair : array
            Fair qualification probabilities indexed by level rank
        Q_observed : array
            Binary vector of who actually qualified
        qualified_indices : list
            List of indices that qualified
        perspective : str
            'seed' or 'level'
        cup : Competition, optional
            Cup object for game-based metrics
        population : str, optional
            Population name
        
        Returns:
        --------
        dict : All computed metrics
        """
        # Qualification-based metrics
        utility_loss = np.sum(P_fair * (1 - Q_observed))
        max_score = np.sum(P_fair[:8])
        normalized_utility_loss = utility_loss / max_score
        
        true_top8 = set(range(8))
        precision = len(true_top8 & set(qualified_indices)) / 8
        
        weighted_precision = np.sum([P_fair[i] for i in qualified_indices]) / np.sum(P_fair)
        
        fair_ranks = np.argsort(np.argsort(P_fair)[::-1])
        observed_ranks = np.argsort(np.argsort(Q_observed)[::-1])
        spearman_corr, _ = spearmanr(fair_ranks, observed_ranks)
        kendall_corr, _ = kendalltau(fair_ranks, observed_ranks)
        
        false_negatives = np.sum([P_fair[i] for i in range(16) if P_fair[i] > 0.5 and i not in qualified_indices])
        false_positives = np.sum([1 - P_fair[i] for i in qualified_indices if P_fair[i] < 0.5])
        misclass_cost = false_negatives + false_positives
        
        metrics = {
            'utility_loss': utility_loss,
            'normalized_utility_loss': normalized_utility_loss,
            'top8_precision': precision,
            'weighted_precision': weighted_precision,
            'spearman_corr': spearman_corr,
            'kendall_corr': kendall_corr,
            'misclass_cost': misclass_cost,
        }
        
        # Get appropriate reference ranking
        reference = (self.ground_truth_rankings[population] if perspective == 'level' else cup.seeding)
        
        # Call individual metric functions
        metrics['fairness'] = cm.fairness_from_cup(cup, reference)
        metrics['balance'] = cm.balance_from_cup(cup, reference)
        metrics['last_round_fairness'] = cm.last_round_fairness_from_cup(cup, reference)
        metrics['last_round_balance'] = cm.last_round_balance_from_cup(cup, reference)
        metrics['upset_rate'] = cm.upset_rate_from_cup(cup, reference)
        metrics['frustration'] = cm.frustration_from_cup(cup, reference)
        metrics['avg_competitiveness'] = cm.avg_competitiveness_from_cup(cup, reference, self.models_probabilities[population])

        return metrics
    