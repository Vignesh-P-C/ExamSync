from exam_timetable.cost import evaluate
from exam_timetable.models import Course, ProblemInstance, Room, TimeSlot

ROOMS = [Room(id=0, capacity=10), Room(id=1, capacity=10)]
SLOTS = [
    TimeSlot(id=0, day=0, period=0),
    TimeSlot(id=1, day=0, period=1),
    TimeSlot(id=2, day=1, period=0),
]


def make_instance(course0_students, course1_students):
    courses = [
        Course(id=0, name="C0", students=frozenset(course0_students)),
        Course(id=1, name="C1", students=frozenset(course1_students)),
    ]
    return ProblemInstance(courses=courses, rooms=ROOMS, slots=SLOTS, num_students=3)


def test_no_violations_on_disjoint_well_spread_exams():
    instance = make_instance({0}, {1})
    assignment = [(0, 0), (2, 1)]  # different days, disjoint students
    result = evaluate(instance, assignment)
    assert result.hard == 0
    assert result.soft == 0


def test_room_capacity_violation():
    small_room_instance = ProblemInstance(
        courses=[Course(id=0, name="C0", students=frozenset({0, 1}))],
        rooms=[Room(id=0, capacity=1)],
        slots=SLOTS,
        num_students=2,
    )
    assignment = [(0, 0)]  # 2 students into a 1-seat room
    result = evaluate(small_room_instance, assignment)
    assert result.hard == 1
    assert result.soft == 0


def test_room_slot_clash():
    instance = make_instance({0}, {1})
    assignment = [(0, 0), (0, 0)]  # same slot AND same room
    result = evaluate(instance, assignment)
    assert result.hard == 1
    assert result.soft == 0


def test_student_double_booked():
    instance = make_instance({0}, {0})  # shared student
    assignment = [(0, 0), (0, 1)]  # same slot, different rooms
    result = evaluate(instance, assignment)
    assert result.hard == 1
    assert result.soft == 0


def test_back_to_back_and_bunching_soft_violation():
    instance = make_instance({0}, {0})  # shared student
    assignment = [(0, 0), (1, 1)]  # same day, adjacent periods, different rooms
    result = evaluate(instance, assignment)
    assert result.hard == 0
    assert result.soft == 2  # 1 bunching + 1 back-to-back


def test_total_applies_weights():
    instance = make_instance({0, 1}, {1})
    assignment = [(0, 0), (0, 0)]  # clash (hard) + nothing else
    result = evaluate(instance, assignment)
    assert result.total == 10 * result.hard + result.soft
