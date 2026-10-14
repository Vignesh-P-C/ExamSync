"""Steepest-ascent (here, steepest-descent-on-cost) Hill-Climbing.

Each round, every shift and every swap is evaluated; the single best one is
taken. Stops when no move improves the state, or at `max_iters`.

Scoring every candidate with the full `evaluate()` would rescan every
enrollment for each of the thousands of candidates generated per round.
Instead, a `Snapshot` of the current assignment is built once per round
(`build_snapshot`), and each candidate's cost delta is computed against it
(`delta_shift` / `delta_swap`) touching only the students actually enrolled
in the exam(s) that candidate would move.
"""

import random
import time

from ..cost import build_snapshot, delta_shift, delta_swap, evaluate
from ..models import ProblemInstance
from ..operators import all_shift_candidates, all_swap_candidates
from ..result import SearchResult
from ..state import random_assignment, shifted, swapped


def run(
    instance: ProblemInstance, max_iters: int = 100, rng: random.Random = None
) -> SearchResult:
    rng = rng or random.Random()
    start = time.perf_counter()

    assignment = random_assignment(instance, rng)
    cost = evaluate(instance, assignment)
    history = [cost.total]

    for _ in range(max_iters):
        snapshot = build_snapshot(instance, assignment)
        best_delta = 0
        best_move = None  # ("shift", exam_idx, slot_idx, room_idx) | ("swap", i, j)

        for exam_idx, slot_idx, room_idx in all_shift_candidates(instance, assignment):
            delta = delta_shift(instance, assignment, snapshot, exam_idx, slot_idx, room_idx)
            if delta < best_delta:
                best_delta = delta
                best_move = ("shift", exam_idx, slot_idx, room_idx)

        for i, j in all_swap_candidates(instance.num_exams):
            delta = delta_swap(instance, assignment, snapshot, i, j)
            if delta < best_delta:
                best_delta = delta
                best_move = ("swap", i, j)

        if best_move is None:
            break  # local optimum: no move improves the state

        if best_move[0] == "shift":
            _, exam_idx, slot_idx, room_idx = best_move
            assignment = shifted(assignment, exam_idx, slot_idx, room_idx)
        else:
            _, i, j = best_move
            assignment = swapped(assignment, i, j)

        cost = evaluate(instance, assignment)
        history.append(cost.total)
        if cost.total == 0:
            break

    return SearchResult(
        assignment=assignment,
        cost=cost,
        history=history,
        iterations=len(history) - 1,
        elapsed_seconds=time.perf_counter() - start,
    )
