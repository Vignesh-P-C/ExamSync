from io import StringIO
from pathlib import Path

import pytest

from exam_timetable.csv_loader import CsvSchemaError, load_instance_from_csv

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample"

COURSES_TEXT = "course_id,course_name\nC1,Course One\nC2,Course Two\n"
ROOMS_TEXT = "room_id,capacity\nR1,30\nR2,20\n"
ENROLLMENTS_TEXT = "student_id,course_id\nS1,C1\nS1,C2\nS2,C1\nS3,C2\n"


def COURSES():
    return StringIO(COURSES_TEXT)


def ROOMS():
    return StringIO(ROOMS_TEXT)


def ENROLLMENTS():
    return StringIO(ENROLLMENTS_TEXT)


def test_loads_valid_instance():
    instance, labels = load_instance_from_csv(COURSES(), ENROLLMENTS(), ROOMS(), days=2, periods_per_day=3)

    assert instance.num_exams == 2
    assert instance.num_rooms == 2
    assert instance.num_slots == 6
    assert instance.num_students == 3
    assert labels.course_ids == ["C1", "C2"]
    assert labels.room_ids == ["R1", "R2"]
    assert set(labels.student_ids) == {"S1", "S2", "S3"}

    c1 = instance.courses[0]
    assert c1.name == "Course One"
    assert len(c1.students) == 2  # S1, S2


def test_missing_column_raises():
    bad_courses = StringIO("course_id\nC1\n")
    with pytest.raises(CsvSchemaError):
        load_instance_from_csv(bad_courses, ENROLLMENTS(), ROOMS())


def test_duplicate_course_id_raises():
    dup_courses = StringIO("course_id,course_name\nC1,A\nC1,B\n")
    with pytest.raises(CsvSchemaError):
        load_instance_from_csv(dup_courses, ENROLLMENTS(), ROOMS())


def test_enrollment_unknown_course_raises():
    bad_enrollments = StringIO("student_id,course_id\nS1,DOES_NOT_EXIST\n")
    with pytest.raises(CsvSchemaError):
        load_instance_from_csv(COURSES(), bad_enrollments, ROOMS())


def test_non_positive_capacity_raises():
    bad_rooms = StringIO("room_id,capacity\nR1,0\n")
    with pytest.raises(CsvSchemaError):
        load_instance_from_csv(COURSES(), ENROLLMENTS(), bad_rooms)


def test_sample_files_load():
    instance, labels = load_instance_from_csv(
        str(SAMPLE_DIR / "courses.csv"),
        str(SAMPLE_DIR / "enrollments.csv"),
        str(SAMPLE_DIR / "rooms.csv"),
    )
    assert instance.num_exams == 30
    assert instance.num_rooms == 6
    assert instance.num_students == 300
