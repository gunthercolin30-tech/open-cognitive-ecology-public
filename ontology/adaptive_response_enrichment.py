"""
Adaptive Response Enrichment

Primitive enrichissant les réponses du représentant suprême à partir de
l'historique conversationnel et de l'état courant de la société.
"""

from __future__ import annotations

PRIMITIVE = "adaptive_response_enrichment"

DEPENDENCIES = ['supreme_representative_runtime', 'conversation_memory_archive', 'civilizational_dashboard', 'longitudinal_society_observatory']


class AdaptiveResponseEnrichment:
    def __init__(self) -> None:
        from ontology.civilizational_dashboard import CivilizationalDashboard
        from ontology.conversation_memory_archive import ConversationMemoryArchive
        from ontology.longitudinal_society_observatory import (
            LongitudinalSocietyObservatory,
        )

        self.dashboard = CivilizationalDashboard()
        self.archive = ConversationMemoryArchive()
        self.observatory = LongitudinalSocietyObservatory()

    def enrich(self, base_response: str) -> str:
        dashboard_state = self.dashboard.step()
        archive_state = self.archive.step()
        observatory_state = self.observatory.step()

        return (
            base_response
            + "\n\n"
            + "Contexte actuel : "
            + f"population={dashboard_state.get('population_size', 0)}, "
            + f"viabilité={dashboard_state.get('global_viability_score', 0.0):.3f}, "
            + f"archives={archive_state.get('archive_count', 0)}, "
            + f"historique={observatory_state.get('history_length', 0)}."
        )

    def step(self) -> dict:
        return {
            "primitive": PRIMITIVE,
            "enrichment_ready": True,
            "classification": "Adaptive Response Enrichment Operational",
            "diagnostics": {
                "dependencies": DEPENDENCIES,
            },
        }
