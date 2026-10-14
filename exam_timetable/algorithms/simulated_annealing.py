"""Simulated Annealing.

Always accepts a better neighbor; accepts a worse one with probability
P = exp(-delta_cost / T). T decreases geometrically (T <- alpha * T) each
step; the run ends once T drops below `min_temp` or `max_iters` is hit.
"""

import math
import random
import time

from ..cost import evaluate
from ..models import ProblemInstance
from ..operators import random_shift_move, random_swap_move
from ..result import SearchResult
from ..state import random_assignment


def run(
    instance: ProblemInstance,
    max_iters: int = 5000,
    initial_temp: float = 50.0,
    alpha: float = None,
    min_temp: float = 1e-3,
    rng: random.Random = None,
) -> SearchResult:
    rng = rng or random.Random()
    start = time.perf_counter()

    if alpha is None:
        # Derive the cooling rate from max_iters so the schedule spans the
        # whole budget: a fixed alpha (e.g. 0.995) cools below min_temp
        # after a fixed number of steps regardless of max_iters, silently
        # handing back unused budget (observed: ~2159 steps with the old
        # default, no matter whether max_iters was 2000 or 50000).
        alpha = (min_temp / initial_temp) ** (1 / max_iters)

    assignment = random_assignment(instance, rng)
    cost = evaluate(instance, assignment)
    best_assignment, best_cost = assignment, cost
    history = [cost.total]
    temp = initial_temp

    for _ in range(max_iters):
        if temp < min_temp:
            break

        candidate = (
            random_shift_move(instance, assignment, rng)
            if rng.random() < 0.5
            else random_swap_move(assignment, rng)
        )
        c = evaluate(instance, candidate)
        delta = c.total - cost.total

        if delta < 0 or rng.random() < math.exp(-delta / temp):
            assignment, cost = candidate, c
            if cost.total < best_cost.total:
                best_assignment, best_cost = assignment, cost

        temp *= alpha
        history.append(best_cost.total)
        if best_cost.total == 0:
            break

    return SearchResult(
        assignment=best_assignment,
        cost=best_cost,
        history=history,
        iterations=len(history) - 1,
        elapsed_seconds=time.perf_counter() - start,
    )
