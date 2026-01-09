from typing import Any
from rstt import Ranking, SwissBracket

from ema.completebipartite import handles, CompleteBiPartite as CBG
from ema.coverings import FLAT, STAR

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
import numpy as np

def plot_models(models: dict[str, Any], data_dir: str, max_cols: int=4):
    n = len(models)
    cols = min(n, max_cols)
    rows = math.ceil(n / cols)
    
    fig, axes = plt.subplots(rows, cols, figsize=(8, 8))

    for ax, name in zip(axes.flat, models.keys()):
        path = f"{data_dir}/{name}.png"
        img = mpimg.imread(path)
        ax.imshow(img)
        ax.set_title(name)
        ax.axis("off")   # hide axes

    #plt.tight_layout()
    plt.show()
    
    
def plot_coverings(coverings: list[dict[str, list]], titles: list, axes: list, fig):
    nb = len(coverings[0].values())
    for op, name, ax in zip(coverings, titles, axes):
        k33 = CBG(n=nb*2)
        k33.set_edges_color(op)
        plt.sca(ax)
        k33.plot()
        ax.text(0.5, 0.94, name, transform=ax.transAxes, ha="center",va="bottom", fontsize=15,fontweight="bold")
    #plt.tight_layout()
    fig.legend(loc="lower center", bbox_to_anchor=(0.5, -0.1), handles=handles[:nb], ncol=nb, fontsize=15)
    plt.show()
    
def set_rounds_5_layout(figsize=(16, 8)):
    fig = plt.figure(figsize=figsize)
    nr, nc = 4, 5
    gs = fig.add_gridspec(nr, nc, wspace=0.4, hspace=0.4)
    ax_k44 = fig.add_subplot(gs[0:2, 0:2])

    axes = {}

    for r in range(nr):
        for c in range(nc):
            if not (r < 2 and c < 2):  
                axes[(r, c)] = fig.add_subplot(gs[r, c])
    return fig, axes, ax_k44
    