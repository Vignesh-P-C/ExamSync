"""The cost function shared by all three algorithms.

Hard violations (weight 10): a student double-booked in the same slot, a
room asked to hold more students than it can seat, or two exams clashing in
the same room/slot. Soft violations (weight 1): a student with back-to-back
exams, or exams bunched onto the same day instead of spread out. Weights are
placeholders to be tuned in Review 2, per the proposal.
"""

from collections import defaultdict
from dataclasses import dataclass

from .models import ProblemInstance
from .state import Assignment

HARD_WEIGHT = 10
SOFT_WEIGHT = 1


@dataclass(frozen=True)
class CostResult:
    hard: int
    soft: int

    @property
    def total(self) -> int:
        return HARD_WEIGHT * self.hard + SOFT_WEIGHT * self.soft


def evaluate(instance: ProblemInstance, assignment: Assignment) -> CostResult:
    hard = 0
    room_slot_occupant = {}
    student_slot_count = defaultdict(int)
    student_day_periods = defaultdict(set)

    for exam_idx, (slot_idx, room_idx) in enumerate(assignment):
        course = instance.courses[exam_idx]
        slot = instance.slots[slot_idx]
        room = instance.rooms[room_idx]

        if len(course.students) > room.capacity:
            hard += 1

        key = (slot_idx, room_idx)
        if key in room_slot_occupant:
            hard += 1
        else:
            room_slot_occupant[key] = exam_idx

        for student in course.students:
            student_slot_count[(student, slot_idx)] += 1
            student_day_periods[(student, slot.day)].add(slot.period)

    for count in student_slot_count.values():
        if count > 1:
            hard += count - 1

    soft = 0
    for periods in student_day_periods.values():
        n = len(periods)
        if n > 1:
            soft += n - 1  # bunching: more than one exam the same day
        ordered = sorted(periods)
        for a, b in zip(ordered, ordered[1:]):
            if b - a == 1:
                soft += 1  # back-to-back: adjacent periods the same day

    return CostResult(hard=hard, soft=soft)


# ---------------------------------------------------------------------------
# Incremental delta-cost computation.
#
# Hill-Climbing's exhaustive neighborhood (every shift + every swap, every
# round) makes `evaluate()` too slow at scale: it rescans every enrollment
# for every single candidate move. A `Snapshot` captures the aggregates
# `evaluate()` would otherwise rebuild from scratch, once per round; each
# candidate move's cost delta is then computed by touching only the
# students actually enrolled in the exam(s) that moved.
# ---------------------------------------------------------------------------


@dataclass
class Snapshot:
    room_slot_occupant: dict  # (slot_idx, room_idx) -> list[exam_idx]
    student_slot_count: dict  # (student, slot_idx) -> int
    student_day_periods: dict  # (student, day) -> dict[period, int]


def build_snapshot(instance: ProblemInstance, assignment: Assignment) -> Snapshot:
    room_slot_occupant = defaultdict(list)
    student_slot_count = defaultdict(int)
    student_day_periods = defaultdict(lambda: defaultdict(int))

    for exam_idx, (slot_idx, room_idx) in enumerate(assignment):
        course = instance.courses[exam_idx]
        slot = instance.slots[slot_idx]
        room_slot_occupant[(slot_idx, room_idx)].append(exam_idx)
        for student in course.students:
            student_slot_count[(student, slot_idx)] += 1
            student_day_periods[(student, slot.day)][slot.period] += 1

    return Snapshot(room_slot_occupant, student_slot_count, student_day_periods)


def _capacity_violation(num_students: int, room_capacity: int) -> int:
    return 1 if num_students > room_capacity else 0


def _soft_contribution(period_counts) -> int:
    periods = sorted(p for p, c in period_counts.items() if c > 0)
    n = len(periods)
    contrib = max(0, n - 1)
    for a, b in zip(periods, periods[1:]):
        if b - a == 1:
            contrib += 1
    return contrib


