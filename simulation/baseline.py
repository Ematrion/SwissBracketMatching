import os
import json

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from rstt import BasicPlayer, BTRanking, LogSolver, RoundRobin

DATA_DIR = "simulation/population"

def load_population(directory: str) -> dict[str, list[BasicPlayer]]:
    data = {}
    for file in os.listdir(directory):
        if file.endswith('.json'):
            file = os.path.join(directory, file)
            name = file.split('/')[-1].replace('.json', '')
            with open(file, 'r') as source:
                population = json.load(source)
                teams = [BasicPlayer(infos['name'], infos['level']) for infos in population]
                gt = BTRanking(name=name, players=teams) #type:ignore
            data[name] = gt
            
    return data

def qualification_probabilities(models: dict[str, BTRanking], sample_size: int) -> dict[str, dict[int, float]]:
    models_probabilities = {}
    for name, perfect_seed in models.items():
        teams = perfect_seed.players()
        qualifications = {i: 0 for i in range(len(teams))} # seed 0 to 15
        for i in range(sample_size):
            rr = RoundRobin(f'{name}-{i}', perfect_seed, LogSolver()) # type:ignore
            rr.registration(teams)
            rr.run()

            for i in qualifications.keys():
                seed_i = perfect_seed[i]
                if rr.standing()[seed_i] <= 8: # qualification threshold # type:ignore
                    qualifications[i] += 1
    
        models_probabilities[name] = {i: qualifications[i]/sample_size for i in qualifications.keys()}
    return models_probabilities


def plot_model_prob(proba: dict[str, dict[int, float]]):
    model_names = list(proba.keys())
    n = len(model_names)
    fig = plt.figure(figsize=(4 * n, 8))
    gs = fig.add_gridspec(nrows=2, ncols=n,
                        left=0.05, right=0.98, top=0.90, bottom=0.08,
                        wspace=0.25, hspace=0.35
    )
    axes = np.empty((2, n), dtype=object)

    for col in range(n):
        axes[0, col] = fig.add_subplot(gs[0, col])
        axes[1, col] = fig.add_subplot(gs[1, col])

    for col, name in enumerate(model_names):    
        # ---------- Row 1: Image ----------
        ax_img = axes[0, col]
        path = f"{DATA_DIR}/{name}.png"
        img = mpimg.imread(path)
        ax_img.imshow(img)
        ax_img.set_title(name)
        ax_img.axis("off")

        # ---------- Row 2: Probability vs Seed ----------
        ax = axes[1, col]
        data = proba[name]

        # shift seeding to 1,...16 notation
        x, y = zip(*sorted((k + 1, v) for k, v in data.items())) 

        ax.bar(x, y, color="steelblue")
        #ax.plot(x, y, marker="o", linewidth=2)
        ax.set_ylim(0, 1.05)
        ax.set_xlim(min(x) - 0.5, max(x) + 0.5)

        ax.set_xlabel("Seed")
        ax.set_ylabel("Top8 probability")
        ax.grid(alpha=0.3)

    fig.text(0.5, 0.94, "Model Heatmaps", ha="center", fontsize=16)
    fig.text(0.5, 0.49, "Top-8 Qualification Probability by Seed",
            ha="center", fontsize=16)
    
    plt.show()