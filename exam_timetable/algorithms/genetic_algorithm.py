"""Genetic Algorithm.

Tournament selection picks parents, single-point crossover combines them,
every child is then mutated gene-by-gene (each exam independently
reassigned with probability `gene_mutation_rate`), and elitism carries the
best few individuals unchanged into the next generation. Stops at
`max_generations` or once the best fitness plateaus for `plateau_limit`
generations.
"""

import random
import time

from ..cost import evaluate
from ..models import ProblemInstance
from ..operators import crossover_single_point, mutate, tournament_select
from ..result import SearchResult
from ..state import random_assignment


def run(
    instance: ProblemInstance,
    population_size: int = 40,
    max_generations: int = 200,
    gene_mutation_rate: float = 0.05,
    tournament_k: int = 3,
    elitism: int = 2,
    plateau_limit: int = 20,
    rng: random.Random = None,
) -> SearchResult:
    rng = rng or random.Random()
    start = time.perf_counter()

    population = [random_assignment(instance, rng) for _ in range(population_size)]
    fitness = [evaluate(instance, ind) for ind in population]

    best_idx = min(range(population_size), key=lambda i: fitness[i].total)
    best_assignment, best_cost = population[best_idx], fitness[best_idx]
    history = [best_cost.total]
    plateau_counter = 0

    for _ in range(max_generations):
        ranked = sorted(range(population_size), key=lambda i: fitness[i].total)
        new_population = [population[i] for i in ranked[:elitism]]

        while len(new_population) < population_size:
            parent1 = tournament_select(population, fitness, tournament_k, rng)
            parent2 = tournament_select(population, fitness, tournament_k, rng)
            child = crossover_single_point(parent1, parent2, rng)
            child = mutate(child, instance, rng, gene_rate=gene_mutation_rate)
            new_population.append(child)

        population = new_population
        fitness = [evaluate(instance, ind) for ind in population]

        gen_best_idx = min(range(population_size), key=lambda i: fitness[i].total)
        gen_best_cost = fitness[gen_best_idx]

        if gen_best_cost.total < best_cost.total:
            best_assignment, best_cost = population[gen_best_idx], gen_best_cost
            plateau_counter = 0
        else:
            plateau_counter += 1

        history.append(best_cost.total)
        if best_cost.total == 0 or plateau_counter >= plateau_limit:
            break

    return SearchResult(
        assignment=best_assignment,
        cost=best_cost,
        history=history,
        iterations=len(history) - 1,
        elapsed_seconds=time.perf_counter() - start,
    )
