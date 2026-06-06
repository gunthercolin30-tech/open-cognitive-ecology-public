"""
Civilizational CLI Interface.
Interactive command-line interface for the artificial civilization.
"""

from __future__ import annotations

from ontology.continuous_civilizational_scheduler import ContinuousCivilizationalScheduler
from ontology.civilizational_state_persistence import CivilizationalStatePersistence

PRIMITIVE = "CIVILIZATIONAL_CLI_INTERFACE"

DEPENDENCIES = [
    "continuous_civilizational_scheduler",
    "civilizational_state_persistence",
]


class CivilizationalCLIInterface:
    def __init__(self) -> None:
        self.primitive = PRIMITIVE
        self.scheduler = ContinuousCivilizationalScheduler()
        self.persistence = CivilizationalStatePersistence()

    def step(self, command: str = "status") -> dict:
        command = str(command).strip().lower()

        if command == "run":
            return self.scheduler.step(cycles=1)

        if command == "run10":
            return self.scheduler.step(cycles=10)

        if command == "status":
            try:
                return self.persistence.load()
            except Exception:
                return {
                    "primitive": self.primitive,
                    "command": "status",
                    "success": False,
                    "message": "No saved state found.",
                }

        if command == "help":
            return {
                "primitive": self.primitive,
                "available_commands": [
                    "status",
                    "run",
                    "run10",
                    "help",
                ],
            }

        return {
            "primitive": self.primitive,
            "command": command,
            "success": False,
            "message": "Unknown command.",
        }
