"""The incremental delta functions must agree with full evaluate() exactly,
for every move, on every instance - otherwise Hill-Climbing would silently
optimize the wrong thing. Checked here by brute force across many random
instances and moves rather than by hand-picked cases."""

import random

from exam_timetable.cost import build_snapshot, delta_shift, delta_swap, evaluate
from exam_timetable.generator import generate_instance
from exam_timetable.state import random_assignment, shifted, swapped

SEEDS = range(20)


def test_delta_shift_matches_full_recompute():
    for seed in SEEDS:
        rng = random.Random(seed)
        instance = generate_instance(num_exams=12, num_rooms=4, days=3, periods_per_day=3, seed=seed)
        assignment = random_assignment(instance, rng)
        snapshot = build_snapshot(instance, assignment)
        base_cost = evaluate(instance, assignment).total

        for _ in range(30):
            exam_idx = rng.randrange(instance.num_exams)
            slot_idx = rng.randrange(instance.num_slots)
            room_idx = rng.randrange(instance.num_rooms)
            if (slot_idx, room_idx) == assignment[exam_idx]:
                continue

            expected_delta = delta_shift(instance, assignment, snapshot, exam_idx, slot_idx, room_idx)
            new_assignment = shifted(assignment, exam_idx, slot_idx, room_idx)
            actual_delta = evaluate(instance, new_assignment).total - base_cost

            assert expected_delta == actual_delta, (
                f"seed={seed} exam={exam_idx} -> ({slot_idx},{room_idx}): "
                f"expected {expected_delta}, got {actual_delta}"
            )


def test_delta_swap_matches_full_recompute():
    for seed in SEEDS:
        rng = random.Random(seed)
        instance = generate_instance(num_exams=12, num_rooms=4, days=3, periods_per_day=3, seed=seed)
        assignment = random_assignment(instance, rng)
        snapshot = build_snapshot(instance, assignment)
        base_cost = evaluate(instance, assignment).total

        for _ in range(30):
            i, j = rng.sample(range(instance.num_exams), 2)
            if assignment[i] == assignment[j]:
                continue

            expected_delta = delta_swap(instance, assignment, snapshot, i, j)
            new_assignment = swapped(assignment, i, j)
            actual_delta = evaluate(instance, new_assignment).total - base_cost

            assert expected_delta == actual_delta, (
                f"seed={seed} swap=({i},{j}): expected {expected_delta}, got {actual_delta}"
            )
