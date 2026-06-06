from pathlib import Path
import json
from statistics import mean

EXPECTED_STATES = 3

class CardinalityPropagationMixin:

    def _cardinality_factor(self, partition_root):
        states = 0
        for node in ["alpha", "beta", "gamma"]:
            if (partition_root / node / "partition_state.json").exists():
                states += 1
        return max(0.0, min(1.0, states / EXPECTED_STATES))


def patch_notice():
    return {
        "primitive": "RECONCILIATION_CARDINALITY_PROPAGATION",
        "status": "installed",
        "expected_states": EXPECTED_STATES,
    }