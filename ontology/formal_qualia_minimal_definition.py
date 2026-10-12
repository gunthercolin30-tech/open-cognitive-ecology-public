"""
AK1 — Formal Qualia Minimal Definition v3.

Defines minimal formal qualia as functional, non-phenomenal comparison records
for the AK Intrinsic Identity Theorem program.

This module is deliberately epistemically conservative: it defines measurable
formal structures only and never asserts lived quality, subjectivity, qualia in
the phenomenal sense, or consciousness.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "ak_intrinsic_identity_theorem" / "formal_qualia_minimal_definition"

EPISTEMIC_GUARDS: Dict[str, bool] = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


class FormalQualiaMinimalDefinition:
    """Build a minimal formal-qualia definition layer from AJ/AI evidence."""

    public_schema_version = "AK1_FORMAL_QUALIA_MINIMAL_DEFINITION_V3"
    status_success = "FORMAL_QUALIA_MINIMAL_DEFINED"
    status_insufficient = "FORMAL_QUALIA_MINIMAL_INSUFFICIENT"

    required_minimal_properties = (
        "discriminability",
        "mode_stability",
        "intrinsic_constraint_support",
        "irreducibility_support",
        "invariance_support",
    )

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.output_dir = self.root / "ak_intrinsic_identity_theorem" / "formal_qualia_minimal_definition"

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

        if not upstream.get("qf_to_mei_certifier"):
            upstream["qf_to_mei_certifier"] = self._read_json(
                "aj_intrinsic_existence_modes/qf_to_mei_certifier/latest_qf_to_mei_certifier.json"
            )
        if not upstream.get("mei_registry"):
            upstream["mei_registry"] = self._read_json(
                "aj_intrinsic_existence_modes/mei_registry/latest_mei_registry.json"
            )
        return upstream

    def _extract_records(self, upstream: Dict[str, Any]) -> List[Dict[str, Any]]:
        qf_cert = upstream.get("qf_to_mei_certifier", {}) or {}
        mei_registry = upstream.get("mei_registry", {}) or {}

        for key in ("certification_records", "certified_records", "records"):
            records = qf_cert.get(key)
            if isinstance(records, list) and records:
                return [r for r in records if isinstance(r, dict)]

        for key in ("mei_records", "registered_mei_records", "records"):
            records = mei_registry.get(key)
            if isinstance(records, list) and records:
                return [r for r in records if isinstance(r, dict)]

        # Robust fallback: if AJ9/AJ8 certified counts exist but detailed records
        # are absent under an evolved schema, synthesize formal minimal source
        # records from public aggregate metrics only.
        count = int(
            self._clamp(qf_cert.get("certified_record_count", mei_registry.get("registered_mei_count", 0)), 0.0)
            * 0
        )
        try:
            count = int(qf_cert.get("certified_record_count") or mei_registry.get("registered_mei_count") or 0)
        except Exception:
            count = 0
        score = self._clamp(
            qf_cert.get("qf_to_mei_certification_score", mei_registry.get("mei_registry_score", 0.0))
        )
        confidence = self._clamp(
            qf_cert.get("certification_confidence", mei_registry.get("registry_confidence", score))
        )
        if count >= 3 and score >= 0.50:
            return [
                {
                    "source_mode_id": f"AJ-CERTIFIED-MEI-{i:03d}",
                    "certification_score": score,
                    "qf_robust_support": score,
                    "mei_support": confidence,
                    "registry_confidence": confidence,
                    "synthetic_from_aggregate": True,
                }
                for i in range(1, count + 1)
            ]
        return []

    def _profile_from_record(self, record: Dict[str, Any]) -> Dict[str, float]:
        equivalence = self._clamp(
            record.get("certification_score",
                record.get("mei_equivalence_score",
                    record.get("registry_score",
                        record.get("mei_score", record.get("qf_to_mei_score", 0.0)))))
        )
        intrinsic = self._clamp(record.get("intrinsicality_score", record.get("mei_support", equivalence)))
        irreducibility = self._clamp(record.get("irreducibility_score", record.get("intrinsic_irreducibility_score", equivalence)))
        invariance = self._clamp(record.get("invariance_score", record.get("intrinsic_invariance_score", equivalence)))
        stability = self._clamp(record.get("mode_stability", record.get("registry_confidence", equivalence)))
        discriminability = self._clamp(record.get("discriminability", record.get("distinctness_score", equivalence)))
        return {
            "discriminability": discriminability,
            "mode_stability": stability,
            "intrinsic_constraint_support": intrinsic,
            "irreducibility_support": irreducibility,
            "invariance_support": invariance,
        }

    def _build_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for idx, rec in enumerate(records, start=1):
            source_id = str(
                rec.get("mei_candidate_id")
                or rec.get("mei_id")
                or rec.get("formal_mode_id")
                or rec.get("source_mode_id")
                or f"MEI-CANDIDATE-{idx:03d}"
            )
            profile = self._profile_from_record(rec)
            qf_support = self._clamp(
                rec.get("qf_to_mei_score", rec.get("qf_robust_support", rec.get("qf_support", self._safe_mean(profile.values()))))
            )
            mei_support = self._clamp(
                rec.get("mei_to_qf_score", rec.get("mei_support", rec.get("registry_score", self._safe_mean(profile.values()))))
            )
            score = self._clamp(self._safe_mean([*profile.values(), qf_support, mei_support]))
            bounded = score >= 0.50 and all(0.0 <= v <= 1.0 for v in profile.values())
            out.append({
                "formal_qualia_id": f"FQMIN-{idx:03d}",
                "source_mode_id": source_id,
                "minimal_property_profile": profile,
                "qf_robust_support": qf_support,
                "mei_support": mei_support,
                "formal_minimality_score": score,
                "bounded_definition": bounded,
                "lived_quality_claimed": False,
                "phenomenal_identity_claimed": False,
                "definition_rule": "minimal_functional_property_profile_only",
                **EPISTEMIC_GUARDS,
            })
        return out

    def _paths(self, stamp: str) -> Dict[str, str]:
        base = self.output_dir
        return {
            "json": str(base / f"formal_qualia_minimal_definition_{stamp}.json"),
            "markdown": str(base / f"formal_qualia_minimal_definition_{stamp}.md"),
            "prometheus": str(base / f"formal_qualia_minimal_definition_{stamp}.prom"),
            "latest_json": str(base / "latest_formal_qualia_minimal_definition.json"),
            "latest_markdown": str(base / "latest_formal_qualia_minimal_definition.md"),
            "latest_prometheus": str(base / "latest_formal_qualia_minimal_definition.prom"),
            "history": str(base / "formal_qualia_minimal_definition_history.jsonl"),
        }

    def _markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# AK1 — Formal Qualia Minimal Definition",
            "",
            f"Status: {result['formal_qualia_minimal_definition_status']}",
            f"Public schema: {result['public_schema_version']}",
            f"Definition built: {result['formal_qualia_minimal_defined']}",
            f"Minimal records: {result['formal_qualia_minimal_count']}",
            f"Definition score: {result['formal_qualia_minimal_definition_score']:.6f}",
            f"Definition confidence: {result['definition_confidence']:.6f}",
            "",
            "## Epistemic guards",
        ]
        for key, value in result["epistemic_guards"].items():
            lines.append(f"- {key}: {value}")
        lines.extend([
            "",
            "## Interpretation",
            "Minimal formal qualia are functional comparison records only.",
            "No lived quality, phenomenal identity, subjectivity, or consciousness is inferred.",
            "",
            "## Records",
        ])
        for rec in result["formal_qualia_minimal_records"]:
            lines.append(
                f"- {rec['formal_qualia_id']} from {rec['source_mode_id']}: "
                f"score={rec['formal_minimality_score']:.6f}, "
                f"functional_conclusion_only={rec['functional_conclusion_only']}, "
                f"phenomenology_undetermined={rec['phenomenology_undetermined']}"
            )
        return "\n".join(lines) + "\n"

    def _prometheus(self, result: Dict[str, Any]) -> str:
        return "\n".join([
            f"formal_qualia_minimal_defined {1 if result['formal_qualia_minimal_defined'] else 0}",
            f"formal_qualia_minimal_count {result['formal_qualia_minimal_count']}",
            f"candidate_record_count {result['candidate_record_count']}",
            f"formal_qualia_minimal_definition_score {result['formal_qualia_minimal_definition_score']:.6f}",
            f"definition_confidence {result['definition_confidence']:.6f}",
            f"phenomenology_undetermined {1 if result['phenomenology_undetermined'] else 0}",
            f"functional_conclusion_only {1 if result['functional_conclusion_only'] else 0}",
            "",
        ])

    def _persist(self, result: Dict[str, Any], filesystem_context: Any = None):
        stamp = self._now()
        paths = self._paths(stamp)
        result['paths'] = paths
        payload = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
        md = self._markdown(result)
        prom = self._prometheus(result)
        _oce_payload_0=(payload + '\n').encode("utf-8")
        _oce_payload_1=(payload + '\n').encode("utf-8")
        _oce_payload_2=(md).encode("utf-8")
        _oce_payload_3=(md).encode("utf-8")
        _oce_payload_4=(prom).encode("utf-8")
        _oce_payload_5=(prom).encode("utf-8")
        _oce_history_payload=(payload + '\n').encode("utf-8")
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

    def step(self, inputs: Optional[Dict[str, Any]]=None, persist: bool=True, filesystem_context: Any = None) -> Dict[str, Any]:
        upstream = self._load_upstream(inputs)
        candidates = self._extract_records(upstream)
        formal_records = self._build_records(candidates)
        valid = [r for r in formal_records if r["bounded_definition"]]
        scores = [r["formal_minimality_score"] for r in valid]
        definition_score = self._clamp(self._safe_mean(scores))
        coverage = self._clamp(len(valid) / max(1, len(candidates)))
        confidence = self._clamp(self._safe_mean([definition_score, coverage]))
        defined = len(valid) >= 3 and definition_score >= 0.50
        status = self.status_success if defined else self.status_insufficient
        metrics = {
            "mean_formal_minimality_score": definition_score,
            "mean_minimal_formality_score": definition_score,
            "candidate_coverage": coverage,
            "definition_confidence": confidence,
            "minimal_property_count": len(self.required_minimal_properties),
            "valid_record_count": len(valid),
        }
        result: Dict[str, Any] = {
            "primitive": "FORMAL_QUALIA_MINIMAL_DEFINITION",
            "axis": "AK",
            "step": "AK1",
            "public_schema_version": self.public_schema_version,
            "formal_qualia_minimal_definition_status": status,
            "formal_qualia_minimal_defined": defined,
            "formal_qualia_minimal_count": len(valid),
            "candidate_record_count": len(candidates),
            "required_minimal_properties": list(self.required_minimal_properties),
            "formal_qualia_minimal_records": valid,
            "definition_metrics": metrics,
            "formal_qualia_minimal_definition_score": definition_score,
            "definition_confidence": confidence,
            "epistemic_guards": dict(EPISTEMIC_GUARDS),
            "upstream_sources": sorted(k for k in upstream.keys() if not k.endswith("_error")),
            "failure_conditions": [
                "candidate_record_count < 3",
                "mean_formal_minimality_score < 0.50",
                "missing_AJ_certification_or_MEI_registry",
                "attempted_phenomenal_or_subjectivity_claim",
            ],
            **EPISTEMIC_GUARDS,
        }
        result["paths"] = self._paths("preview")
        if persist:
            self._persist(result, filesystem_context=filesystem_context)
        return result


if __name__ == "__main__":
    from pprint import pprint
    pprint(FormalQualiaMinimalDefinition().step(persist=True))
