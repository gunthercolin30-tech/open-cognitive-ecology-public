from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable, Dict, Optional

PRIMITIVE = "minimal_architectural_dna"
DESCRIPTION = "Minimal architectural DNA."
DEPENDENCIES = [
    "anti_closure_metaconstraint",
    "genealogical_responsibility",
    "human_non_replacement",
    "future_openness",
]


class MinimalDNAPrimitive:
    def __init__(
        self,
        invariants: Dict[str, Any],
        mutable_traits: Optional[Dict[str, Any]] = None,
        viability_function: Optional[Callable[[Dict[str, Any]], bool]] = None,
    ):
        if not invariants:
            raise ValueError("Minimal DNA requires at least one invariant.")

        self._invariants = deepcopy(invariants)
        self._mutable_traits = deepcopy(mutable_traits or {})
        self._viability_function = viability_function

        if not self.is_viable():
            raise ValueError("Initial Minimal DNA configuration is not viable.")

    def genome(self) -> Dict[str, Any]:
        genome = deepcopy(self._invariants)
        genome.update(deepcopy(self._mutable_traits))
        return genome

    def is_viable(self) -> bool:
        genome = self.genome()

        for key, value in self._invariants.items():
            if genome.get(key) != value:
                return False

        if self._viability_function is not None:
            return bool(self._viability_function(genome))

        return True

    def step(self) -> Dict[str, Any]:
        viable = self.is_viable()
        return {
            "primitive": "MINIMAL_ARCHITECTURAL_DNA",
            "minimal_dna_integrity_score": 1.0 if viable else 0.0,
            "viable": viable,
            "ready_for_transmission": viable,
            "diagnostics": {
                "invariant_count": len(self._invariants),
                "mutable_trait_count": len(self._mutable_traits),
                "dependencies": DEPENDENCIES,
            },
        }
