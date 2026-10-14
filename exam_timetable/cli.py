"""Command-line entry point.

    python main.py solve --algorithm hc --exams 10
    python main.py experiment
"""

import argparse
import random

from .algorithms import genetic_algorithm, hill_climbing, simulated_annealing
from .generator import generate_instance

ALGORITHM_CHOICES = {
    "hc": hill_climbing,
    "sa": simulated_annealing,
    "ga": genetic_algorithm,
}


def _solve(args: argparse.Namespace) -> None:
    rng = random.Random(args.seed)
    instance = generate_instance(args.exams, seed=args.seed)
    module = ALGORITHM_CHOICES[args.algorithm]
    result = module.run(instance, rng=rng)

    print(f"Algorithm: {args.algorithm}")
    print(f"Exams: {args.exams}, Students: {instance.num_students}")
    print(f"Rounds/iterations used: {result.iterations}")
    print(f"Final cost: {result.cost.total} (hard={result.cost.hard}, soft={result.cost.soft})")
    print(f"Elapsed: {result.elapsed_seconds:.2f}s")


def _experiment(args: argparse.Namespace) -> None:
    from .experiment import run_experiment

    run_experiment(seed=args.seed, results_dir=args.results_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Automated Exam Timetable Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    solve_parser = subparsers.add_parser("solve", help="Run one algorithm on one instance")
    solve_parser.add_argument("--algorithm", choices=ALGORITHM_CHOICES.keys(), default="hc")
    solve_parser.add_argument("--exams", type=int, default=10)
    solve_parser.add_argument("--seed", type=int, default=42)
    solve_parser.set_defaults(func=_solve)

    experiment_parser = subparsers.add_parser(
        "experiment", help="Run all three algorithms across problem sizes 10/30/60"
    )
    experiment_parser.add_argument("--seed", type=int, default=42)
    experiment_parser.add_argument("--results-dir", default="results")
    experiment_parser.set_defaults(func=_experiment)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
