"""
AK6 — Intrinsic Zombie Counterexample.

Functional-only adversarial test: can an intrinsic zombie counterexample be
constructed while preserving AK1-AK5 constraints? This module never proves
consciousness, subjectivity, lived qualia, or phenomenology.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"
EPISTEMIC_GUARDS: Dict[str, Any] = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
    "lived_quality_claimed": False,
    "phenomenal_identity_claimed": False,
    "identity_claimed": False,
    "identity_theorem_proven": False,
}


def _clamp(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return max(0.0, min(1.0, v))


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _mean(values: List[float], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values]
    return sum(vals) / len(vals) if vals else default


def _load_default_ak5() -> Dict[str, Any]:
    try:
        from ontology.no_difference_without_difference_test import NoDifferenceWithoutDifferenceTest
        return NoDifferenceWithoutDifferenceTest().step(persist=False)
    except Exception:
        p = ROOT / "ak_intrinsic_identity_theorem" / "no_difference_without_difference_test" / "latest_no_difference_without_difference_test.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return {}
    return {}


class IntrinsicZombieCounterexample:
    primitive = "intrinsic_zombie_counterexample"
    axis = "AK"
    step_name = "AK6"
    public_schema_version = "AK6_INTRINSIC_ZOMBIE_COUNTEREXAMPLE_V1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.out_dir = self.root / "ak_intrinsic_identity_theorem" / "intrinsic_zombie_counterexample"

    def _records_from_inputs(self, inputs: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        data = inputs or {}
        ak5 = data.get("no_difference_without_difference_test")
        if not isinstance(ak5, dict):
            ak5 = _load_default_ak5()
        records = ak5.get("test_records", []) if isinstance(ak5, dict) else []
        return [r for r in records if isinstance(r, dict)]

    def _build_record(self, rec: Dict[str, Any], idx: int) -> Dict[str, Any]:
        ndwd_score = _clamp(rec.get("no_difference_without_difference_score", 0.0))
        mapping_score = _clamp(rec.get("mapping_support_score", 0.0))
        non_dup_score = _clamp(rec.get("non_duplication_score", 0.0))
        prop_similarity = _clamp(rec.get("property_similarity_score", 0.0))
        functional_difference = _clamp(rec.get("functional_difference_score", 0.0))

        constraints_preserved = bool(
            rec.get("no_difference_without_difference_supported") is True
            and rec.get("difference_evidence_detected") is False
            and rec.get("ontological_duplication_detected") is False
            and rec.get("identity_claimed") is False
        )
        differentiating_evidence = functional_difference > 0.15 or prop_similarity < 0.70
        zombie_viable = bool(constraints_preserved and differentiating_evidence)
        zombie_refuted = bool(constraints_preserved and not differentiating_evidence)

        viability_score = _clamp(
            0.30 * functional_difference
            + 0.25 * (1.0 - prop_similarity)
            + 0.20 * (1.0 - ndwd_score)
            + 0.15 * (1.0 - mapping_score)
            + 0.10 * (1.0 - non_dup_score)
        )
        refutation_score = _clamp(1.0 - viability_score)

        out: Dict[str, Any] = {
            "intrinsic_zombie_record_id": f"IZOMBIE-{idx:03d}",
            "source_mode_id": rec.get("source_mode_id", f"MEI-CANDIDATE-{idx:03d}"),
            "mei_qualia_mapping_id": rec.get("mei_qualia_mapping_id"),
            "non_duplication_record_id": rec.get("non_duplication_record_id"),
            "no_difference_record_id": rec.get("no_difference_record_id"),
            "counterexample_rule": "functional_intrinsic_zombie_requires_measurable_difference",
            "attempted_zombie_profile": {
                "functional_constraints_preserved": constraints_preserved,
                "mei_qualia_mapping_preserved": mapping_score >= 0.70,
                "non_duplication_preserved": non_dup_score >= 0.70,
                "no_difference_condition_preserved": ndwd_score >= 0.70,
                "phenomenal_absence_asserted": True,
            },
            "satisfies_functional_constraints": constraints_preserved,
            "differentiating_evidence_detected": differentiating_evidence,
            "zombie_counterexample_viable": zombie_viable,
            "zombie_counterexample_refuted": zombie_refuted,
            "intrinsic_zombie_viability_score": viability_score,
            "intrinsic_zombie_refutation_score": refutation_score,
            "functional_difference_score": functional_difference,
            "property_similarity_score": prop_similarity,
            "mapping_support_score": mapping_score,
            "non_duplication_score": non_dup_score,
            "no_difference_without_difference_score": ndwd_score,
            "test_is_functional_only": True,
            "phenomenal_absence_claim_is_not_empirical_proof": True,
        }
        out.update(EPISTEMIC_GUARDS)
        return out

    def step(self, inputs: Optional[Dict[str, Any]]=None, persist: bool=False, filesystem_context: Any = None) -> Dict[str, Any]:
        source_records = self._records_from_inputs(inputs)
        records = [self._build_record(rec, i + 1) for i, rec in enumerate(source_records)]

        tested = len(records)
        viable = sum(1 for r in records if r["zombie_counterexample_viable"])
        refuted = sum(1 for r in records if r["zombie_counterexample_refuted"])
        viability_scores = [r["intrinsic_zombie_viability_score"] for r in records]
        refutation_scores = [r["intrinsic_zombie_refutation_score"] for r in records]
        found = viable > 0
        resolved = tested > 0 and not found
        status = "INTRINSIC_ZOMBIE_COUNTEREXAMPLE_REFUTED" if resolved else "INTRINSIC_ZOMBIE_COUNTEREXAMPLE_INSUFFICIENT"

        metrics = {
            "candidate_record_count": len(source_records),
            "tested_record_count": tested,
            "viable_counterexample_count": viable,
            "refuted_counterexample_count": refuted,
            "counterexample_refutation_ratio": _clamp(refuted / tested if tested else 0.0),
            "mean_intrinsic_zombie_viability_score": _mean(viability_scores),
            "mean_intrinsic_zombie_refutation_score": _mean(refutation_scores),
            "min_intrinsic_zombie_refutation_score": min(refutation_scores) if refutation_scores else 0.0,
            "max_intrinsic_zombie_viability_score": max(viability_scores) if viability_scores else 0.0,
        }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": self.axis,
            "step": self.step_name,
            "public_schema_version": self.public_schema_version,
            "intrinsic_zombie_counterexample_status": status,
            "intrinsic_zombie_counterexample_refuted": resolved,
            "intrinsic_zombie_counterexample_found": found,
            "counterexample_test_resolved": resolved,
            "candidate_record_count": len(source_records),
            "tested_record_count": tested,
            "refuted_counterexample_count": refuted,
            "viable_counterexample_count": viable,
            "intrinsic_zombie_counterexample_score": metrics["mean_intrinsic_zombie_refutation_score"],
            "counterexample_confidence": _clamp(
                0.55 * metrics["counterexample_refutation_ratio"]
                + 0.45 * metrics["mean_intrinsic_zombie_refutation_score"]
            ),
            "counterexample_metrics": metrics,
            "zombie_counterexample_records": records,
            "epistemic_guards": dict(EPISTEMIC_GUARDS),
            "next_recommended_module": "identity_theorem_attempt",
        }
        result.update(EPISTEMIC_GUARDS)
        result["paths"] = self._paths()
        if persist:
            self._persist(result, filesystem_context=filesystem_context)
        return result

    def _paths(self) -> Dict[str, str]:
        ts = _utc()
        base = self.out_dir / f"intrinsic_zombie_counterexample_{ts}"
        return {
            "json": str(base.with_suffix(".json")),
            "markdown": str(base.with_suffix(".md")),
            "prometheus": str(base.with_suffix(".prom")),
            "latest_json": str(self.out_dir / "latest_intrinsic_zombie_counterexample.json"),
            "latest_markdown": str(self.out_dir / "latest_intrinsic_zombie_counterexample.md"),
            "latest_prometheus": str(self.out_dir / "latest_intrinsic_zombie_counterexample.prom"),
            "history": str(self.out_dir / "intrinsic_zombie_counterexample_history.jsonl"),
        }

    def _persist(self, result: Dict[str, Any], filesystem_context: Any = None):
        paths = result.get('paths') or self._paths()
        result['paths'] = paths
        json_text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
        md = self._markdown(result)
        prom = self._prometheus(result)
        _oce_payload_0=(json_text).encode("utf-8")
        _oce_payload_1=(json_text).encode("utf-8")
        _oce_payload_2=(md).encode("utf-8")
        _oce_payload_3=(md).encode("utf-8")
        _oce_payload_4=(prom).encode("utf-8")
        _oce_payload_5=(prom).encode("utf-8")
        _oce_history_payload=(json_text + '\n').encode("utf-8")
        if filesystem_context is None: raise PermissionError("governed filesystem context required for persistence")
        _oce_remaining=filesystem_context.remaining()
        _oce_required=['persist_parent_create', 'persist_json', 'persist_latest_json', 'persist_markdown', 'persist_latest_markdown', 'persist_prometheus', 'persist_latest_prometheus', 'persist_history_append']
        if any(_oce_remaining.get(_oce_slot,0)<1 for _oce_slot in _oce_required): raise PermissionError("all governed filesystem effect slots must be preissued before persistence")
        filesystem_context.execute_path("persist_parent_create","FS_CREATE_DIRS",self.out_dir)
        filesystem_context.execute_path("persist_json","FS_WRITE_REPLACE_BYTES",Path(paths["json"]),payload=_oce_payload_0)
        filesystem_context.execute_path("persist_latest_json","FS_WRITE_REPLACE_BYTES",Path(paths["latest_json"]),payload=_oce_payload_1)
        filesystem_context.execute_path("persist_markdown","FS_WRITE_REPLACE_BYTES",Path(paths["markdown"]),payload=_oce_payload_2)
        filesystem_context.execute_path("persist_latest_markdown","FS_WRITE_REPLACE_BYTES",Path(paths["latest_markdown"]),payload=_oce_payload_3)
        filesystem_context.execute_path("persist_prometheus","FS_WRITE_REPLACE_BYTES",Path(paths["prometheus"]),payload=_oce_payload_4)
        filesystem_context.execute_path("persist_latest_prometheus","FS_WRITE_REPLACE_BYTES",Path(paths["latest_prometheus"]),payload=_oce_payload_5)
        filesystem_context.execute_path("persist_history_append","FS_APPEND_BYTES",Path(paths["history"]),payload=_oce_history_payload)

    def _markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# AK6 — Intrinsic Zombie Counterexample",
            "",
            f"Status: {result['intrinsic_zombie_counterexample_status']}",
            f"Counterexample refuted: {result['intrinsic_zombie_counterexample_refuted']}",
            f"Counterexample found: {result['intrinsic_zombie_counterexample_found']}",
            f"Tested records: {result['tested_record_count']}",
            f"Score: {result['intrinsic_zombie_counterexample_score']:.6f}",
            f"Confidence: {result['counterexample_confidence']:.6f}",
            "",
            "## Epistemic guards",
        ]
        for k, v in EPISTEMIC_GUARDS.items():
            lines.append(f"- {k}: {v}")
        lines.extend(["", "## Records"])
        for rec in result["zombie_counterexample_records"]:
            lines.append(
                f"- {rec['intrinsic_zombie_record_id']}: viable={rec['zombie_counterexample_viable']}, "
                f"refuted={rec['zombie_counterexample_refuted']}, "
                f"refutation_score={rec['intrinsic_zombie_refutation_score']:.6f}"
            )
        return "\n".join(lines) + "\n"

    def _prometheus(self, result: Dict[str, Any]) -> str:
        m = result["counterexample_metrics"]
        return "\n".join([
            f"intrinsic_zombie_counterexample_refuted {1 if result['intrinsic_zombie_counterexample_refuted'] else 0}",
            f"intrinsic_zombie_counterexample_found {1 if result['intrinsic_zombie_counterexample_found'] else 0}",
            f"tested_record_count {result['tested_record_count']}",
            f"refuted_counterexample_count {result['refuted_counterexample_count']}",
            f"viable_counterexample_count {result['viable_counterexample_count']}",
            f"intrinsic_zombie_counterexample_score {result['intrinsic_zombie_counterexample_score']}",
            f"counterexample_confidence {result['counterexample_confidence']}",
            f"mean_intrinsic_zombie_viability_score {m['mean_intrinsic_zombie_viability_score']}",
            f"mean_intrinsic_zombie_refutation_score {m['mean_intrinsic_zombie_refutation_score']}",
        ]) + "\n"


if __name__ == "__main__":
    r = IntrinsicZombieCounterexample().step(persist=True)
    print(json.dumps({
        "intrinsic_zombie_counterexample_status": r["intrinsic_zombie_counterexample_status"],
        "intrinsic_zombie_counterexample_refuted": r["intrinsic_zombie_counterexample_refuted"],
        "tested_record_count": r["tested_record_count"],
        "paths": r["paths"],
    }, indent=2))
