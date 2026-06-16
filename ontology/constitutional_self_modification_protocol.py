"""
Constitutional Self-Modification Protocol.
"""

from __future__ import annotations

PRIMITIVE = "constitutional_self_modification_protocol"

DEPENDENCIES = [
    "constitutional_evolution_gate",
    "genealogical_responsibility",
]


class ConstitutionalSelfModificationProtocol:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE
        self.history = []

    def step(self, gate_result=None, mutation_descriptor=None):
        gate_result = gate_result or {}
        mutation_descriptor = mutation_descriptor or {}

        authorized = bool(gate_result.get("mutation_authorized", False))

        record = {
            "authorized": authorized,
            "gate_status": gate_result.get("gate_status", "unknown"),
            "evolutionary_confidence_score": gate_result.get(
                "evolutionary_confidence_score", 0.0
            ),
            "mutation_descriptor": mutation_descriptor,
            "rollback_available": authorized,
        }

        self.history.append(record)

        return {
            "primitive": "CONSTITUTIONAL_SELF_MODIFICATION_PROTOCOL",
            "mutation_recorded": True,
            "mutation_authorized": authorized,
            "rollback_available": record["rollback_available"],
            "protocol_history_length": len(self.history),
            "latest_record": record,
            "diagnostics": {
                "dependencies": DEPENDENCIES,
            },
        }
