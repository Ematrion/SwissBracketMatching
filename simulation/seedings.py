import random
from copy import copy

import numpy as np
from scipy.stats import spearmanr, kendalltau
import matplotlib.pyplot as plt
import seaborn as sns

def shake_seed(segments: list[list[int]], nb: int) -> set[tuple]:
    sgmts = [copy(seg) for seg in segments]
    
    variants = set()
    while len(variants) < nb:
        variant = []
        for segment in sgmts:
            random.shuffle(segment)
            variant += segment
        variants.add(tuple(variant))
    return list(variants) # type:ignore



def seeding_classes(nbv: int):
    seeds_values = list(range(0, 16))

    # segments
    h1 = seeds_values[:8]
    h2 = seeds_values[8:]
    top4 = seeds_values[:4]
    bottom4 = seeds_values[-4:]
    mid8 = seeds_values[4:-4]
    mid6 = seeds_values[5:-5]
    top5 = seeds_values[:5]
    bottom5 = seeds_values[-5:]

    correct_halves = shake_seed([h1, h2], nb=nbv)
    prior_mid = shake_seed([top4, mid8, bottom4], nb=nbv) # middle 8 teams
    post_mid = shake_seed([top5, mid6, bottom5], nb=nbv) # middle 6 teams
    random_seeds = shake_seed([seeds_values], nb=nbv)
    return {'ACR2': correct_halves, 'ACR3': prior_mid, 'ACR5': post_mid, 'RANDOM': random_seeds}


def rank_corr(seed):
    ref = np.arange(len(seed))
    return kendalltau(ref, seed).correlation #type: ignore

def top8_accuracy(seed):
    true_top8 = set(range(8))
    predicted_top8 = set(seed[:8])
    return len(true_top8 & predicted_top8) / 8



def plot_seeding_quality(seed_classes: dict[str, list]):
    rank_corrs = {}
    top8_accs = {}

    for name, seeds in seed_classes.items():
        rank_corrs[name] = [rank_corr(s) for s in seeds]
        top8_accs[name] = [top8_accuracy(s) for s in seeds]

    labels = list(seed_classes.keys())

    rank_data = [rank_corrs[l] for l in labels]
    top8_data = [top8_accs[l] for l in labels]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharex=True)

    sns.violinplot(data=rank_data, ax=axes[0], inner="quartile")
    sns.violinplot(data=top8_data, ax=axes[1], inner="quartile")

    positions = np.arange(len(labels))

    for ax in axes:
        ax.set_xticks(positions)
        ax.set_xticklabels(labels, rotation=20)
        ax.grid(alpha=0.3)

    axes[0].set_ylabel("Spearman rank correlation")
    axes[0].set_title("Rank correlation vs unshuffled seeds")
    axes[0].set_ylim(-1, 1)

    axes[1].set_ylabel("Top-8 accuracy")
    axes[1].set_title("Top-8 preservation")
    axes[1].set_ylim(0, 1)

    plt.tight_layout()
    plt.show()