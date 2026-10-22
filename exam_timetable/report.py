"""Human-readable violations report for a solved timetable.

`cost.evaluate()` gives counts (hard/soft) for scoring; this module walks
the same assignment and produces descriptions of *which* violations
remain, for display in the frontend (CLAUDE.md §8.2 / Issue #8) - e.g.
"Room R3 at Day 2 Period 1 is double-booked by CSE101 and CSE107" rather
than just "hard=1".
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Optional

from .models import ProblemInstance
from .state import Assignment


@dataclass
class ViolationReport:
    hard: List[str] = field(default_factory=list)
    soft: List[str] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return not self.hard and not self.soft


def _room_label(room_labels: Optional[List[str]], room_idx: int) -> str:
    if room_labels and room_idx < len(room_labels):
        return room_labels[room_idx]
    return f"Room {room_idx}"


def _student_label(student_labels: Optional[List[str]], student: int) -> str:
    if student_labels and student < len(student_labels):
        return student_labels[student]
    return f"Student {student}"


def _period_label(period_labels: Optional[List[str]], period: int) -> str:
    if period_labels and period < len(period_labels):
        return period_labels[period]
    return f"Period {period + 1}"


def _slot_label(period_labels: Optional[List[str]], slot) -> str:
    return f"Day {slot.day + 1}, {_period_label(period_labels, slot.period)}"


def build_violation_report(
    instance: ProblemInstance,
    assignment: Assignment,
    room_labels: Optional[List[str]] = None,
    student_labels: Optional[List[str]] = None,
    period_labels: Optional[List[str]] = None,
) -> ViolationReport:
    report = ViolationReport()

    room_slot_occupants = defaultdict(list)
    student_slot_exams = defaultdict(list)
    student_day_exams = defaultdict(list)

    for exam_idx, (slot_idx, room_idx) in enumerate(assignment):
        course = instance.courses[exam_idx]
        slot = instance.slots[slot_idx]
        room = instance.rooms[room_idx]

        if len(course.students) > room.capacity:
            report.hard.append(
                f"{course.name} needs {len(course.students)} seats but "
                f"{_room_label(room_labels, room_idx)} only holds {room.capacity} "
                f"({_slot_label(period_labels, slot)})."
            )

        room_slot_occupants[(slot_idx, room_idx)].append(exam_idx)

        for student in course.students:
            student_slot_exams[(student, slot_idx)].append(exam_idx)
            student_day_exams[(student, slot.day)].append((slot.period, exam_idx))

    for (slot_idx, room_idx), occupants in room_slot_occupants.items():
        if len(occupants) > 1:
            slot = instance.slots[slot_idx]
            names = ", ".join(instance.courses[e].name for e in occupants)
            report.hard.append(
                f"{_room_label(room_labels, room_idx)} at {_slot_label(period_labels, slot)} "
                f"is double-booked by {names}."
            )

    for (student, slot_idx), exams in student_slot_exams.items():
        if len(exams) > 1:
            slot = instance.slots[slot_idx]
            names = ", ".join(instance.courses[e].name for e in exams)
            report.hard.append(
                f"{_student_label(student_labels, student)} has overlapping exams "
                f"({names}) at {_slot_label(period_labels, slot)}."
            )

    for (student, day), period_exams in student_day_exams.items():
        periods = sorted(set(p for p, _ in period_exams))
        if len(periods) > 1:
            names = ", ".join(instance.courses[e].name for _, e in sorted(period_exams))
            report.soft.append(
                f"{_student_label(student_labels, student)} has {len(periods)} exams "
                f"bunched on Day {day + 1} ({names})."
            )
        ordered = sorted(period_exams)
        for (pa, ea), (pb, eb) in zip(ordered, ordered[1:]):
            if pb - pa == 1:
                report.soft.append(
                    f"{_student_label(student_labels, student)} has back-to-back exams "
                    f"{instance.courses[ea].name} and {instance.courses[eb].name} on "
                    f"Day {day + 1}, between {_period_label(period_labels, pa)} and "
                    f"{_period_label(period_labels, pb)}."
                )

    return report
