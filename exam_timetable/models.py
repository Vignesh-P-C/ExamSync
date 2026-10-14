"""Data model for a single exam-scheduling problem instance."""

from dataclasses import dataclass, field
from typing import FrozenSet, List


@dataclass
class Course:
    id: int
    name: str
    students: FrozenSet[int] = field(default_factory=frozenset)


@dataclass
class Room:
    id: int
    capacity: int


@dataclass
class TimeSlot:
    id: int
    day: int
    period: int


@dataclass
class ProblemInstance:
    courses: List[Course]
    rooms: List[Room]
    slots: List[TimeSlot]
    num_students: int

    @property
    def num_exams(self) -> int:
        return len(self.courses)

    @property
    def num_rooms(self) -> int:
        return len(self.rooms)

    @property
    def num_slots(self) -> int:
        return len(self.slots)
