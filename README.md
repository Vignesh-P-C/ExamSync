# Automated Exam Timetable Generator

AI Course Project (Module 3 — Local Search). Hill-Climbing, Simulated
Annealing, and a Genetic Algorithm each solve the same exam-to-(time slot,
room) assignment problem, sharing one state representation and cost
function, so they can be compared fairly.

## Structure

```
exam_timetable/
  models.py        Course, Room, TimeSlot, ProblemInstance
  generator.py      synthetic problem-instance generator (seeded, reproducible)
  state.py          the state: one (slot, room) pair per exam
  cost.py           the shared cost function (hard + soft violations)
  operators.py      shift/swap moves, crossover, mutation, tournament selection
  result.py         common SearchResult type returned by all three algorithms
  algorithms/
    hill_climbing.py        steepest-ascent, exhaustive neighborhood
    simulated_annealing.py  geometric cooling, Metropolis acceptance
    genetic_algorithm.py    tournament selection + crossover + mutation + elitism
  experiment.py     runs all three algorithms on 10/30/60-exam instances,
                    writes results/comparison.csv and results/plots/*.png
  cli.py            argparse entry point
tests/              unit tests for cost function, state ops, generator, algorithms
main.py             `python main.py ...`
```

## Setup

```
pip install -r requirements.txt
```

## Run

Solve a single instance with one algorithm:

```
python main.py solve --algorithm hc --exams 10
python main.py solve --algorithm sa --exams 30
python main.py solve --algorithm ga --exams 60
```

Run the full comparison (all three algorithms x 10/30/60 exams), producing
`results/comparison.csv` and `results/plots/*.png`:

```
python main.py experiment
```

## Tests

```
pytest
```

## Notes

- Hard violations (student double-booked, room over capacity, two exams
  clashing in the same room/slot) are weighted 10; soft violations (a
  student with back-to-back exams, exams bunched onto one day) are weighted
  1. Both the weights and the algorithms' hyperparameters (iteration caps,
  cooling schedule, population size, mutation rate) are initial defaults —
  per the proposal, these get tuned during Review 2.
- No external optimization/metaheuristic libraries are used (no DEAP,
  PyGAD, or scipy.optimize) — the state, operators, and cost function are
  all implemented directly, per the proposal's declarations. matplotlib is
  used only for plotting results.
