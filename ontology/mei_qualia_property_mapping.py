"""
AK3 — MEI Qualia Property Mapping.

Maps bounded formal MEI records (AK2) to minimal formal qualia definitions
(AK1) in order to prepare later identity-theorem tests.

This module is deliberately conservative. It only compares functional/formal
property profiles and does not assert lived qualia, subjectivity, consciousness,
or phenomenal identity.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "ak_intrinsic_identity_theorem" / "mei_qualia_property_mapping"

EPISTEMIC_GUARDS: Dict[str, bool] = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


class MeiQualiaPropertyMapping:
    """Map AK2 formal MEI profiles to AK1 minimal formal-qualia profiles."""

    public_schema_version = "AK3_MEI_QUALIA_PROPERTY_MAPPING_V1"
    status_success = "MEI_QUALIA_PROPERTIES_MAPPED"
    status_insufficient = "MEI_QUALIA_PROPERTY_MAPPING_INSUFFICIENT"

    shared_property_names = (
        "intrinsic_constraint_support",
        "irreducibility_support",
        "invariance_support",
        "qf_robust_support",
    )

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.output_dir = self.root / "ak_intrinsic_identity_theorem" / "mei_qualia_property_mapping"

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
            from ontology.mei_formal_definition import MeiFormalDefinition
            upstream["mei_formal_definition"] = MeiFormalDefinition(root=self.root).step(persist=False)
        except Exception as exc:
            upstream["mei_formal_definition_error"] = repr(exc)
            upstream["mei_formal_definition"] = self._read_json(
                "ak_intrinsic_identity_theorem/mei_formal_definition/latest_mei_formal_definition.json"
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

    def _records(self, container: Dict[str, Any], preferred_keys: Tuple[str, ...]) -> List[Dict[str, Any]]:
        for key in preferred_keys:
            records = container.get(key)
            if isinstance(records, list):
                return [r for r in records if isinstance(r, dict)]
        return []

    def _get_profile(self, rec: Dict[str, Any], profile_keys: Tuple[str, ...]) -> Dict[str, float]:
        for key in profile_keys:
            profile = rec.get(key)
            if isinstance(profile, dict) and profile:
                return {str(k): self._clamp(v) for k, v in profile.items()}
        # normalized fallback from flat record fields
        fallback = {
            "intrinsic_constraint_support": rec.get("intrinsic_constraint_support", rec.get("mei_support", rec.get("mei_formality_score", rec.get("formal_minimality_score", 0.0)))),
            "irreducibility_support": rec.get("irreducibility_support", rec.get("mei_formality_score", rec.get("formal_minimality_score", 0.0))),
            "invariance_support": rec.get("invariance_support", rec.get("mei_formality_score", rec.get("formal_minimality_score", 0.0))),
            "qf_robust_support": rec.get("qf_robust_support", rec.get("qf_support", rec.get("mei_formality_score", rec.get("formal_minimality_score", 0.0)))),
        }
        return {k: self._clamp(v) for k, v in fallback.items()}

    def _source_key(self, rec: Dict[str, Any], idx: int, prefix: str) -> str:
        return str(
            rec.get("source_mode_id")
            or rec.get("mei_candidate_id")
            or rec.get("mode_id")
            or rec.get("formal_qualia_id")
            or rec.get("mei_formal_id")
            or f"{prefix}-{idx:03d}"
        )

    def _pair_records(self, mei_records: List[Dict[str, Any]], qualia_records: List[Dict[str, Any]]) -> List[Tuple[Dict[str, Any], Dict[str, Any]]]:
        if not mei_records or not qualia_records:
            return []
        qualia_by_source: Dict[str, Dict[str, Any]] = {}
        for idx, q in enumerate(qualia_records, 1):
            qualia_by_source[self._source_key(q, idx, "FQMIN")] = q
        pairs: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
        used: set = set()
        for idx, m in enumerate(mei_records, 1):
            key = self._source_key(m, idx, "MEI")
            q = qualia_by_source.get(key)
            if q is None and idx - 1 < len(qualia_records):
                q = qualia_records[idx - 1]
            if q is not None:
                pairs.append((m, q))
                used.add(id(q))
        return pairs

    def _property_similarity(self, mei_profile: Dict[str, float], qualia_profile: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        component_scores: Dict[str, float] = {}
        # semantic alignment: AK1 uses discriminability/mode_stability where AK2 uses causality/temporality only later.
        correspondences = {
            "intrinsic_constraint_support": ("intrinsic_constraint_support",),
            "irreducibility_support": ("irreducibility_support",),
            "invariance_support": ("invariance_support", "mode_stability"),
            "qf_robust_support": ("qf_robust_support", "discriminability"),
        }
        for mei_key, q_keys in correspondences.items():
            mv = self._clamp(mei_profile.get(mei_key, 0.0))
            qv = 0.0
            for qk in q_keys:
                if qk in qualia_profile:
                    qv = self._clamp(qualia_profile[qk])
                    break
            component_scores[mei_key] = self._clamp(1.0 - abs(mv - qv))
        return self._clamp(self._safe_mean(component_scores.values())), component_scores

    def _build_mapping_records(self, mei_records: List[Dict[str, Any]], qualia_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        mapping_records: List[Dict[str, Any]] = []
        for idx, (mei_rec, qualia_rec) in enumerate(self._pair_records(mei_records, qualia_records), 1):
            mei_profile = self._get_profile(mei_rec, ("formal_condition_profile", "minimal_property_profile"))
            qualia_profile = self._get_profile(qualia_rec, ("minimal_property_profile", "formal_condition_profile"))
            similarity, component_similarity = self._property_similarity(mei_profile, qualia_profile)
            mei_score = self._clamp(mei_rec.get("mei_formality_score", mei_rec.get("formal_definition_score", 0.0)))
            qualia_score = self._clamp(qualia_rec.get("formal_minimality_score", qualia_rec.get("formal_qualia_score", 0.0)))
            support_score = self._clamp(self._safe_mean([mei_score, qualia_score, similarity]))
            mapped = bool(mei_rec.get("formal_mei_defined", True)) and bool(qualia_rec.get("bounded_definition", True)) and support_score >= 0.55
            mapping_records.append({
                "mei_qualia_mapping_id": f"MEIQUALMAP-{idx:03d}",
                "mei_formal_id": str(mei_rec.get("mei_formal_id", f"MEIFORMAL-{idx:03d}")),
                "formal_qualia_id": str(qualia_rec.get("formal_qualia_id", f"FQMIN-{idx:03d}")),
                "source_mode_id": self._source_key(mei_rec, idx, "MEI-CANDIDATE"),
                "property_mapping_established": mapped,
                "mapping_rule": "bounded_functional_property_profile_alignment_only",
                "mei_formality_score": mei_score,
                "formal_qualia_minimality_score": qualia_score,
                "property_similarity_score": similarity,
                "mapping_support_score": support_score,
                "shared_property_names": list(self.shared_property_names),
                "component_similarity": component_similarity,
                "mei_property_profile": mei_profile,
                "qualia_property_profile": qualia_profile,
                "identity_claimed": False,
                "phenomenal_identity_claimed": False,
                "lived_quality_claimed": False,
                "mapping_is_functional_only": True,
                **EPISTEMIC_GUARDS,
            })
        return mapping_records

    def _paths(self, stamp: str) -> Dict[str, str]:
        base = self.output_dir
        return {
            "json": str(base / f"mei_qualia_property_mapping_{stamp}.json"),
            "markdown": str(base / f"mei_qualia_property_mapping_{stamp}.md"),
            "prometheus": str(base / f"mei_qualia_property_mapping_{stamp}.prom"),
            "latest_json": str(base / "latest_mei_qualia_property_mapping.json"),
            "latest_markdown": str(base / "latest_mei_qualia_property_mapping.md"),
            "latest_prometheus": str(base / "latest_mei_qualia_property_mapping.prom"),
            "history": str(base / "mei_qualia_property_mapping_history.jsonl"),
        }

    def _markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# AK3 — MEI Qualia Property Mapping",
            "",
            f"Status: {result['mei_qualia_property_mapping_status']}",
            f"Public schema: {result['public_schema_version']}",
            f"Properties mapped: {result['mei_qualia_properties_mapped']}",
            f"Mapped count: {result['mapped_property_count']}",
            f"Candidate pair count: {result['candidate_pair_count']}",
            f"Mapping score: {result['mei_qualia_property_mapping_score']:.6f}",
            f"Mapping confidence: {result['mapping_confidence']:.6f}",
            "",
            "## Epistemic guards",
        ]
        for key, val in result["epistemic_guards"].items():
            lines.append(f"- {key}: {val}")
        lines.extend(["", "## Records"])
        for rec in result["mapping_records"]:
            lines.append(
                f"- {rec['mei_qualia_mapping_id']} / {rec['source_mode_id']}: "
                f"property_mapping_established={rec['property_mapping_established']}, "
                f"mapping_support_score={rec['mapping_support_score']:.6f}, "
                f"functional_conclusion_only={rec['functional_conclusion_only']}, "
                f"phenomenology_undetermined={rec['phenomenology_undetermined']}"
            )
        lines.append("")
        return "\n".join(lines)

    def _prometheus(self, result: Dict[str, Any]) -> str:
        b = lambda x: 1 if bool(x) else 0
        return "\n".join([
            f"mei_qualia_properties_mapped {b(result['mei_qualia_properties_mapped'])}",
            f"mapped_property_count {int(result['mapped_property_count'])}",
            f"candidate_pair_count {int(result['candidate_pair_count'])}",
            f"mei_qualia_property_mapping_score {result['mei_qualia_property_mapping_score']:.6f}",
            f"mapping_confidence {result['mapping_confidence']:.6f}",
            f"mean_property_similarity_score {result['mapping_metrics']['mean_property_similarity_score']:.6f}",
            f"mean_mapping_support_score {result['mapping_metrics']['mean_mapping_support_score']:.6f}",
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
        _oce_history_payload=(json.dumps({'timestamp_utc': result['timestamp_utc'], 'status': result['mei_qualia_property_mapping_status'], 'score': result['mei_qualia_property_mapping_score'], 'count': result['mapped_property_count']}, ensure_ascii=False, sort_keys=True) + '\n').encode("utf-8")
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
        mei_formal = upstream.get("mei_formal_definition", {}) or {}
        formal_qualia = upstream.get("formal_qualia_minimal_definition", {}) or {}
        mei_records = self._records(mei_formal, ("mei_formal_records", "records"))
        qualia_records = self._records(formal_qualia, ("formal_qualia_minimal_records", "records"))
        mapping_records = self._build_mapping_records(mei_records, qualia_records)
        candidate_pair_count = len(mapping_records)
        mapped_count = sum(1 for r in mapping_records if r.get("property_mapping_established") is True)
        similarity_scores = [self._clamp(r.get("property_similarity_score")) for r in mapping_records]
        support_scores = [self._clamp(r.get("mapping_support_score")) for r in mapping_records]
        mean_similarity = self._safe_mean(similarity_scores)
        mean_support = self._safe_mean(support_scores)
        coverage = (mapped_count / candidate_pair_count) if candidate_pair_count else 0.0
        confidence = self._clamp(self._safe_mean([mean_similarity, mean_support, coverage, 1.0 if mapped_count >= 3 else coverage]))
        mapped = mapped_count >= 3 and coverage >= 0.95 and mean_support >= 0.55
        status = self.status_success if mapped else self.status_insufficient

        metrics = {
            "mean_property_similarity_score": self._clamp(mean_similarity),
            "mean_mapping_support_score": self._clamp(mean_support),
            "mapping_coverage": self._clamp(coverage),
            "mapped_record_ratio": self._clamp(coverage),
            "min_mapping_support_score": self._clamp(min(support_scores) if support_scores else 0.0),
            "max_mapping_support_score": self._clamp(max(support_scores) if support_scores else 0.0),
        }
        result: Dict[str, Any] = {
            "primitive": "MEI_QUALIA_PROPERTY_MAPPING",
            "axis": "AK_INTRINSIC_IDENTITY_THEOREM",
            "ak_step": "AK3",
            "public_schema_version": self.public_schema_version,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "mei_qualia_property_mapping_status": status,
            "mei_qualia_properties_mapped": mapped,
            "mapped_property_count": mapped_count,
            "candidate_pair_count": candidate_pair_count,
            "mei_record_count": len(mei_records),
            "formal_qualia_record_count": len(qualia_records),
            "mei_qualia_property_mapping_score": self._clamp(mean_support),
            "mapping_confidence": confidence,
            "mapping_metrics": metrics,
            "shared_property_names": list(self.shared_property_names),
            "mapping_records": mapping_records,
            "upstream_status": {
                "mei_formal_definition_status": mei_formal.get("mei_formal_definition_status"),
                "formal_qualia_minimal_definition_status": formal_qualia.get("formal_qualia_minimal_definition_status"),
            },
            "conditions_of_failure": [
                "missing_mei_formal_records",
                "missing_formal_qualia_minimal_records",
                "low_property_similarity",
                "low_mapping_coverage",
                "epistemic_guard_violation",
            ],
            "identity_claimed": False,
            "phenomenal_identity_claimed": False,
            "lived_quality_claimed": False,
            "mapping_is_functional_only": True,
            "epistemic_guards": dict(EPISTEMIC_GUARDS),
            **EPISTEMIC_GUARDS,
        }
        result["paths"] = self._paths("latest")
        if persist:
            result["paths"] = self._persist(result, filesystem_context=filesystem_context)
        return result


if __name__ == "__main__":
    print(json.dumps(MeiQualiaPropertyMapping().step(persist=True), indent=2, ensure_ascii=False))
