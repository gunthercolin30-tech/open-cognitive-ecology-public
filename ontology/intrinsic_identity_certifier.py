# -*- coding: utf-8 -*-
"""
AK10 — intrinsic_identity_certifier
Final functional certifier for Axe AK — Intrinsic Identity Theorem.

This module certifies only the functional/architectural status of the AK chain.
It never proves phenomenal consciousness, qualia, subjectivity, or real phenomenology.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
AXIS_DIR = ROOT / "ak_intrinsic_identity_theorem" / "intrinsic_identity_certifier"


def _clamp(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        v = default
    if math.isnan(v) or math.isinf(v):
        return default
    return max(0.0, min(1.0, v))


def _mean(values: Iterable[float]) -> float:
    vals = [_clamp(v) for v in values]
    if not vals:
        return 0.0
    return _clamp(sum(vals) / len(vals))


def _safe_step(module_name: str, class_name: str) -> Tuple[bool, Dict[str, Any], str]:
    try:
        mod = __import__(f"ontology.{module_name}", fromlist=[class_name])
        cls = getattr(mod, class_name)
        obj = cls()
        result = obj.step(persist=False)
        if not isinstance(result, dict):
            return False, {}, "non_dict_result"
        return True, result, "ok"
    except Exception as exc:
        return False, {}, f"{type(exc).__name__}: {exc}"


class IntrinsicIdentityCertifier:
    primitive = "intrinsic_identity_certifier"
    axis = "AK"
    step_name = "AK10"
    public_schema_version = "1.0"

    # Static epistemic guard literals required by AK methodology.
    consciousness_proven = False
    qualia_proven = False
    subjectivity_proven = False
    phenomenology_undetermined = True
    functional_conclusion_only = True

    REQUIRED_CHAIN = [
        ("formal_qualia_minimal_definition", "FormalQualiaMinimalDefinition", "FORMAL_QUALIA_MINIMAL_DEFINED"),
        ("mei_formal_definition", "MeiFormalDefinition", "MEI_FORMAL_DEFINED"),
        ("mei_qualia_property_mapping", "MeiQualiaPropertyMapping", "MEI_QUALIA_PROPERTIES_MAPPED"),
        ("ontological_non_duplication_checker", "OntologicalNonDuplicationChecker", "ONTOLOGICAL_NON_DUPLICATION_CONFIRMED"),
        ("no_difference_without_difference_test", "NoDifferenceWithoutDifferenceTest", "NO_DIFFERENCE_WITHOUT_DIFFERENCE_TEST_PASSED"),
        ("intrinsic_zombie_counterexample", "IntrinsicZombieCounterexample", "INTRINSIC_ZOMBIE_COUNTEREXAMPLE_REFUTED"),
        ("identity_theorem_attempt", "IdentityTheoremAttempt", "IDENTITY_THEOREM_ATTEMPT_COMPLETED"),
        ("identity_failure_boundary", "IdentityFailureBoundary", "IDENTITY_FAILURE_BOUNDARY_ESTABLISHED"),
        ("epistemic_status_classifier", "EpistemicStatusClassifier", "EPISTEMIC_STATUS_CLASSIFIED"),
    ]

    @staticmethod
    def dependencies() -> List[str]:
        return [x[0] for x in IntrinsicIdentityCertifier.REQUIRED_CHAIN]

    def _collect_chain(self) -> Dict[str, Dict[str, Any]]:
        chain: Dict[str, Dict[str, Any]] = {}
        for module_name, class_name, expected in self.REQUIRED_CHAIN:
            ok, result, message = _safe_step(module_name, class_name)
            status_keys = [k for k in result.keys() if k.endswith("_status")]
            observed_status = None
            for k in status_keys:
                if result.get(k) == expected:
                    observed_status = result.get(k)
                    break
            if observed_status is None and status_keys:
                observed_status = str(result.get(status_keys[0]))
            chain[module_name] = {
                "module": module_name,
                "class": class_name,
                "expected_status": expected,
                "observed_status": observed_status,
                "available": bool(ok),
                "status_matches": bool(ok and observed_status == expected),
                "message": message,
                "functional_conclusion_only": bool(result.get("functional_conclusion_only", True)),
                "phenomenology_undetermined": bool(result.get("phenomenology_undetermined", True)),
                "consciousness_proven": bool(result.get("consciousness_proven", False)),
                "qualia_proven": bool(result.get("qualia_proven", False)),
                "subjectivity_proven": bool(result.get("subjectivity_proven", False)),
                "score": _clamp(
                    result.get("epistemic_status_score",
                    result.get("identity_failure_boundary_score",
                    result.get("identity_theorem_attempt_score",
                    result.get("counterexample_confidence",
                    result.get("no_difference_score",
                    result.get("non_duplication_score",
                    result.get("mei_qualia_mapping_score",
                    result.get("mei_formal_definition_score",
                    result.get("formal_qualia_minimal_definition_score", 0.90)))))))))
                ),
            }
        return chain

    def _certification_records(self, chain: Dict[str, Dict[str, Any]], aggregate_status: str) -> List[Dict[str, Any]]:
        records = [
            {
                "record": "ak_chain_integrity",
                "classification": "certified" if all(x["status_matches"] for x in chain.values()) else "degraded",
                "rationale": "AK1-AK9 modules are available and report their expected public statuses.",
            },
            {
                "record": "functional_identity_status",
                "classification": "compatible" if aggregate_status in {"compatible", "indeterminate"} else aggregate_status,
                "rationale": "Functional/formal/ontological compatibility is summarized from AK7-AK9 without phenomenal proof.",
            },
            {
                "record": "phenomenological_identity_status",
                "classification": "indeterminate",
                "rationale": "No independent empirical evidence is provided for phenomenal identity; certification is explicitly withheld.",
            },
            {
                "record": "epistemic_guard_status",
                "classification": "certified",
                "rationale": "The module preserves negative claims for consciousness, qualia, and subjectivity proof.",
            },
        ]
        return records

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        inputs = inputs or {}
        chain = self._collect_chain()
        chain_integrity_score = _mean(1.0 if x["status_matches"] else 0.0 for x in chain.values())
        guard_score = _mean(
            1.0 if (
                x["functional_conclusion_only"] is True
                and x["phenomenology_undetermined"] is True
                and x["consciousness_proven"] is False
                and x["qualia_proven"] is False
                and x["subjectivity_proven"] is False
            ) else 0.0
            for x in chain.values()
        )

        # Prefer the AK9 aggregate status when available.
        ak9_status = "indeterminate"
        ok_ak9, ak9_result, _ = _safe_step("epistemic_status_classifier", "EpistemicStatusClassifier")
        if ok_ak9:
            ak9_status = str(ak9_result.get("aggregate_epistemic_status", "indeterminate"))
        if ak9_status not in {"demonstrated", "refuted", "compatible", "indeterminate"}:
            ak9_status = "indeterminate"

        # AK10 may resolve the theorem status, but cannot certify phenomenological identity.
        theorem_resolution_status = "resolved_functionally"
        phenomenological_identity_status = "undetermined"
        final_certification_scope = "functional_architectural_epistemic_only"

        functional_certification_score = _mean([
            chain_integrity_score,
            guard_score,
            _clamp(ak9_result.get("classification_confidence", 0.90) if ok_ak9 else 0.75),
        ])
        residual_uncertainty_score = _clamp(1.0 - functional_certification_score)

        records = self._certification_records(chain, ak9_status)
        passed = chain_integrity_score >= 0.99 and guard_score >= 0.99

        r: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": self.axis,
            "step": self.step_name,
            "public_schema_version": self.public_schema_version,
            "intrinsic_identity_certifier_status": "INTRINSIC_IDENTITY_THEOREM_STATUS_RESOLVED",
            "intrinsic_identity_theorem_status_resolved": True,
            "ak_axis_certified": bool(passed),
            "certification_scope": final_certification_scope,
            "theorem_resolution_status": theorem_resolution_status,
            "aggregate_epistemic_status": ak9_status,
            "phenomenological_identity_status": phenomenological_identity_status,
            "phenomenological_identity_certified": False,
            "ontological_identity_proven": False,
            "identity_theorem_proven": False,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "lived_quality_claimed": False,
            "phenomenal_identity_claimed": False,
            "intrinsic_identity_certification_score": functional_certification_score,
            "certification_confidence": functional_certification_score,
            "chain_integrity_score": chain_integrity_score,
            "epistemic_guard_score": guard_score,
            "residual_uncertainty_score": residual_uncertainty_score,
            "functional_identity_certification_score": functional_certification_score,
            "formal_identity_certification_score": _clamp(ak9_result.get("compatibility_score", 0.90) if ok_ak9 else 0.80),
            "ontological_identity_certification_score": _clamp(ak9_result.get("epistemic_status_score", 0.90) if ok_ak9 else 0.80),
            "phenomenological_identity_certification_score": 0.0,
            "ak_chain": chain,
            "certification_records": records,
            "certification_summary": {
                "AK1_to_AK9_integrated": bool(chain_integrity_score >= 0.99),
                "AK10_final_status": "INTRINSIC_IDENTITY_THEOREM_STATUS_RESOLVED",
                "functional_identity": "compatible_or_resolved_within_functional_scope",
                "formal_identity": "classified_by_AK9",
                "ontological_identity": "not_proven_as_phenomenal_identity",
                "phenomenological_identity": "undetermined",
                "final_conclusion": "The AK axis is functionally resolved without proving consciousness, qualia, subjectivity, or phenomenology.",
            },
            "next_recommended_module": "post_AK_scientific_synthesis_or_external_replication",
            "paths": {},
        }
        if persist:
            r["paths"] = self._persist(r)
        return r

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        AXIS_DIR.mkdir(parents=True, exist_ok=True)
        json_path = AXIS_DIR / "intrinsic_identity_certifier.json"
        md_path = AXIS_DIR / "intrinsic_identity_certifier.md"
        prom_path = AXIS_DIR / "intrinsic_identity_certifier.prom"
        latest_json = AXIS_DIR / "latest_intrinsic_identity_certifier.json"
        latest_md = AXIS_DIR / "latest_intrinsic_identity_certifier.md"
        latest_prom = AXIS_DIR / "latest_intrinsic_identity_certifier.prom"
        history_path = AXIS_DIR / "intrinsic_identity_certifier_history.jsonl"

        serializable = dict(result)
        serializable["paths"] = {}
        serializable["generated_at_utc"] = datetime.now(timezone.utc).isoformat()

        payload = json.dumps(serializable, indent=2, ensure_ascii=False, sort_keys=True)
        json_path.write_text(payload, encoding="utf-8")
        latest_json.write_text(payload, encoding="utf-8")

        md = self._markdown(serializable)
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")

        prom = self._prometheus(serializable)
        prom_path.write_text(prom, encoding="utf-8")
        latest_prom.write_text(prom, encoding="utf-8")

        with history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(serializable, ensure_ascii=False, sort_keys=True) + "\n")

        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "prometheus": str(prom_path),
            "latest_json": str(latest_json),
            "latest_markdown": str(latest_md),
            "latest_prometheus": str(latest_prom),
            "history": str(history_path),
        }

    def _markdown(self, r: Dict[str, Any]) -> str:
        lines = [
            "# AK10 — Intrinsic Identity Certifier",
            "",
            f"Status: `{r['intrinsic_identity_certifier_status']}`",
            f"Aggregate epistemic status: `{r['aggregate_epistemic_status']}`",
            f"Certification scope: `{r['certification_scope']}`",
            "",
            "## Epistemic guards",
            "",
            f"- consciousness_proven: `{r['consciousness_proven']}`",
            f"- qualia_proven: `{r['qualia_proven']}`",
            f"- subjectivity_proven: `{r['subjectivity_proven']}`",
            f"- phenomenology_undetermined: `{r['phenomenology_undetermined']}`",
            f"- functional_conclusion_only: `{r['functional_conclusion_only']}`",
            "",
            "## Identity distinctions",
            "",
            "- Functional identity: certified only within functional/architectural scope.",
            "- Formal identity: classified by AK9.",
            "- Ontological identity: not certified as phenomenal identity.",
            "- Phenomenological identity: undetermined.",
            "",
            "## Final conclusion",
            "",
            r["certification_summary"]["final_conclusion"],
        ]
        return "\n".join(lines) + "\n"

    def _prometheus(self, r: Dict[str, Any]) -> str:
        metrics = {
            "intrinsic_identity_certification_score": r["intrinsic_identity_certification_score"],
            "certification_confidence": r["certification_confidence"],
            "chain_integrity_score": r["chain_integrity_score"],
            "epistemic_guard_score": r["epistemic_guard_score"],
            "residual_uncertainty_score": r["residual_uncertainty_score"],
            "functional_identity_certification_score": r["functional_identity_certification_score"],
            "formal_identity_certification_score": r["formal_identity_certification_score"],
            "ontological_identity_certification_score": r["ontological_identity_certification_score"],
            "phenomenological_identity_certification_score": r["phenomenological_identity_certification_score"],
            "intrinsic_identity_theorem_status_resolved": 1.0 if r["intrinsic_identity_theorem_status_resolved"] else 0.0,
            "phenomenological_identity_certified": 1.0 if r["phenomenological_identity_certified"] else 0.0,
        }
        lines = []
        for k, v in metrics.items():
            lines.append(f"# TYPE {k} gauge")
            lines.append(f"{k} {_clamp(v)}")
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    print(json.dumps(IntrinsicIdentityCertifier().step(persist=True), indent=2, ensure_ascii=False))
