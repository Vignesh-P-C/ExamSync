"""The shipped sample data must be schedulable on the frontend's default grid.

The first sample had 432 of 435 course pairs sharing a student and needed
>= 28 time slots, so on the default 5 days x 3 periods grid (15 slots) every
algorithm ended with ~35 hard violations and the demo looked broken. These
tests make sure that can't silently come back.
"""

from itertools import combinations
from pathlib import Path

from exam_timetable.csv_loader import load_instance_from_csv

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample"
DAYS, PERIODS = 5, 3  # app.py's default grid


def _load():
    instance, _labels = load_instance_from_csv(
        str(SAMPLE / "courses.csv"),
        str(SAMPLE / "enrollments.csv"),
        str(SAMPLE / "rooms.csv"),
        days=DAYS,
        periods_per_day=PERIODS,
    )
    return instance


def _dsatur_slots_needed(instance):
    """Slots a greedy (DSATUR) colouring of the conflict graph uses. A valid
    colouring is a clash-free timetable, so this upper-bounds the slots
    actually needed."""
    n = instance.num_exams
    adjacent = {i: set() for i in range(n)}
    for a, b in combinations(range(n), 2):
        if instance.courses[a].students & instance.courses[b].students:
            adjacent[a].add(b)
            adjacent[b].add(a)

    colour = {}
    while len(colour) < n:
        v = max(
            (x for x in range(n) if x not in colour),
            key=lambda x: (len({colour[u] for u in adjacent[x] if u in colour}), len(adjacent[x])),
        )
        used = {colour[u] for u in adjacent[v] if u in colour}
        c = 0
        while c in used:
            c += 1
        colour[v] = c
    return max(colour.values()) + 1


def test_sample_loads():
    instance = _load()
    assert instance.num_exams == 30
    assert instance.num_rooms == 6


def test_sample_fits_in_default_grid():
    instance = _load()
    assert _dsatur_slots_needed(instance) <= instance.num_slots


def test_every_course_fits_in_some_room():
    instance = _load()
    biggest_room = max(room.capacity for room in instance.rooms)
    assert all(len(course.students) <= biggest_room for course in instance.courses)


def test_sample_is_not_trivially_dense():
    """Guards against regenerating a fully-random enrolment again."""
    instance = _load()
    n = instance.num_exams
    conflicting = sum(
        1
        for a, b in combinations(instance.courses, 2)
        if a.students & b.students
    )
    assert conflicting < 0.5 * (n * (n - 1) // 2)
