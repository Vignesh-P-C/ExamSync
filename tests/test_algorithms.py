import random

import pytest

from exam_timetable.algorithms import genetic_algorithm, hill_climbing, simulated_annealing
from exam_timetable.generator import generate_instance

# Small, generously resourced instance so cost 0 is reachable quickly.
INSTANCE = generate_instance(
    num_exams=6, num_rooms=6, days=5, periods_per_day=4, seed=0
)


@pytest.mark.parametrize(
    "module,kwargs",
    [
        (hill_climbing, {"max_iters": 30}),
        (simulated_annealing, {"max_iters": 1000}),
        (genetic_algorithm, {"population_size": 20, "max_generations": 50}),
    ],
)
def test_algorithm_runs_and_does_not_worsen(module, kwargs):
    rng = random.Random(0)
    result = module.run(INSTANCE, rng=rng, **kwargs)

    assert len(result.assignment) == INSTANCE.num_exams
    assert result.cost.total >= 0
    assert result.history[-1] <= result.history[0]
    assert result.cost.total == result.history[-1]
