from __future__ import annotations
import itertools, random
from typing import Any

SCHEMA_VERSION = "1.0.0"
DEFAULT_SEED = 61001
TERMINAL_STATES = ("REJECTED", "COMMITTED", "ROLLED_BACK", "QUARANTINE")
FAILURE_PHASES = ("before_mutation", "after_mutation", "rollback_failed", "impossible_state")


def structured_cases(seed: int = DEFAULT_SEED, limit: int = 256) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    cases: list[dict[str, Any]] = []
    for phase, persist, duplicated, gate, variant in itertools.product(
        FAILURE_PHASES, (False, True), (False, True), ("absent", "valid", "corrupt"), (0, 1, 2, 3)
    ):
        cases.append({
            "phase": phase,
            "persist": persist,
            "duplicated": duplicated,
            "gate": gate,
            "candidate_id": f"candidate-{len(cases):04d}",
            "proposal_id": f"proposal-{len(cases):04d}",
        })
    rng.shuffle(cases)
    return cases[:limit]


def permutation_cases() -> list[list[str]]:
    base = ["functional", "fast_guard", "fast_acceptance", "final_lock"]
    return [list(item) for item in itertools.permutations(base)]
