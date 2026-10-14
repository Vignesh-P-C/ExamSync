"""State representation: a timetable is one (slot, room) pair per exam.

Per the proposal's formulation, a state is "a list, one entry per exam" -
here, `Assignment` is exactly that list, shared by all three algorithms.
"""

import random
from typing import List, Tuple

from .models import ProblemInstance

Assignment = List[Tuple[int, int]]  # index = exam index, value = (slot_idx, room_idx)


def random_assignment(instance: ProblemInstance, rng: random.Random) -> Assignment:
    """Every exam thrown into a random slot/room, with no clash avoidance."""
    return [
        (rng.randrange(instance.num_slots), rng.randrange(instance.num_rooms))
        for _ in range(instance.num_exams)
    ]


def shifted(assignment: Assignment, exam_idx: int, slot_idx: int, room_idx: int) -> Assignment:
    """Copy of `assignment` with one exam moved to a different (slot, room)."""
    new_assignment = list(assignment)
    new_assignment[exam_idx] = (slot_idx, room_idx)
    return new_assignment


def swapped(assignment: Assignment, i: int, j: int) -> Assignment:
    """Copy of `assignment` with exams i and j trading (slot, room)."""
    new_assignment = list(assignment)
    new_assignment[i], new_assignment[j] = new_assignment[j], new_assignment[i]
    return new_assignment
