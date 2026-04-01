from rstt import Ranking, SwissBracket

import matplotlib.pyplot as plt
import numpy as np

def skills_seed_matrix(events: list[SwissBracket], gt: Ranking):
    qualifications = np.zeros((16, 16))  # rows = real level, cols = seed
    count = np.zeros((16, 16))

    for event in events:
        for p in gt:
            t = gt[p]
            s = event.seeding[p]
            count[t, s] += 1 # type: ignore
            if event.standing()[p] <= 8:
                qualifications[t, s] += 1 # type: ignore

    # avoid division by zero
    with np.errstate(divide='ignore', invalid='ignore'):
        Q = qualifications / count
        Q[np.isnan(Q)] = 0.0 
        
    return Q

def plot_qualif_matrix(events, models, m):
    Q = skills_seed_matrix(events, models[m])
    n = Q.shape[0]

    plt.figure(figsize=(8, 6))
    im = plt.imshow(Q, cmap="viridis", origin="upper", aspect="auto")

    plt.colorbar(im, label="Qualification probability")

    plt.xticks(range(n), range(1, n+1)) # type: ignore
    plt.yticks(range(n), range(1, n+1)) # type: ignore

    plt.xlabel("Seed")
    plt.ylabel("True Level")
    plt.title('BLUE versus RED Pill')

    # optional: show grid lines
    plt.grid(False)

    plt.tight_layout()
    plt.show()
    
def plot_multiple_Q(v_list, results, s, m, sc, models):
    n = len(v_list)

    # grid size (automatic)
    cols = min(n, 4)
    rows = int(np.ceil(n / cols))

    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 5 * rows), constrained_layout=True)
    axes = axes.ravel()

    for ax, v in zip(axes, v_list):
        events = results[v][s][m][sc].values()
        Q = skills_seed_matrix(events, models[m])

        im = ax.imshow(Q, cmap="viridis", origin="upper", aspect="auto")
        ax.set_title(f"{v}", fontsize=12)

        ax.set_xlabel("Seed")
        ax.set_ylabel("True Level")
        ax.set_xticks(range(16))
        ax.set_xticklabels(range(1, 17))
        ax.set_yticks(range(16))
        ax.set_yticklabels(range(1, 17))

        # Add huge cross at center
        mid = Q.shape[0] // 2
        ax.axhline(mid-0.5, color='red', linewidth=2, linestyle='--')
        ax.axvline(mid-0.5, color='red', linewidth=2, linestyle='--')

    # Hide unused axes
    for ax in axes[len(v_list):]:
        ax.axis("off")

    # One colorbar for the whole figure
    cbar = fig.colorbar(im, ax=axes, shrink=0.7, pad=0.02)
    cbar.set_label("Qualification Probability")

    plt.show()
    
