"""Synthetic problem-instance generator.

Builds a reproducible (seeded) exam-scheduling instance of a given size so the
three algorithms can be compared on identical inputs, per the proposal's
experiment plan (10 / 30 / 60 exams).
"""

import random
from typing import Optional

from .models import Course, ProblemInstance, Room, TimeSlot

ROOM_CAPACITIES = [30, 40, 50, 60, 80, 100]


def generate_instance(
    num_exams: int,
    num_students: Optional[int] = None,
    num_rooms: int = 6,
    days: int = 5,
    periods_per_day: int = 4,
    min_courses_per_student: int = 3,
    max_courses_per_student: int = 6,
    seed: Optional[int] = None,
) -> ProblemInstance:
    rng = random.Random(seed)

    if num_students is None:
        num_students = max(num_exams * 5, 50)

    course_students = [set() for _ in range(num_exams)]
    k_max = min(max_courses_per_student, num_exams)
    k_min = min(min_courses_per_student, k_max)
    for student in range(num_students):
        k = rng.randint(k_min, k_max)
        for course_idx in rng.sample(range(num_exams), k):
            course_students[course_idx].add(student)

    # Guarantee every course has at least one enrolled student.
    for course_idx, enrolled in enumerate(course_students):
        if not enrolled:
            enrolled.add(rng.randrange(num_students))

    courses = [
        Course(id=i, name=f"CSE{100 + i}", students=frozenset(course_students[i]))
        for i in range(num_exams)
    ]
    rooms = [
        Room(id=r, capacity=rng.choice(ROOM_CAPACITIES)) for r in range(num_rooms)
    ]
    slots = [
        TimeSlot(id=day * periods_per_day + period, day=day, period=period)
        for day in range(days)
        for period in range(periods_per_day)
    ]

    return ProblemInstance(
        courses=courses, rooms=rooms, slots=slots, num_students=num_students
    )
