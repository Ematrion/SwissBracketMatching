# Swiss Bracket Matching


---

## Repository content

1. Research Report Notebooks
    - EmaColoring: Explores matching in the swiss bracket with a graph theory. Present two matching algorhims
    - MatchingStudy: Perform simulation based comparative study between matchings strategy in the Swiss Bracket tournament.

2. code base
    - ema folder: modules for the EmaColoring notebook. Include Graph definitions, algorithms implementations and analysis, etc.
    - simulation folder: module for the MatchingStudy notebook. Include dataframe specification, parameters definition, experimental protocol, etc.
    - utils: a common module for both notebook. Include "pairings" specification relative to Valve Swiss Bracket RuleBook.
    
3. data
    - examples: tournament outcome csv from various sources
    - synthetic: output dataset from simulation in MatchingStudy

---

## The *Expected Matching Approach*

The method is explained in the EmaColoring notebook. It adresses a fairness problem in competition by ensuring the existence of *perfect matching on $K_{3,3}* in the last round of the tournament.

---

## Evaluation in simulation

Different tournament matching strategy are compared in simulation. I evaluate which teams achieve top8 and compared them to their *initial seed* and *true level*. Parameters of the study are: Player level distribution (4 population); class of seedings (4 class of 200 randomly sample seedings); 2 game outcome generator (1 deterministic, one stochastic).
The goal is to measure wether the top8 are more representatif of the players skills or their seed.

---


## Sources & References

- Problem Statement from GrahamPitt
https://x.com/messioso/status/1644389658942373899

- Valve's CS Major Supplemental Rulebook
https://github.com/ValveSoftware/counter-strike_rules_and_regs/blob/main/major-supplemental-rulebook.md

- img/Chord_diagrams_K6_matchings.svg
https://en.wikipedia.org/wiki/Chord_diagram_%28mathematics%29

- RSTT - simulation framework
DOI 10.5281/zenodo.16926605