def _student_move_delta(snapshot: Snapshot, student: int, old_slot, new_slot):
    """Hard (double-booking) and soft delta for one student's one exam
    moving from `old_slot` to `new_slot`, read against `snapshot` (which
    still reflects the pre-move assignment)."""
    if old_slot.id == new_slot.id:
        return 0, 0

    old_count = snapshot.student_slot_count.get((student, old_slot.id), 0)
    new_count = snapshot.student_slot_count.get((student, new_slot.id), 0)
    delta_hard = (max(0, old_count - 2) - max(0, old_count - 1)) + (
        max(0, new_count) - max(0, new_count - 1)
    )

    delta_soft = 0
    if old_slot.day == new_slot.day:
        day_counts = snapshot.student_day_periods.get((student, old_slot.day), {})
        before = _soft_contribution(day_counts)
        temp = dict(day_counts)
        temp[old_slot.period] = temp.get(old_slot.period, 0) - 1
        temp[new_slot.period] = temp.get(new_slot.period, 0) + 1
        delta_soft += _soft_contribution(temp) - before
    else:
        old_day_counts = snapshot.student_day_periods.get((student, old_slot.day), {})
        before_old = _soft_contribution(old_day_counts)
        temp_old = dict(old_day_counts)
        temp_old[old_slot.period] = temp_old.get(old_slot.period, 0) - 1
        delta_soft += _soft_contribution(temp_old) - before_old

        new_day_counts = snapshot.student_day_periods.get((student, new_slot.day), {})
        before_new = _soft_contribution(new_day_counts)
        temp_new = dict(new_day_counts)
        temp_new[new_slot.period] = temp_new.get(new_slot.period, 0) + 1
        delta_soft += _soft_contribution(temp_new) - before_new

    return delta_hard, delta_soft


def delta_shift(
    instance: ProblemInstance,
    assignment: Assignment,
    snapshot: Snapshot,
    exam_idx: int,
    new_slot_idx: int,
    new_room_idx: int,
) -> int:
    old_slot_idx, old_room_idx = assignment[exam_idx]
    if (old_slot_idx, old_room_idx) == (new_slot_idx, new_room_idx):
        return 0

    course = instance.courses[exam_idx]
    old_slot, new_slot = instance.slots[old_slot_idx], instance.slots[new_slot_idx]
    n_students = len(course.students)

    delta_hard = _capacity_violation(
        n_students, instance.rooms[new_room_idx].capacity
    ) - _capacity_violation(n_students, instance.rooms[old_room_idx].capacity)

    old_key, new_key = (old_slot_idx, old_room_idx), (new_slot_idx, new_room_idx)
    old_occupants = snapshot.room_slot_occupant.get(old_key, [])
    new_occupants = snapshot.room_slot_occupant.get(new_key, [])
    delta_hard += max(0, len(old_occupants) - 2) - max(0, len(old_occupants) - 1)
    delta_hard += max(0, len(new_occupants)) - max(0, len(new_occupants) - 1)

    delta_soft = 0
    if old_slot_idx != new_slot_idx:
        for student in course.students:
            h, s = _student_move_delta(snapshot, student, old_slot, new_slot)
            delta_hard += h
            delta_soft += s

    return HARD_WEIGHT * delta_hard + SOFT_WEIGHT * delta_soft


def delta_swap(
    instance: ProblemInstance,
    assignment: Assignment,
    snapshot: Snapshot,
    i: int,
    j: int,
) -> int:
    slot_i_idx, room_i_idx = assignment[i]
    slot_j_idx, room_j_idx = assignment[j]
    if (slot_i_idx, room_i_idx) == (slot_j_idx, room_j_idx):
        return 0

    course_i, course_j = instance.courses[i], instance.courses[j]
    slot_i, slot_j = instance.slots[slot_i_idx], instance.slots[slot_j_idx]

    # The two occupied (slot, room) keys are unchanged by a swap - only
    # which exam sits in which key changes - so room/slot clash delta is
    # always 0; only capacity can change, since the two courses differ in size.
    delta_hard = (
        _capacity_violation(len(course_i.students), instance.rooms[room_j_idx].capacity)
        + _capacity_violation(len(course_j.students), instance.rooms[room_i_idx].capacity)
        - _capacity_violation(len(course_i.students), instance.rooms[room_i_idx].capacity)
        - _capacity_violation(len(course_j.students), instance.rooms[room_j_idx].capacity)
    )
    delta_soft = 0

    # A student enrolled in both courses keeps one exam at slot_i and one at
    # slot_j either way, so only students enrolled in exactly one of the two
    # courses actually experience their exam moving.
    only_i = course_i.students - course_j.students
    only_j = course_j.students - course_i.students

    for student in only_i:
        h, s = _student_move_delta(snapshot, student, slot_i, slot_j)
        delta_hard += h
        delta_soft += s
    for student in only_j:
        h, s = _student_move_delta(snapshot, student, slot_j, slot_i)
        delta_hard += h
        delta_soft += s

    return HARD_WEIGHT * delta_hard + SOFT_WEIGHT * delta_soft
