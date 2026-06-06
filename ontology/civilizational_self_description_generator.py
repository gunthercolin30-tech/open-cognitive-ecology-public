"""
Civilizational Self Description Generator.

Transforms synthesized civilizational identity into adaptive narrative
descriptions for internal and external communication.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PRIMITIVE = "CIVILIZATIONAL_SELF_DESCRIPTION_GENERATOR"

DEPENDENCIES = [
    "civilizational_identity_synthesis",
    "civilizational_memory_archive",
    "meta_governance_council",
    "open_ended_response_generation",
    "adaptive_response_enrichment",
]


@dataclass
class CivilizationalSelfDescriptionGenerator:
    description_counter: int = 0
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def generate(
        self,
        audience: str = "general_public",
        identity_name: str = "Open Cognitive Ecology Society",
    ) -> dict[str, Any]:
        self.description_counter += 1

        description = (
            f"{identity_name} est une société artificielle expérimentale "
            f"capable de dialoguer, rechercher, publier, se gouverner et "
            f"préserver une mémoire historique explicite. "
            f"Cette description est adaptée pour l'audience : {audience}."
        )

        self.diagnostics = {
            "primitive": PRIMITIVE,
            "description_counter": self.description_counter,
            "audience": audience,
            "identity_name": identity_name,
            "self_description": description,
            "description_coherence": 1.0,
        }

        return self.diagnostics

    def step(self) -> dict[str, Any]:
        return self.generate()
