"""Move, crossover, and mutation operators shared across algorithms."""

import random
from itertools import combinations
from typing import Iterator, Tuple

from .models import ProblemInstance
from .state import Assignment, shifted, swapped


def all_shift_moves(instance: ProblemInstance, assignment: Assignment) -> Iterator[Assignment]:
    """Every way to move a single exam to a different (slot, room)."""
    for exam_idx, current in enumerate(assignment):
        for slot_idx in range(instance.num_slots):
            for room_idx in range(instance.num_rooms):
                if (slot_idx, room_idx) == current:
                    continue
                yield shifted(assignment, exam_idx, slot_idx, room_idx)


def all_swap_moves(assignment: Assignment) -> Iterator[Assignment]:
    """Every way to swap the (slot, room) of two exams."""
    for i, j in combinations(range(len(assignment)), 2):
        yield swapped(assignment, i, j)


def all_shift_candidates(
    instance: ProblemInstance, assignment: Assignment
) -> Iterator[Tuple[int, int, int]]:
    """Every (exam_idx, new_slot_idx, new_room_idx) - as plain tuples, so
    Hill-Climbing's exhaustive scan doesn't have to copy the whole
    assignment list just to score a candidate."""
    for exam_idx, current in enumerate(assignment):
        for slot_idx in range(instance.num_slots):
            for room_idx in range(instance.num_rooms):
                if (slot_idx, room_idx) != current:
                    yield exam_idx, slot_idx, room_idx


def all_swap_candidates(num_exams: int) -> Iterator[Tuple[int, int]]:
    """Every (i, j) exam-index pair whose (slot, room) could be swapped."""
    return combinations(range(num_exams), 2)


def random_shift_move(
    instance: ProblemInstance, assignment: Assignment, rng: random.Random
) -> Assignment:
    exam_idx = rng.randrange(instance.num_exams)
    slot_idx = rng.randrange(instance.num_slots)
    room_idx = rng.randrange(instance.num_rooms)
    return shifted(assignment, exam_idx, slot_idx, room_idx)


def random_swap_move(assignment: Assignment, rng: random.Random) -> Assignment:
    i, j = rng.sample(range(len(assignment)), 2)
    return swapped(assignment, i, j)


def crossover_single_point(
    parent1: Assignment, parent2: Assignment, rng: random.Random
) -> Assignment:
    point = rng.randrange(1, len(parent1))
    return list(parent1[:point]) + list(parent2[point:])


def mutate(
    assignment: Assignment,
    instance: ProblemInstance,
    rng: random.Random,
    gene_rate: float = 0.05,
) -> Assignment:
    """Each exam independently reassigned to a random (slot, room) with
    probability `gene_rate` - a single all-or-nothing mutated exam gives a
    GA almost no search power on top of crossover, so every gene gets its
    own independent chance each generation, with at least one guaranteed
    mutation so the operator always does something."""
    new_assignment = list(assignment)
    mutated_any = False
    for exam_idx in range(instance.num_exams):
        if rng.random() < gene_rate:
            new_assignment[exam_idx] = (
                rng.randrange(instance.num_slots),
                rng.randrange(instance.num_rooms),
            )
            mutated_any = True
    if not mutated_any:
        exam_idx = rng.randrange(instance.num_exams)
        new_assignment[exam_idx] = (
            rng.randrange(instance.num_slots),
            rng.randrange(instance.num_rooms),
        )
    return new_assignment


def tournament_select(
    population, fitness, k: int, rng: random.Random
) -> Assignment:
    contenders = rng.sample(range(len(population)), k)
    winner = min(contenders, key=lambda i: fitness[i].total)
    return population[winner]
