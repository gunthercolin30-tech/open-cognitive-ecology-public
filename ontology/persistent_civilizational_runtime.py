"""
Persistent Civilizational Runtime.
Loads the latest saved state, executes a governance cycle, and saves the updated state.
"""

from __future__ import annotations

from ontology.civilizational_state_persistence import CivilizationalStatePersistence
from ontology.autonomous_civilizational_governor import AutonomousCivilizationalGovernor

PRIMITIVE = "PERSISTENT_CIVILIZATIONAL_RUNTIME"

DEPENDENCIES = [
    "civilizational_state_persistence",
    "autonomous_civilizational_governor",
]


class PersistentCivilizationalRuntime:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE
        self.persistence = CivilizationalStatePersistence()
        self.governor = AutonomousCivilizationalGovernor()

    def step(self) -> dict:
        try:
            load_result = self.persistence.load()
            state = load_result.get("state", {})
        except Exception:
            load_result = {
                "primitive": self.primitive,
                "action": "load",
                "success": False,
                "state": {},
            }
            state = {}

        governance_result = self.governor.step(
            unified_consciousness_score=state.get(
                "unified_consciousness_score", 0.917
            ),
            civilizational_autonomy_score=state.get(
                "civilizational_autonomy_score", 0.9367
            ),
            global_viability_score=state.get(
                "global_viability_score", 0.9310
            ),
            constitutional_integrity_score=state.get(
                "constitutional_integrity_score", 0.95
            ),
        )

        updated_state = dict(state)
        updated_state.update(governance_result)

        save_result = self.persistence.save(updated_state)

        return {
            "primitive": self.primitive,
            "load_result": load_result,
            "governance_result": governance_result,
            "save_result": save_result,
            "runtime_continuity": True,
        }
