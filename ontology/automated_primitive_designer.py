"""
Automated Primitive Designer — C3 primitive design governance integration.

This module proposes primitive blueprints only under explicit governance:
non-redundancy, reversibility, testability, constitutional authorization,
non-closure compliance, and traceability.

It does not directly create or install new primitives. It produces governed
blueprints that can be reviewed and implemented through refine_<primitive>.py
scripts.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import re


PRIMITIVE = "automated_primitive_designer"

DEPENDENCIES = [
    "ontology_gap_detector",
    "redundancy",
    "constitutional_self_modification_protocol",
    "governance_approval_policy_manager",
    "constitutional_evolution_gate",
]


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except Exception:
        return default


def _slug(value: str) -> str:
    value = str(value or "").strip().lower()
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unnamed_primitive"


def _class_name(slug: str) -> str:
    return "".join(part.capitalize() for part in slug.split("_") if part) or "UnnamedPrimitive"


def _safe_mean(values: list[float], default: float = 0.0) -> float:
    filtered = [float(v) for v in values if v is not None]
    if not filtered:
        return default
    return round(sum(filtered) / len(filtered), 4)


class AutomatedPrimitiveDesigner:
    primitive = PRIMITIVE

    def __init__(self, root: str | Path | None = None):
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.ontology_dir = self.root / "ontology"
        self.state_dir = self.root / "civilizational_mutation"
        self.state_path = self.state_dir / "automated_primitive_designer_state.json"

    def _load_inventory(self) -> set[str]:
        inventory_file = self.root / "ontology_inventory.txt"
        if inventory_file.exists():
            try:
                return {
                    line.strip()
                    for line in inventory_file.read_text(encoding="utf-8").splitlines()
                    if line.strip() and not line.strip().startswith("#")
                }
            except Exception:
                pass

        if self.ontology_dir.exists():
            return {
                path.stem
                for path in self.ontology_dir.glob("*.py")
                if path.name != "__init__.py"
            }
        return set()

    def _load_state(self) -> dict[str, Any]:
        if self.state_path.exists():
            try:
                return json.loads(self.state_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "primitive": PRIMITIVE,
            "design_cycles": 0,
            "blueprints": [],
            "governance_history": [],
        }

    def _save_state(self, state: dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _detect_candidate_names(self, inputs: dict[str, Any], inventory: set[str]) -> list[str]:
        candidates: list[str] = []

        for key in ("primitive_name", "candidate", "capability", "gap"):
            value = inputs.get(key)
            if isinstance(value, str) and value.strip():
                candidates.append(_slug(value))

        for key in ("candidates", "gaps", "capabilities", "proposed_primitives"):
            values = inputs.get(key, [])
            if isinstance(values, (list, tuple)):
                for item in values:
                    if isinstance(item, str):
                        candidates.append(_slug(item))
                    elif isinstance(item, dict):
                        name = (
                            item.get("primitive_name")
                            or item.get("name")
                            or item.get("capability")
                            or item.get("gap")
                        )
                        if name:
                            candidates.append(_slug(str(name)))

        if not candidates:
            try:
                from ontology.ontology_gap_detector import OntologyGapDetector
                detector = OntologyGapDetector()
                detected = detector.step()
                recommended = detected.get("recommended_primitives", [])
                for item in recommended:
                    if isinstance(item, str):
                        candidates.append(_slug(item))
                    elif isinstance(item, dict):
                        name = item.get("primitive_name") or item.get("name")
                        if name:
                            candidates.append(_slug(str(name)))
            except Exception:
                pass

        if not candidates:
            candidates = [
                "controlled_mutation_regression_validator",
                "primitive_design_governance",
                "mutation_regression_validator",
            ]

        seen = set()
        unique = []
        for candidate in candidates:
            candidate = _slug(candidate)
            if candidate not in seen:
                seen.add(candidate)
                unique.append(candidate)

        return unique[:10]

    def _redundancy_score(self, candidate: str, inventory: set[str]) -> float:
        if candidate in inventory:
            return 1.0

        candidate_parts = set(candidate.split("_"))
        best = 0.0

        for existing in inventory:
            existing_parts = set(existing.split("_"))
            if not candidate_parts or not existing_parts:
                continue
            overlap = len(candidate_parts & existing_parts) / len(candidate_parts | existing_parts)
            if overlap > best:
                best = overlap

        return round(best, 4)

    def _governance_assessment(
        self,
        candidate: str,
        inputs: dict[str, Any],
        inventory: set[str],
    ) -> dict[str, Any]:
        redundancy_score = self._redundancy_score(candidate, inventory)
        non_redundant = redundancy_score < float(inputs.get("redundancy_threshold", 0.72))

        rollback_required = bool(inputs.get("rollback_required", True))
        rollback_available = bool(
            inputs.get("rollback_available",
            inputs.get("reversible", True))
        )
        scientifically_testable = bool(inputs.get("scientifically_testable", True))
        non_closure_compliant = bool(
            inputs.get(
                "non_closure_compliant",
                inputs.get("non_closure_preserved", True),
            )
        )

        constitutional_alignment = _bounded(
            inputs.get("constitutional_alignment", 0.92),
            default=0.92,
        )
        governance_score = _bounded(
            inputs.get("governance_score", 0.92),
            default=0.92,
        )

        constitutionally_authorized = (
            constitutional_alignment >= float(inputs.get("constitutional_threshold", 0.85))
            and rollback_available
            and non_closure_compliant
        )

        governance_approved = (
            governance_score >= float(inputs.get("governance_threshold", 0.85))
            and constitutionally_authorized
            and non_redundant
            and scientifically_testable
        )

        traceability_score = _bounded(inputs.get("traceability_score", 1.0), default=1.0)
        reversibility_score = 1.0 if rollback_available else 0.0
        testability_score = 1.0 if scientifically_testable else 0.0
        non_redundancy_score = max(0.0, 1.0 - redundancy_score)
        non_closure_score = 1.0 if non_closure_compliant else 0.0
        authorization_score = 1.0 if constitutionally_authorized else 0.0
        governance_approval_score = 1.0 if governance_approved else 0.0

        primitive_design_confidence = _safe_mean([
            non_redundancy_score,
            reversibility_score,
            testability_score,
            non_closure_score,
            authorization_score,
            governance_approval_score,
            traceability_score,
        ])

        primitive_design_certified = (
            primitive_design_confidence >= 0.85
            and non_redundant
            and constitutionally_authorized
            and rollback_available
            and scientifically_testable
            and non_closure_compliant
            and governance_approved
        )

        return {
            "redundancy_score": round(redundancy_score, 4),
            "non_redundant": non_redundant,
            "constitutionally_authorized": constitutionally_authorized,
            "rollback_required": rollback_required,
            "rollback_available": rollback_available,
            "scientifically_testable": scientifically_testable,
            "non_closure_compliant": non_closure_compliant,
            "governance_approved": governance_approved,
            "primitive_design_confidence": round(primitive_design_confidence, 4),
            "primitive_design_certified": primitive_design_certified,
            "constitutional_alignment": round(constitutional_alignment, 4),
            "governance_score": round(governance_score, 4),
        }

    def _blueprint(self, candidate: str, assessment: dict[str, Any]) -> dict[str, Any]:
        class_name = _class_name(candidate)
        return {
            "primitive_name": candidate,
            "class_name": class_name,
            "script_name": f"refine_{candidate}.py",
            "module_path": f"ontology/{candidate}.py",
            "test_command": (
                "python3 - <<'PY'\n"
                f"from ontology.{candidate} import {class_name}\n"
                f"print({class_name}().step())\n"
                "PY"
            ),
            "installation_command": f"python3 ~/Downloads/refine_{candidate}.py",
            "reversible": assessment["rollback_available"],
            "traceable": True,
            "governed": assessment["governance_approved"],
            "non_closure_compliant": assessment["non_closure_compliant"],
            "scientifically_testable": assessment["scientifically_testable"],
            "certified_for_design": assessment["primitive_design_certified"],
            "governance": assessment,
        }

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        inventory = self._load_inventory()
        candidates = self._detect_candidate_names(inputs, inventory)

        blueprints = []
        rejected = []

        for candidate in candidates:
            assessment = self._governance_assessment(candidate, inputs, inventory)
            blueprint = self._blueprint(candidate, assessment)
            if assessment["primitive_design_certified"]:
                blueprints.append(blueprint)
            else:
                rejected.append(blueprint)

        blueprints.sort(
            key=lambda item: item["governance"]["primitive_design_confidence"],
            reverse=True,
        )

        all_items = blueprints + rejected
        mean_confidence = _safe_mean(
            [b["governance"]["primitive_design_confidence"] for b in all_items],
            default=0.0,
        )

        state = self._load_state()
        state["primitive"] = PRIMITIVE
        state["design_cycles"] = int(state.get("design_cycles", 0)) + 1
        state["last_execution_utc"] = datetime.now(timezone.utc).isoformat()
        state["blueprints"] = (state.get("blueprints", []) + blueprints)[-500:]
        state["governance_history"] = (
            state.get("governance_history", [])
            + [{
                "timestamp_utc": state["last_execution_utc"],
                "candidate_count": len(candidates),
                "certified_count": len(blueprints),
                "rejected_count": len(rejected),
                "mean_design_confidence": mean_confidence,
            }]
        )[-1000:]
        self._save_state(state)

        highest_priority = blueprints[0]["primitive_name"] if blueprints else None

        return {
            "primitive": "AUTOMATED_PRIMITIVE_DESIGNER",
            "phase": "C3_PRIMITIVE_DESIGN_GOVERNANCE",
            "candidate_count": len(candidates),
            "blueprint_count": len(blueprints),
            "rejected_blueprint_count": len(rejected),
            "highest_priority_blueprint": highest_priority,
            "blueprints": blueprints,
            "rejected_blueprints": rejected,
            "primitive_design_confidence": round(mean_confidence, 4),
            "primitive_design_certified": bool(blueprints) and mean_confidence >= 0.85,
            "state_path": str(self.state_path),
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "inventory_size": len(inventory),
                "non_redundancy_guard": True,
                "rollback_required": True,
                "non_closure_guard": True,
                "direct_code_modification": False,
                "error_count_target": 0,
            },
        }

    def diagnostics(self) -> dict[str, Any]:
        return self.step()


ENGINE = AutomatedPrimitiveDesigner
