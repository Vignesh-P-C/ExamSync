"""Regenerate data/sample/enrollments.csv (deterministic, seeded).

The sample is modelled on how real departments enrol students: students
belong to a programme and take most of that programme's courses, and some take one
elective from a small related pool. That keeps the conflict graph sparse enough that
the sample can be scheduled on the frontend's default 5 days x 3 periods
grid (15 slots). The earlier fully-random sample had 432 of 435 course
pairs sharing a student, which needs >= 28 slots and could never reach 0
hard violations on the default grid.

    python scripts/make_sample_data.py

courses.csv and rooms.csv are hand-written and left untouched.
"""

import csv
import random
from pathlib import Path

SEED = 2026
SAMPLE_DIR = Path(__file__).resolve().parent.parent / "data" / "sample"

# programme name -> (course ids, number of students)
PROGRAMMES = {
    "Computer Science": (["C001", "C002", "C003", "C004", "C005", "C006"], 80),
    "AI & Software": (["C007", "C008", "C009", "C010", "C011", "C030"], 70),
    "Mathematics": (["C012", "C013", "C014", "C015", "C016", "C017"], 60),
    "Physics & Electronics": (["C018", "C019", "C020", "C021", "C022", "C029"], 50),
    "Business": (["C023", "C024", "C025", "C026", "C027", "C028"], 40),
}
CORE_PER_STUDENT = 4  # of the programme's 6 courses

# Cross-programme electives: each programme's students may take ONE elective
# from a small pool of related courses. Keeping the pools small and the
# take-up partial is what keeps the conflict graph sparse (a free choice of
# any outside course links every programme to every other one).
ELECTIVE_POOL = {
    "Computer Science": ["C007", "C010"],
    "AI & Software": ["C002", "C003"],
    "Mathematics": ["C018", "C019"],
    "Physics & Electronics": ["C012", "C014"],
    "Business": ["C016", "C017"],
}
ELECTIVE_TAKE_UP = 0.4  # fraction of students who take an elective


def build_rows(seed=SEED):
    rng = random.Random(seed)
    rows, student_no = [], 1
    for name, (courses, n_students) in PROGRAMMES.items():
        for _ in range(n_students):
            sid = f"S{student_no:03d}"
            student_no += 1
            chosen = rng.sample(courses, CORE_PER_STUDENT)
            if rng.random() < ELECTIVE_TAKE_UP:
                chosen.append(rng.choice(ELECTIVE_POOL[name]))
            rows.extend((sid, c) for c in sorted(chosen))
    return rows


def main():
    rows = build_rows()
    path = SAMPLE_DIR / "enrollments.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["student_id", "course_id"])
        writer.writerows(rows)
    print(f"wrote {len(rows)} enrollments to {path}")


if __name__ == "__main__":
    main()
