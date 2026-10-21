"""Shared categorical color palette for the three algorithms.

One fixed hue per algorithm, reused everywhere a chart compares them
(experiment.py's plots, the frontend's comparison chart) so the same
algorithm is always the same color. Values are the first three slots of
the project's validated categorical palette (passes CVD/contrast checks
for up to three series shown together) - not picked by eye.
"""

ALGORITHM_COLORS = {
    "Hill-Climbing": "#2a78d6",       # blue
    "Simulated Annealing": "#eb6834",  # orange
    "Genetic Algorithm": "#1baf7a",    # aqua
}
