# Swiss Bracket Matching: The Expected Matching Approach

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19409379.svg)](https://doi.org/10.5281/zenodo.19409379)

**Research on matching algorithms for Swiss Bracket tournaments in competitive eSports** The method adresses a fairness issue by ensuring the existence of perfect matching in the last round of the tournament.


---

## Overview

This repository presents a comprehensive analysis of matching strategies in the **Swiss Bracket** format - a tournament structure used by major eSports events including Valve's Counter-Strike Majors and Riot's League of Legends World Championship. The Swiss Bracket qualifies 8 teams from a pool of 16 for playoff stages through five rounds. It is an alternative to traditionnal group stage before play-offs.

### The Problem

In 2023, a viral Twitter thread by analyst Graham Pitt highlighted a fairness issue in the CS Major format: in certain scenarios, despite all teams performing according to their seeds, the 8th-best team could fail to qualify while the 11th-best team advances. The proposed solution - "speed-up" matching (pairing 1st seed vs 9th seed, 2nd vs 10th, etc.) - was adopted by Valve but may actually contradict the format's core purpose without improving the tournament.

### Contribution

This research:
1. **Identifies the root cause** through graph-theoretic analysis ($K_{3,3}$ perfect matching theory)
2. **Proposes the Expected Matching Approach (EMA)** using rotation algorithms to guarantee valid matchings
3. **Validates through simulation** across multiple population models, seeding qualities, and game outcome generators
4. **Demonstrates superior robustness** of the EMA Rotation algorithm over current implementations and alternatives

---

## Repository Structure

### 📓 Interactive Notebooks

1. **[1_GraphColoring.ipynb](1_GraphColoring.ipynb)** - Theoretical Foundation
   - Graph-theoretic problem identification
   - Analysis of FLAT and STAR edge colorings on $K_{3,3}$
   - Cross algorithm vs Rotation algorithm comparison
   - Cycle basis analysis for predicting problematic scenarios

2. **[2_Simulation.ipynb](2_Simulation.ipynb)** - Simulation Protocol
   - RSTT framework implementation
   - Reproduction of Twitter example
   - Experimental design and parameters
   - Comparison of 8 tournament variants across 48 configurations

3. **[3_Dashboard.ipynb](3_Dashboard.ipynb)** - Interactive Dashboard
   - Comprehensive metric definitions
   - Interactive visualizations for all results
   - User guide for interpreting findings
   - Comparison across utility loss, precision, fairness, balance, and last round quality

### 🔧 Code Base

- **`ema/`** - Expected Matching Approach implementation
  - Complete bipartite graph definitions
  - Cross and Rotation algorithms
  - Intersection graph analysis
  - Cycle basis prediction tools

- **`simulation/`** - Simulation framework modules
  - Tournament system implementations
  - Seeding class generators
  - Population distribution models
  - Experimental protocols and data structures

- **`evaluation/`** - Analysis and metrics
  - Result matrix computations
  - Tournament analyzer
  - Statistical aggregation

- **`visualisation/`** - Dashboard components
  - Interactive plotting utilities
  - Metric visualization functions

- **`utils.py`** - Shared utilities
  - Valve Swiss Bracket pairing specifications
  - Common helper functions

### 📊 Data

- **`data/examples/`** - Real tournament outcomes (CSV format)
- **`data/results/`** - Simulation output datasets
- **`figures/`** - Generated visualizations

---

## Key Findings

### 1. The Root Cause: Incompatible Edge Colorings

The problem stems from mixing edges from incompatible proper 3-edge colorings (FLAT and STAR) of $K_{3,3}$. When Round 1 and Round 3 pairings come from different colorings, **no valid $K_{3,3}$ perfect matching remains for Round 5** in certain scenarios.

**Mathematical Insight:** The six preferred matchings on $K_{3,3}$ form two distinct proper colorings that are structurally incompatible. Each matching from one coloring shares exactly one edge with each matching from the other.

### 2. The Expected Matching Approach (EMA)

**Rotation Algorithm Properties:**
- ✅ Guarantees valid $K_{3,3}$ matching exists in Round 5 for **all 16 possible scenarios**
- ✅ Respects Valve's preference for pairing top-half vs bottom-half seeds
- ✅ No "virtual duplicate" games that violate proper edge coloring
- ✅ Provides structural guarantees regardless of which teams reach 2-2 record

**Cross Algorithm (Current Major) Deficiencies:**
- ❌ Valid matching exists in only 8 of 16 scenarios
- ❌ Fails precisely when good seeding should work best
- ❌ Forces suboptimal pairings (top vs top, or bottom vs bottom)
- ❌ No practical differences between the old and the new rules

### 3. Simulation Results

Across **4 population models** × **4 seeding classes** × **3 solvers** × **20 samples**:

**EMA Rotation advantages:**
- **Better qualification accuracy**: Lower utility loss and higher top-8 precision across all seeding qualities
- **Higher robustness**: Maintains performance even with random seedings
- **Improved last-round fairness**: More appropriate pairings in decisive moments

**Key insight:** The current "speed-up" approach optimizes for perfect seeds but fails under realistic conditions. EMA is robust to seeding uncertainty.

---

## The Expected Matching Approach Explained

### Rotation Algorithm (Simplified)

For teams at 2-2 record reaching Round 5:

0. Input: a perfect matching on $K_{3,3}$
1. Order top-half teams: $(a, 1, 2, 3)$
2. Order bottom-half teams: $(b, 6, 5, 4)$
3. Generate pairings by rotation: $(V_{1,j}, V_{2,(j-i) \mod 4})$ for $i = 0,1,2,3$

This creates a proper 4-edge coloring of $K_{4,4}$ where:
- All possible 2-team removal scenarios leave a valid $K_{3,3}$ matching after two rounds.
- No *virtual duplicate* encounters across rounds
- Optimal pairing structure (top vs bottom) is preserved

### Why This Works

The rotation structure ensures that *forbiden patterns* does not appear. By avoiding 2-color cycles in the cycle basis, we eliminate scenarios where team removal makes perfect matchings impossible.

---

## Evaluation Metrics

The simulation study evaluates systems across six key metrics:

| Metric | Description | Optimal Value |
|--------|-------------|--------------|
| **Utility Loss** | Qualification probability gap between actual and ideal outcomes | Lower |
| **Top 8 Precision** | Percentage of qualified teams from true top 8 | Higher |
| **Fairness** | Deviation from ideal seed-based pairings | Lower |
| **Balance** | Average skill difference in matchups | Lower |
| **Last Round Fairness** | Round 5 specific pairing quality | Lower |


See [3_Dashboard.ipynb](.dev/claude/3_Dashboard.ipynb) for detailed metric definitions and interpretation guides.

---

## Getting Started

### Installation

1. **Install uv** (if not already installed):
  ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

2. **Clone the repository**:

   ```bash
   git clone https://github.com/Ematrion/SwissBracketMatching.git
   cd SwissBracketmatching
   ```

3. **Install dependencies** (using `pyproject.toml` and `uv.lock`):

   ```bash
   uv sync
   ```

### Running the Notebooks

```bash
uv run jupyter lab
```


**Recommended order:**
1. Start with `1_GraphColoring.ipynb` to understand the theoretical foundation
2. Proceed to `2_Simulation.ipynb` to see the experimental setup
You do not need to run it. Simulation is heavy and can take several hours to complete, data/results/ contains ready to use .csv. with precomputed metrics.
3. Explore `3_Dashboard.ipynb` to interactively visualize results

**Quick Example: Reproducing the Twitter Scenario**

See section 1.2 of [2_Simulation.ipynb](.dev/claude/2_Simulation.ipynb) for a complete reproduction of the Graham Pitt example demonstrating the problematic outcome.

---

## Simulation Framework: RSTT

This project uses **RSTT** (Ranking & Seeding Tournament Toolkit), a custom Python framework for simulation based research released early 2025.

**Key Features:**
- Flexible tournament format definitions
- Deterministic and stochastic game outcome generators
- Tunable ranking state for seeding purposes.

**DOI:** [10.5281/zenodo.16926605](https://doi.org/10.5281/zenodo.16926605)

---

## Experimental Design

### Population Models
- **GPR_teams**: Real Elo ratings from Riot's 2024 Global Power Ranking
- **Gaussian**: σ=250, μ=1500 (highly competitive field)
- **Pareto**: α=5.5 (heavy-tailed, dominant teams)
- **Weibull**: α=1.2, β=7.0 (intermediate distribution)

### Seeding Classes
- **RANDOM**: Complete shuffle (realistic for international events)
- **ACR2**: Top 8 and bottom 8 shuffled separately
- **ACR3**: Top 4, middle 8, bottom 4 shuffled separately
- **ACR5**: Top 5, middle 6, bottom 5 shuffled separately

### Solvers (Game Outcome Generators)
- **BetterWin**: Deterministic (higher skill always wins)
- **Logistic**: Stochastic with skill-based probabilities
- **MinEffort**: Top-4 teams underperform (upset scenarios) in the first two rounds.

### Tournament Systems Compared

| System | Description | Application|
|--------|-------------|------------|
| **2Groups8** | Two groups of 8 | IIHF Ice-Hockey |
| **4Groups4** | Four groups of 4| Sport Standard|
| **Original** | Twitter example system (F1_CROSS + tiebreaker) | Old CS:GO major 
| **Original-NTB** | Same without tiebreaker | - |
| **Major** | Current Valve implementation (speed-up matching) | Current CS Major |
| **Major-NTB** | Same without tiebreaker | - |
| **FixedDefault** | RSTT default with Valve rules for the last round | - |
| **Ema** | **Proposed EMA Rotation algorithm** | Maybe one day

---

## Results Summary

### Qualification Accuracy
- **EMA Rotation** achieves **lower utility loss** across all seeding qualities
- Advantage most pronounced with poor seedings (RANDOM, ACR2)
- Best **Top-8 precision ~85%** even with imperfect seeds

### Fairness and Balance
- **EMA** produces more fair matchups in Round 5 
- Fewer mismatches between top and bottom seeds in deciding games
- More consistent performance across different population models

### Robustness
- **Current Major performs well only with perfect seeds and deterministic outcomes** 
- **EMA maintains advantages across all seeding qualities**
- Particularly valuable for international tournaments with uncertain rankings

---

## Practical Implications

### For Tournament Organizers

**Recommendation:** Adopt the EMA Rotation algorithm for Round 1-5 pairings.

**Benefits:**
1. **Structural guarantees** - valid matchings always exist
2. **Better qualification accuracy** under realistic seeding uncertainty
3. **Reduced controversial outcomes** that damage competitive integrity
4. **No additional complexity** - It is a pairing system

**Implementation:** See `simulation/systems/` for reference implementations compatible with Valve's rulebook preferences.

### For Competitive Integrity

The "speed-up" matching approach was designed to handle perfect seeds and deterministic game outcome, but:

- Real tournaments never have perfect seeds
- Predefine results is match fixing, not entertaining competition
- Speed-up contradicts the format's goal of letting mid-tier teams face each other frequently
- Keep the same problemtic scenrios.

**EMA addresses the actual problem:** ensuring fair, valid matchings exist regardless of seeding accuracy and game outcomes.


---

## Contributing

Contributions are welcome! Areas of interest:
- Additional population models or seeding strategies
- Alternative matching algorithms
- Extensions to different tournament sizes
- Improved visualization and dashboard features
- Bug fixes and documentation improvements

Please open an issue to discuss proposed changes before submitting PRs.

---

## Citation

If you use this work in your research, please cite:

```bibtex
@misc{swissbracket2024,
  title={The Expected Matching Approach: a Pairing Strategy for Swiss Bracket},
  author={[David Bucher]},
  year={2026},
  publisher={},
  url={https://github.com/yourusername/SwissBracketMatching},
  doi={}
}
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Graham Pitt** for identifying and publicizing the initial problem
- **Valve Corporation** for transparent rulesets and tournament documentation
- **Riot Games** for Global Power Ranking data

---

## Sources & References

### Primary Sources

- **Problem Motivation**: Graham Pitt's Twitter Analysis
  https://x.com/messioso/status/1644389658942373899

- **Current Ruleset**: Valve's CS Major Supplemental Rulebook
  https://github.com/ValveSoftware/counter-strike_rules_and_regs/blob/main/major-supplemental-rulebook.md

- **Graph Theory Background**: Chord Diagrams and Perfect Matchings
  https://en.wikipedia.org/wiki/Chord_diagram_(mathematics)

- **RSTT**: simulation framework 
  DOI 10.5281/zenodo.16926605

### Related Work

- **Swiss-system tournament** (general format description)
- **Graph edge coloring** (theoretical foundation)
- **Complete bipartite graphs** ($K_{n,n}$ properties)

---

## Contact

For questions, suggestions, or collaboration inquiries, please open an issue on GitHub or join the RSTT discord.

---

