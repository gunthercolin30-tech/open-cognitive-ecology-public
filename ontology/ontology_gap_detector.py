"""
ONTOLOGY_GAP_DETECTOR

Detects conceptual gaps by comparing proposed primitives with the current ontology inventory.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

from ontology.civilizational_self_extension import CivilizationalSelfExtension


@dataclass
class OntologyGapDetector:
    primitive_name: str = "ONTOLOGY_GAP_DETECTOR"

    def _inventory_path(self):
        from pathlib import Path
        return Path(__file__).resolve().parents[1] / "ontology_inventory.txt"

    def _load_inventory(self) -> set:
        path = self._inventory_path()
        if not path.exists():
            return set()
        return {
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }

    def step(self) -> Dict:
        inventory = self._load_inventory()
        proposals = CivilizationalSelfExtension().step()["proposed_primitives"]

        gaps: List[Dict] = []
        for proposal in proposals:
            name = proposal["primitive_name"]
            if name not in inventory:
                gaps.append({
                    "primitive_name": name,
                    "priority_rank": proposal["rank"],
                    "expected_benefit": proposal["expected_benefit"],
                    "missing": True,
                    "script_name": proposal["script_name"],
                })

        gaps.sort(
            key=lambda item: (
                item["priority_rank"],
                -item["expected_benefit"]
            )
        )

        return {
            "primitive": self.primitive_name,
            "inventory_size": len(inventory),
            "gap_count": len(gaps),
            "highest_priority_gap": gaps[0]["primitive_name"] if gaps else None,
            "gaps": gaps,
            "status": "operational",
        }


if __name__ == "__main__":
    from pprint import pprint
    pprint(OntologyGapDetector().step())
