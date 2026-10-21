# CSV input schema

(Issue #4.) Three files, all plain CSV with a header row. Sample files
that satisfy this schema are in [`data/sample/`](../data/sample/) and
load cleanly in the frontend (`streamlit run app.py`, "Upload CSVs").

## `courses.csv`

One row per exam to schedule.

| Column | Type | Required | Notes |
|---|---|---|---|
| `course_id` | string | yes | Must be unique. Used to match rows in `enrollments.csv`. |
| `course_name` | string | yes | Display name shown in the timetable grid and violations report. |

## `rooms.csv`

One row per room available for exams.

| Column | Type | Required | Notes |
|---|---|---|---|
| `room_id` | string | yes | Must be unique. |
| `capacity` | integer > 0 | yes | Seats available; drives the over-capacity hard violation. |

## `enrollments.csv`

One row per (student, course) pair — **the** source of every student-side
conflict check (double-booking, back-to-back, bunching). A student with
no row here is invisible to the algorithm.

| Column | Type | Required | Notes |
|---|---|---|---|
| `student_id` | string | yes | Any stable identifier; doesn't need to be numeric. |
| `course_id` | string | yes | Must match a `course_id` in `courses.csv`, or the file is rejected. |

## Exam period structure

Not a file — a simple `days` x `periods_per_day` config, entered directly
in the frontend sidebar (the loader's own function default is 5 days, 4
periods/day, matching `generator.py`'s synthetic instances, but the
frontend's own default is 5 days x 3 periods/day, labeled "Morning
(9-12)" / "Noon (12-3)" / "Evening (3-6)" — editable in the sidebar, and
shown throughout the timetable/violations display instead of generic
"Period 1/2/3" whenever the label count matches `periods_per_day`). This
assumes a uniform grid of slots; non-uniform slot structures are a
stretch goal (Issue #14) not currently supported.

## Validation

`exam_timetable/csv_loader.py`'s `load_instance_from_csv()` rejects (with
a specific error message) a CSV that's empty, missing a required column,
has a duplicate `course_id`/`room_id`, a non-positive/non-integer room
capacity, or an enrollment referencing a `course_id` not present in
`courses.csv`. These are data-entry errors to fix in the CSV, not bugs in
the loader.

## What's explicitly not supported yet

Per CLAUDE.md §8.1 — would need changes to `models.py`/`cost.py`:
- Exams with different durations (every exam currently occupies exactly
  one slot).
- Pre-locked/fixed exams (Issue #15, stretch).
- Room-type restrictions, e.g. a course needing a lab specifically rather
  than any sufficiently large room (Issue #16, stretch).
- Invigilator/staff conflicts.

Student and course *display* names beyond what's listed above (e.g. a
separate "full name" column) aren't used by the algorithm and aren't part
of this schema — `course_name` already covers course display, and
`student_id` is shown as-is in the violations report.
