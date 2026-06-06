"""
AUTOMATED_PRIMITIVE_DESIGNER

Generates implementation blueprints for missing ontology primitives.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

from ontology.ontology_gap_detector import OntologyGapDetector


@dataclass
class AutomatedPrimitiveDesigner:
    primitive_name: str = "AUTOMATED_PRIMITIVE_DESIGNER"

    def _make_blueprint(self, gap: Dict) -> Dict:
        name = gap["primitive_name"]
        class_name = "".join(part.capitalize() for part in name.split("_"))
        test_command = (
            'python3 -c "from ontology.'
            + name
            + ' import '
            + class_name
            + ' as P; from pprint import pprint; pprint(P().step())"'
        )
        return {
            "primitive_name": name,
            "class_name": class_name,
            "module_path": "ontology/" + name + ".py",
            "refine_script": "refine_" + name + ".py",
            "test_command": test_command,
            "expected_benefit": gap["expected_benefit"],
        }

    def step(self) -> Dict:
        gaps = OntologyGapDetector().step()["gaps"]
        blueprints: List[Dict] = [self._make_blueprint(g) for g in gaps]

        return {
            "primitive": self.primitive_name,
            "blueprint_count": len(blueprints),
            "highest_priority_blueprint": (
                blueprints[0]["primitive_name"] if blueprints else None
            ),
            "blueprints": blueprints,
            "status": "operational",
        }


if __name__ == "__main__":
    from pprint import pprint
    pprint(AutomatedPrimitiveDesigner().step())
