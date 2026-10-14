"""Common return type for all three algorithms, so the experiment runner
can treat them interchangeably."""

from dataclasses import dataclass, field
from typing import List

from .cost import CostResult
from .state import Assignment


@dataclass
class SearchResult:
    assignment: Assignment
    cost: CostResult
    history: List[int] = field(default_factory=list)  # best cost.total per round
    iterations: int = 0
    elapsed_seconds: float = 0.0
