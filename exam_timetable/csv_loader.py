"""Builds a `ProblemInstance` from real CSV data instead of
`generator.py`'s synthetic sampling. This is the seam described in
CLAUDE.md §8.4 - nothing downstream (state, cost, operators, algorithms,
experiment harness) needs to know or care which one was used.

Expected files (see docs/csv_schema.md for the full schema):
  courses.csv      course_id, course_name
  enrollments.csv   student_id, course_id   (one row per student-course pair)
  rooms.csv         room_id, capacity
"""

import csv
import io
from dataclasses import dataclass, field
from typing import Dict, List, Union

from .models import Course, ProblemInstance, Room, TimeSlot

CsvSource = Union[str, "io.IOBase", bytes]
"""A CSV source is a filesystem path (str), raw CSV bytes, or any
file-like object with .read() (e.g. an io.StringIO, or Streamlit's
UploadedFile) - never a raw CSV string, which would be indistinguishable
from a path."""


class CsvSchemaError(ValueError):
    """Raised when an uploaded CSV is missing columns or otherwise malformed."""


@dataclass
class LoadedInstanceLabels:
    """Original (human-readable) identifiers, index-aligned with the
    `ProblemInstance` built alongside them - the instance only knows 0-based
    indices, but a frontend needs to show real course/room IDs."""

    course_ids: List[str] = field(default_factory=list)
    room_ids: List[str] = field(default_factory=list)
    student_ids: List[str] = field(default_factory=list)


def _read_rows(source: CsvSource, required_columns: List[str], label: str) -> List[Dict[str, str]]:
    if isinstance(source, bytes):
        text = source.decode("utf-8-sig")
    elif isinstance(source, str):
        with open(source, "r", encoding="utf-8-sig", newline="") as f:
            text = f.read()
    elif hasattr(source, "read"):
        raw = source.read()
        text = raw.decode("utf-8-sig") if isinstance(raw, bytes) else raw
    else:
        raise CsvSchemaError(f"{label}: unsupported input type {type(source)!r}")

    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise CsvSchemaError(f"{label}: file is empty")

    fieldnames = {name.strip() for name in reader.fieldnames}
    missing = [col for col in required_columns if col not in fieldnames]
    if missing:
        raise CsvSchemaError(
            f"{label}: missing required column(s) {missing}; found {sorted(fieldnames)}"
        )

    rows = [{k.strip(): (v.strip() if v is not None else "") for k, v in row.items()} for row in reader]
    if not rows:
        raise CsvSchemaError(f"{label}: no data rows")
    return rows


def load_instance_from_csv(
    courses_source: CsvSource,
    enrollments_source: CsvSource,
    rooms_source: CsvSource,
    days: int = 5,
    periods_per_day: int = 4,
):
    """Returns (ProblemInstance, LoadedInstanceLabels).

    Raises CsvSchemaError on missing columns, empty files, duplicate IDs,
    non-positive room capacities, or an enrollment referencing a course
    that isn't in courses.csv - these are user data-entry errors, not bugs,
    so they're reported with enough detail to fix the CSV.
    """
    course_rows = _read_rows(courses_source, ["course_id", "course_name"], "courses.csv")
    room_rows = _read_rows(rooms_source, ["room_id", "capacity"], "rooms.csv")
    enrollment_rows = _read_rows(enrollments_source, ["student_id", "course_id"], "enrollments.csv")

    course_id_to_idx: Dict[str, int] = {}
    course_ids: List[str] = []
    course_names: List[str] = []
    for row in course_rows:
        cid = row["course_id"]
        if not cid:
            raise CsvSchemaError("courses.csv: a row has an empty course_id")
        if cid in course_id_to_idx:
            raise CsvSchemaError(f"courses.csv: duplicate course_id {cid!r}")
        course_id_to_idx[cid] = len(course_ids)
        course_ids.append(cid)
        course_names.append(row["course_name"] or cid)

    room_id_to_idx: Dict[str, int] = {}
    room_ids: List[str] = []
    capacities: List[int] = []
    for row in room_rows:
        rid = row["room_id"]
        if not rid:
            raise CsvSchemaError("rooms.csv: a row has an empty room_id")
        if rid in room_id_to_idx:
            raise CsvSchemaError(f"rooms.csv: duplicate room_id {rid!r}")
        try:
            capacity = int(row["capacity"])
        except ValueError:
            raise CsvSchemaError(f"rooms.csv: room {rid!r} has non-integer capacity {row['capacity']!r}")
        if capacity <= 0:
            raise CsvSchemaError(f"rooms.csv: room {rid!r} has non-positive capacity {capacity}")
        room_id_to_idx[rid] = len(room_ids)
        room_ids.append(rid)
        capacities.append(capacity)

    student_id_to_idx: Dict[str, int] = {}
    student_ids: List[str] = []
    course_students: List[set] = [set() for _ in course_ids]
    for row in enrollment_rows:
        sid, cid = row["student_id"], row["course_id"]
        if not sid or not cid:
            raise CsvSchemaError("enrollments.csv: a row has an empty student_id or course_id")
        if cid not in course_id_to_idx:
            raise CsvSchemaError(
                f"enrollments.csv: course_id {cid!r} is not in courses.csv"
            )
        if sid not in student_id_to_idx:
            student_id_to_idx[sid] = len(student_ids)
            student_ids.append(sid)
        course_students[course_id_to_idx[cid]].add(student_id_to_idx[sid])

    if not course_ids:
        raise CsvSchemaError("courses.csv: no courses defined")
    if not room_ids:
        raise CsvSchemaError("rooms.csv: no rooms defined")
    if not student_ids:
        raise CsvSchemaError("enrollments.csv: no enrollments defined")
    if days <= 0 or periods_per_day <= 0:
        raise CsvSchemaError("days and periods_per_day must both be positive")

    courses = [
        Course(id=i, name=course_names[i], students=frozenset(course_students[i]))
        for i in range(len(course_ids))
    ]
    rooms = [Room(id=i, capacity=capacities[i]) for i in range(len(room_ids))]
    slots = [
        TimeSlot(id=day * periods_per_day + period, day=day, period=period)
        for day in range(days)
        for period in range(periods_per_day)
    ]

    instance = ProblemInstance(
        courses=courses, rooms=rooms, slots=slots, num_students=len(student_ids)
    )
    labels = LoadedInstanceLabels(
        course_ids=course_ids, room_ids=room_ids, student_ids=student_ids
    )
    return instance, labels
