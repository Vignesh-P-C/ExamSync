import random

from exam_timetable.generator import generate_instance
from exam_timetable.state import random_assignment, shifted, swapped


def test_random_assignment_shape_and_bounds():
    instance = generate_instance(num_exams=10, seed=1)
    rng = random.Random(1)
    assignment = random_assignment(instance, rng)

    assert len(assignment) == instance.num_exams
    for slot_idx, room_idx in assignment:
        assert 0 <= slot_idx < instance.num_slots
        assert 0 <= room_idx < instance.num_rooms


def test_shifted_changes_only_target_exam():
    assignment = [(0, 0), (1, 1), (2, 2)]
    new_assignment = shifted(assignment, 1, 5, 6)
    assert new_assignment == [(0, 0), (5, 6), (2, 2)]
    assert assignment == [(0, 0), (1, 1), (2, 2)]  # original untouched


def test_swapped_trades_two_exams():
    assignment = [(0, 0), (1, 1), (2, 2)]
    new_assignment = swapped(assignment, 0, 2)
    assert new_assignment == [(2, 2), (1, 1), (0, 0)]
    assert assignment == [(0, 0), (1, 1), (2, 2)]  # original untouched
