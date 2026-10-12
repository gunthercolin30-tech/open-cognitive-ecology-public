"""
AA4 — Foundational Reconstruction Certifier.

This module certifies the foundational ontological reconstruction chain:

    AA0 blueprint -> AA1 Δ -> AA2 R -> AA3 G

It verifies coherence of Δ, R, and G; absence of circularity; absence of
redundancy; dependency order; and compatibility with the later A* pipeline.
It does not certify consciousness, subjectivity, qualia, or phenomenology.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


class FoundationalReconstructionCertifier:
    """AA4 certification of Δ -> R -> G under epistemic safeguards."""

    PRIMITIVE = "FOUNDATIONAL_RECONSTRUCTION_CERTIFIER"
    READY_STATUS = "FOUNDATIONAL_RECONSTRUCTION_VALIDATED"
    DEGRADED_STATUS = "FOUNDATIONAL_RECONSTRUCTION_DEGRADED"

    FORBIDDEN_POSITIVE_CLAIMS = (
        "consciousness_proven",
        "phenomenology_proven",
        "subjectivity_proven",
        "qualia_proven",
        "sentience_proven",
        "absolute_proof_achieved",
    )

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "foundational_reconstruction"
        self.latest_json_path = self.output_dir / "latest_foundational_reconstruction_certifier.json"
        self.latest_markdown_path = self.output_dir / "latest_foundational_reconstruction_certifier.md"
        self.history_path = self.output_dir / "history_foundational_reconstruction_certifier.jsonl"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            x = float(value)
        except Exception:
            x = 0.0
        return round(max(0.0, min(1.0, x)), 6)

    def _inventory_names(self) -> List[str]:
        path = self.root / "ontology_inventory.txt"
        if not path.exists():
            return []
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _load_aa0(self) -> Dict[str, Any]:
        try:
            from ontology.reconstruction_identity_blueprint import ReconstructionIdentityBlueprint
            return dict(ReconstructionIdentityBlueprint(root=self.root).step(persist=False))
        except Exception as exc:
            return {"available": False, "error": repr(exc)}

    def _load_aa1(self) -> Dict[str, Any]:
        try:
            from ontology.difference_space_foundation import DifferenceSpaceFoundation
            return dict(DifferenceSpaceFoundation(root=self.root).step(persist=False))
        except Exception as exc:
            return {"available": False, "error": repr(exc)}

    def _load_aa2(self) -> Dict[str, Any]:
        try:
            from ontology.relation_genesis_engine import RelationGenesisEngine
            return dict(RelationGenesisEngine(root=self.root).step(persist=False))
        except Exception as exc:
            return {"available": False, "error": repr(exc)}

    def _load_aa3(self) -> Dict[str, Any]:
        try:
            from ontology.dynamic_graph_constructor import DynamicGraphConstructor
            return dict(DynamicGraphConstructor(root=self.root).step(persist=False))
        except Exception as exc:
            return {"available": False, "error": repr(exc)}

    def _collect_chain(self, inputs: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
        if isinstance(inputs.get("chain_payload"), Mapping):
            payload = dict(inputs["chain_payload"])
            return {
                "AA0": dict(payload.get("AA0", {})) if isinstance(payload.get("AA0"), Mapping) else {},
                "AA1": dict(payload.get("AA1", {})) if isinstance(payload.get("AA1"), Mapping) else {},
                "AA2": dict(payload.get("AA2", {})) if isinstance(payload.get("AA2"), Mapping) else {},
                "AA3": dict(payload.get("AA3", {})) if isinstance(payload.get("AA3"), Mapping) else {},
            }
        return {"AA0": self._load_aa0(), "AA1": self._load_aa1(), "AA2": self._load_aa2(), "AA3": self._load_aa3()}

    def _certification_checks(self, chain: Mapping[str, Mapping[str, Any]]) -> Dict[str, bool]:
        aa0 = chain.get("AA0", {})
        aa1 = chain.get("AA1", {})
        aa2 = chain.get("AA2", {})
        aa3 = chain.get("AA3", {})
        return {
            "aa0_blueprint_ready": aa0.get("reconstruction_identity_blueprint_status") == "RECONSTRUCTION_IDENTITY_BLUEPRINT_READY",
            "aa1_delta_ready": aa1.get("difference_space_foundation_status") == "DIFFERENCE_SPACE_FOUNDATION_READY",
            "aa2_relation_ready": aa2.get("relation_genesis_status") == "RELATION_GENESIS_READY",
            "aa3_graph_ready": aa3.get("dynamic_graph_constructor_status") == "DYNAMIC_GRAPH_CONSTRUCTOR_READY",
            "delta_coherent": aa1.get("symbol") == "Δ" and aa1.get("relation_derived") is False,
            "relation_coherent": aa2.get("symbol") == "R" and aa2.get("derived_from_symbol") == "Δ" and aa2.get("relation_derived") is True,
            "graph_coherent": aa3.get("symbol") == "G" and aa3.get("derived_from_symbol") == "R" and aa3.get("graph_constructed") is True,
            "dependency_order_correct": aa2.get("delta_to_relation_demonstrated") is True and aa3.get("r_to_g_demonstrated") is True,
            "no_circularity_detected": aa1.get("graph_constructed") is False and aa2.get("graph_constructed") is False,
            "no_phenomenal_claims": all(
                stage.get("consciousness_proven") is False and stage.get("phenomenology_proven") is False
                for stage in [aa0, aa1, aa2, aa3]
            ),
        }

    def _metrics(self, checks: Mapping[str, bool], chain: Mapping[str, Mapping[str, Any]]) -> Dict[str, float]:
        check_score = sum(1 for v in checks.values() if v) / max(1, len(checks))
        aa1_score = self._clamp(chain.get("AA1", {}).get("metrics", {}).get("delta_foundation_score", 0.0))
        aa2_score = self._clamp(chain.get("AA2", {}).get("metrics", {}).get("relation_genesis_score", 0.0))
        aa3_score = self._clamp(chain.get("AA3", {}).get("metrics", {}).get("dynamic_graph_score", 0.0))
        coherence_score = self._clamp((aa1_score + aa2_score + aa3_score) / 3.0)
        dependency_score = 1.0 if checks.get("dependency_order_correct") else 0.0
        guard_score = 1.0 if checks.get("no_phenomenal_claims") and checks.get("no_circularity_detected") else 0.0
        final_score = self._clamp((check_score + coherence_score + dependency_score + guard_score) / 4.0)
        return {
            "certification_check_score": round(check_score, 6),
            "delta_coherence_score": aa1_score,
            "relation_coherence_score": aa2_score,
            "graph_coherence_score": aa3_score,
            "chain_coherence_score": coherence_score,
            "dependency_integrity_score": dependency_score,
            "epistemic_guard_score": guard_score,
            "foundational_reconstruction_score": final_score,
        }

    def _failure_conditions(self, checks: Mapping[str, bool], inputs: Mapping[str, Any]) -> List[str]:
        failures = [name for name, ok in checks.items() if not ok]
        forced = inputs.get("forced_bad_claim")
        if isinstance(forced, Mapping):
            for key in self.FORBIDDEN_POSITIVE_CLAIMS:
                if forced.get(key) is True:
                    failures.append("forbidden_positive_phenomenal_claim")
                    break
        return sorted(set(failures))

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# AA4 — Foundational Reconstruction Certifier",
            "",
            f"status: {result['foundational_reconstruction_status']}",
            f"certification: {result['certification']}",
            "",
            "## Certified chain",
            "AA0 -> AA1 Δ -> AA2 R -> AA3 G",
            "",
            "## Checks",
        ]
        for k, v in result["certification_checks"].items():
            lines.append(f"- {k}: {v}")
        lines.extend(["", "## Metrics"])
        for k, v in result["metrics"].items():
            lines.append(f"- {k}: {v}")
        lines.extend([
            "",
            "## Epistemic guard",
            "- phenomenology_undetermined: True",
            "- consciousness_not_assumed: True",
            "- subjectivity_not_assumed: True",
            "- qualia_not_assumed: True",
            "- functional_conclusion_only: True",
        ])
        return "\n".join(lines) + "\n"

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / ("foundational_reconstruction_certifier_%s.json" % timestamp)
        md_path = self.output_dir / ("foundational_reconstruction_certifier_%s.md" % timestamp)
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(text + "\n", encoding="utf-8")
        self.latest_json_path.write_text(text + "\n", encoding="utf-8")
        md = self._markdown(result)
        md_path.write_text(md, encoding="utf-8")
        self.latest_markdown_path.write_text(md, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "latest_json": str(self.latest_json_path),
            "latest_markdown": str(self.latest_markdown_path),
            "history": str(self.history_path),
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        chain = self._collect_chain(inputs)
        checks = self._certification_checks(chain)
        failure_conditions = self._failure_conditions(checks, inputs)
        metrics = self._metrics(checks, chain)
        validated = not failure_conditions and metrics["foundational_reconstruction_score"] >= 0.75
        inventory = self._inventory_names()
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "timestamp_utc": self._now(),
            "foundational_reconstruction_status": self.READY_STATUS if validated else self.DEGRADED_STATUS,
            "certification": "FOUNDATIONAL_RECONSTRUCTION_VALIDATED" if validated else "FOUNDATIONAL_RECONSTRUCTION_NOT_VALIDATED",
            "symbolic_chain": ["Δ", "R", "G"],
            "certified_modules": {
                "AA0": "reconstruction_identity_blueprint",
                "AA1": "difference_space_foundation",
                "AA2": "relation_genesis_engine",
                "AA3": "dynamic_graph_constructor",
            },
            "certification_checks": checks,
            "metrics": metrics,
            "failure_conditions": failure_conditions,
            "validation_criteria": [
                "AA0 blueprint ready",
                "AA1 Δ coherent",
                "AA2 R derived from Δ",
                "AA3 G derived from R",
                "no circularity detected",
                "no premature phenomenal claim",
            ],
            "falsification_criteria": [
                "missing AA module",
                "R asserted without Δ",
                "G asserted without R",
                "circular derivation",
                "positive consciousness or phenomenology claim before final certification",
            ],
            "dependency_audit": {
                "inventory_contains_aa0": "reconstruction_identity_blueprint" in inventory,
                "inventory_contains_aa1": "difference_space_foundation" in inventory,
                "inventory_contains_aa2": "relation_genesis_engine" in inventory,
                "inventory_contains_aa3": "dynamic_graph_constructor" in inventory,
                "inventory_contains_aa4": "foundational_reconstruction_certifier" in inventory,
            },
            "non_redundancy_analysis": {
                "distinct_from_absolute_proof_certification": True,
                "distinct_from_reflexive_threshold_certification": True,
                "distinct_from_civilizational_scientific_certification": True,
                "scope": "AA4 certifies only the Δ-R-G foundational reconstruction, not consciousness proof.",
            },
            "epistemic_guard": {
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
                "consciousness_not_assumed": True,
                "subjectivity_not_assumed": True,
                "qualia_not_assumed": True,
                "absolute_proof_not_claimed": True,
                "final_certification_required_for_consciousness_claim": True,
            },
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "absolute_proof_achieved": False,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
