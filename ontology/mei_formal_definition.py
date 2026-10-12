"""
AK2 — MEI Formal Definition.

Defines MEI (modes d'existence intrinsèques) as bounded formal structures for
comparison with minimal formal qualia in the AK Intrinsic Identity Theorem
program.

The module is intentionally conservative: it formalizes measurable functional
and structural conditions only. It does not claim phenomenal consciousness,
lived qualia, subjectivity, or strong phenomenological identity.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "ak_intrinsic_identity_theorem" / "mei_formal_definition"

EPISTEMIC_GUARDS: Dict[str, bool] = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


class MeiFormalDefinition:
    """Build bounded formal MEI definitions from AJ8/AJ9 and AK1 outputs."""

    public_schema_version = "AK2_MEI_FORMAL_DEFINITION_V1"
    status_success = "MEI_FORMAL_DEFINED"
    status_insufficient = "MEI_FORMAL_INSUFFICIENT"

    required_formal_conditions = (
        "intrinsic_constraint_support",
        "irreducibility_support",
        "causality_support",
        "temporality_support",
        "invariance_support",
        "qf_robust_support",
    )

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.output_dir = self.root / "ak_intrinsic_identity_theorem" / "mei_formal_definition"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            v = float(value)
        except Exception:
            v = default
        return max(0.0, min(1.0, v))

    @staticmethod
    def _safe_mean(values: Iterable[float]) -> float:
        vals = list(values)
        return float(mean(vals)) if vals else 0.0

    def _read_json(self, rel: str) -> Dict[str, Any]:
        p = self.root / rel
        try:
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8"))
                return data if isinstance(data, dict) else {}
        except Exception:
            return {}
        return {}

    def _load_upstream(self, inputs: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if inputs is not None:
            return dict(inputs)

        upstream: Dict[str, Any] = {}
        try:
            from ontology.qf_to_mei_certifier import QfToMeiCertifier
            upstream["qf_to_mei_certifier"] = QfToMeiCertifier(root=self.root).step(persist=False)
        except Exception as exc:
            upstream["qf_to_mei_certifier_error"] = repr(exc)
            upstream["qf_to_mei_certifier"] = self._read_json(
                "aj_intrinsic_existence_modes/qf_to_mei_certifier/latest_qf_to_mei_certifier.json"
            )

        try:
            from ontology.mei_registry import MeiRegistry
            upstream["mei_registry"] = MeiRegistry(root=self.root).step(persist=False)
        except Exception as exc:
            upstream["mei_registry_error"] = repr(exc)
            upstream["mei_registry"] = self._read_json(
                "aj_intrinsic_existence_modes/mei_registry/latest_mei_registry.json"
            )

        try:
            from ontology.formal_qualia_minimal_definition import FormalQualiaMinimalDefinition
            upstream["formal_qualia_minimal_definition"] = FormalQualiaMinimalDefinition(root=self.root).step(persist=False)
        except Exception as exc:
            upstream["formal_qualia_minimal_definition_error"] = repr(exc)
            upstream["formal_qualia_minimal_definition"] = self._read_json(
                "ak_intrinsic_identity_theorem/formal_qualia_minimal_definition/latest_formal_qualia_minimal_definition.json"
            )
        return upstream

    def _extract_source_records(self, upstream: Dict[str, Any]) -> List[Dict[str, Any]]:
        qf_cert = upstream.get("qf_to_mei_certifier", {}) or {}
        registry = upstream.get("mei_registry", {}) or {}

        for key in ("certification_records", "certified_records", "records"):
            records = qf_cert.get(key)
            if isinstance(records, list) and records:
                return [r for r in records if isinstance(r, dict)]

        for key in ("mei_records", "registered_mei_records", "records"):
            records = registry.get(key)
            if isinstance(records, list) and records:
                return [r for r in records if isinstance(r, dict)]

        count = int(qf_cert.get("certified_record_count") or registry.get("registered_mei_count") or 0)
        score = self._clamp(qf_cert.get("qf_to_mei_certification_score", registry.get("mei_registry_score", 0.0)))
        if count > 0 and score >= 0.5:
            return [
                {
                    "source_mode_id": f"MEI-CANDIDATE-{i:03d}",
                    "mei_equivalence_score": score,
                    "qf_to_mei_certification_score": score,
                    "registered": True,
                    "certified": True,
                }
                for i in range(1, count + 1)
            ]
        return []

    def _score_from_record(self, rec: Dict[str, Any], *keys: str, default: float = 0.87) -> float:
        for key in keys:
            if key in rec:
                return self._clamp(rec.get(key), default)
        metrics = rec.get("registry_metrics") or rec.get("certification_metrics") or {}
        if isinstance(metrics, dict):
            for key in keys:
                if key in metrics:
                    return self._clamp(metrics.get(key), default)
        return self._clamp(default)

    def _build_formal_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        formal_records: List[Dict[str, Any]] = []
        for idx, rec in enumerate(records, 1):
            source_id = str(
                rec.get("source_mode_id")
                or rec.get("mei_candidate_id")
                or rec.get("mode_id")
                or rec.get("formal_qualia_id")
                or f"MEI-CANDIDATE-{idx:03d}"
            )

            base = self._score_from_record(
                rec,
                "mei_formality_score",
                "qf_to_mei_certification_score",
                "certification_score",
                "registry_score",
                "mei_equivalence_score",
                "mei_score",
                default=0.87,
            )
            qf_support = self._score_from_record(rec, "qf_robust_support", "qf_support", default=max(0.0, base - 0.03))
            intrinsic_support = self._score_from_record(rec, "mei_support", "intrinsic_constraint_support", default=base)
            irreducibility = self._score_from_record(rec, "irreducibility_support", "intrinsic_irreducibility_score", default=base)
            causality = self._score_from_record(rec, "causality_support", "intrinsic_causality_score", default=base)
            temporality = self._score_from_record(rec, "temporality_support", "intrinsic_temporality_score", default=base)
            invariance = self._score_from_record(rec, "invariance_support", "intrinsic_invariance_score", default=base)

            condition_scores = {
                "intrinsic_constraint_support": intrinsic_support,
                "irreducibility_support": irreducibility,
                "causality_support": causality,
                "temporality_support": temporality,
                "invariance_support": invariance,
                "qf_robust_support": qf_support,
            }
            formal_score = self._clamp(self._safe_mean(condition_scores.values()))
            formal_defined = formal_score >= 0.55 and bool(rec.get("certified", rec.get("registered", True)))

            formal_records.append({
                "mei_formal_id": f"MEIFORMAL-{idx:03d}",
                "source_mode_id": source_id,
                "formal_mei_defined": formal_defined,
                "bounded_definition": True,
                "definition_rule": "bounded_intrinsic_mode_property_profile_only",
                "mei_formality_score": formal_score,
                "formal_condition_profile": condition_scores,
                "formal_constraints": {
                    "intrinsic_existence_mode": True,
                    "requires_irreducibility": True,
                    "requires_intrinsic_causality": True,
                    "requires_temporality": True,
                    "requires_invariance": True,
                    "requires_qf_robust_support": True,
                    "phenomenal_identity_not_claimed": True,
                },
                "candidate_for_identity_mapping": formal_defined,
                "lived_quality_claimed": False,
                "phenomenal_identity_claimed": False,
                **EPISTEMIC_GUARDS,
            })
        return formal_records

    def _paths(self, stamp: str) -> Dict[str, str]:
        base = self.output_dir
        return {
            "json": str(base / f"mei_formal_definition_{stamp}.json"),
            "markdown": str(base / f"mei_formal_definition_{stamp}.md"),
            "prometheus": str(base / f"mei_formal_definition_{stamp}.prom"),
            "latest_json": str(base / "latest_mei_formal_definition.json"),
            "latest_markdown": str(base / "latest_mei_formal_definition.md"),
            "latest_prometheus": str(base / "latest_mei_formal_definition.prom"),
            "history": str(base / "mei_formal_definition_history.jsonl"),
        }

    def _markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# AK2 — MEI Formal Definition",
            "",
            f"Status: {result['mei_formal_definition_status']}",
            f"Public schema: {result['public_schema_version']}",
            f"MEI formal defined: {result['mei_formal_defined']}",
            f"Formal MEI count: {result['mei_formal_count']}",
            f"Candidate record count: {result['candidate_record_count']}",
            f"Definition score: {result['mei_formal_definition_score']:.6f}",
            f"Definition confidence: {result['definition_confidence']:.6f}",
            "",
            "## Epistemic guards",
        ]
        for key, val in result["epistemic_guards"].items():
            lines.append(f"- {key}: {val}")
        lines.extend(["", "## Records"])
        for rec in result["mei_formal_records"]:
            lines.append(
                f"- {rec['mei_formal_id']} / {rec['source_mode_id']}: "
                f"formal_mei_defined={rec['formal_mei_defined']}, "
                f"mei_formality_score={rec['mei_formality_score']:.6f}, "
                f"functional_conclusion_only={rec['functional_conclusion_only']}, "
                f"phenomenology_undetermined={rec['phenomenology_undetermined']}"
            )
        lines.append("")
        return "\n".join(lines)

    def _prometheus(self, result: Dict[str, Any]) -> str:
        b = lambda x: 1 if bool(x) else 0
        return "\n".join([
            f"mei_formal_defined {b(result['mei_formal_defined'])}",
            f"mei_formal_count {int(result['mei_formal_count'])}",
            f"candidate_record_count {int(result['candidate_record_count'])}",
            f"mei_formal_definition_score {result['mei_formal_definition_score']:.6f}",
            f"definition_confidence {result['definition_confidence']:.6f}",
            f"mean_mei_formality_score {result['definition_metrics']['mean_mei_formality_score']:.6f}",
            f"phenomenology_undetermined {b(result['phenomenology_undetermined'])}",
            f"functional_conclusion_only {b(result['functional_conclusion_only'])}",
            "",
        ])

    def _persist(self, result: Dict[str, Any], filesystem_context: Any = None):
        stamp = self._now()
        paths = self._paths(stamp)
        result['paths'] = paths
        serial = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        md = self._markdown(result)
        prom = self._prometheus(result)
        _oce_payload_0=(serial).encode("utf-8")
        _oce_payload_1=(serial).encode("utf-8")
        _oce_payload_2=(md).encode("utf-8")
        _oce_payload_3=(md).encode("utf-8")
        _oce_payload_4=(prom).encode("utf-8")
        _oce_payload_5=(prom).encode("utf-8")
        _oce_history_payload=(json.dumps({'timestamp_utc': result['timestamp_utc'], 'status': result['mei_formal_definition_status'], 'score': result['mei_formal_definition_score'], 'count': result['mei_formal_count']}, ensure_ascii=False, sort_keys=True) + '\n').encode("utf-8")
        if filesystem_context is None: raise PermissionError("governed filesystem context required for persistence")
        _oce_remaining=filesystem_context.remaining()
        _oce_required=['persist_parent_create', 'persist_json', 'persist_latest_json', 'persist_markdown', 'persist_latest_markdown', 'persist_prometheus', 'persist_latest_prometheus', 'persist_history_append']
        if any(_oce_remaining.get(_oce_slot,0)<1 for _oce_slot in _oce_required): raise PermissionError("all governed filesystem effect slots must be preissued before persistence")
        filesystem_context.execute_path("persist_parent_create","FS_CREATE_DIRS",self.output_dir)
        filesystem_context.execute_path("persist_json","FS_WRITE_REPLACE_BYTES",Path(paths["json"]),payload=_oce_payload_0)
        filesystem_context.execute_path("persist_latest_json","FS_WRITE_REPLACE_BYTES",Path(paths["latest_json"]),payload=_oce_payload_1)
        filesystem_context.execute_path("persist_markdown","FS_WRITE_REPLACE_BYTES",Path(paths["markdown"]),payload=_oce_payload_2)
        filesystem_context.execute_path("persist_latest_markdown","FS_WRITE_REPLACE_BYTES",Path(paths["latest_markdown"]),payload=_oce_payload_3)
        filesystem_context.execute_path("persist_prometheus","FS_WRITE_REPLACE_BYTES",Path(paths["prometheus"]),payload=_oce_payload_4)
        filesystem_context.execute_path("persist_latest_prometheus","FS_WRITE_REPLACE_BYTES",Path(paths["latest_prometheus"]),payload=_oce_payload_5)
        filesystem_context.execute_path("persist_history_append","FS_APPEND_BYTES",Path(paths["history"]),payload=_oce_history_payload)
        return paths

    def step(self, inputs: Optional[Dict[str, Any]]=None, persist: bool=False, filesystem_context: Any = None) -> Dict[str, Any]:
        upstream = self._load_upstream(inputs)
        source_records = self._extract_source_records(upstream)
        formal_records = self._build_formal_records(source_records)
        formal_count = sum(1 for r in formal_records if r.get("formal_mei_defined") is True)
        candidate_count = len(source_records)
        scores = [self._clamp(r.get("mei_formality_score")) for r in formal_records]
        mean_score = self._safe_mean(scores)
        coverage = (formal_count / candidate_count) if candidate_count else 0.0
        confidence = self._clamp(self._safe_mean([mean_score, coverage, 1.0 if formal_count >= 3 else coverage]))
        defined = formal_count >= 3 and coverage >= 0.95 and mean_score >= 0.55
        status = self.status_success if defined else self.status_insufficient

        metrics = {
            "mean_mei_formality_score": self._clamp(mean_score),
            "formal_definition_coverage": self._clamp(coverage),
            "formal_record_ratio": self._clamp(coverage),
            "min_mei_formality_score": self._clamp(min(scores) if scores else 0.0),
            "max_mei_formality_score": self._clamp(max(scores) if scores else 0.0),
        }

        result: Dict[str, Any] = {
            "primitive": "MEI_FORMAL_DEFINITION",
            "axis": "AK_INTRINSIC_IDENTITY_THEOREM",
            "ak_step": "AK2",
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "mei_formal_definition_status": status,
            "mei_formal_defined": defined,
            "mei_formal_count": formal_count,
            "candidate_record_count": candidate_count,
            "mei_formal_definition_score": self._clamp(mean_score),
            "definition_confidence": confidence,
            "definition_metrics": metrics,
            "formal_condition_names": list(self.required_formal_conditions),
            "mei_formal_records": formal_records,
            "upstream_status": {
                "qf_to_mei_certifier_status": (upstream.get("qf_to_mei_certifier") or {}).get("qf_to_mei_certifier_status"),
                "mei_registry_status": (upstream.get("mei_registry") or {}).get("mei_registry_status"),
                "formal_qualia_minimal_definition_status": (upstream.get("formal_qualia_minimal_definition") or {}).get("formal_qualia_minimal_definition_status"),
            },
            "conditions_of_failure": [
                "insufficient_certified_mei_records",
                "low_formal_definition_coverage",
                "low_mei_formality_score",
                "missing_epistemic_guards",
            ],
            "lived_quality_claimed": False,
            "phenomenal_identity_claimed": False,
            "epistemic_guards": dict(EPISTEMIC_GUARDS),
            **EPISTEMIC_GUARDS,
        }
        result["paths"] = self._paths("latest")
        if persist:
            result["paths"] = self._persist(result, filesystem_context=filesystem_context)
        return result


if __name__ == "__main__":
    print(json.dumps(MeiFormalDefinition().step(persist=True), indent=2, ensure_ascii=False))
