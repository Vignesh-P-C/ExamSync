from exam_timetable.generator import generate_instance


def test_generated_instance_has_requested_sizes():
    instance = generate_instance(num_exams=30, num_rooms=6, days=5, periods_per_day=4, seed=7)
    assert instance.num_exams == 30
    assert instance.num_rooms == 6
    assert instance.num_slots == 20


def test_every_course_has_at_least_one_student():
    instance = generate_instance(num_exams=10, seed=7)
    for course in instance.courses:
        assert len(course.students) >= 1
        assert all(0 <= s < instance.num_students for s in course.students)


def test_generation_is_reproducible_with_same_seed():
    a = generate_instance(num_exams=10, seed=123)
    b = generate_instance(num_exams=10, seed=123)
    assert [c.students for c in a.courses] == [c.students for c in b.courses]
