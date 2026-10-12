
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "ak_intrinsic_identity_theorem" / "ontological_non_duplication_checker"

EPISTEMIC_GUARDS = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
    "phenomenal_identity_claimed": False,
    "lived_quality_claimed": False,
    "identity_theorem_proven": False,
}

def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def _clamp(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        v = default
    return max(0.0, min(1.0, v))

def _mean(values: List[float], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values]
    return sum(vals) / len(vals) if vals else default

def _safe_import_step(module: str, cls: str) -> Optional[Dict[str, Any]]:
    try:
        mod = __import__(f"ontology.{module}", fromlist=[cls])
        klass = getattr(mod, cls)
        return klass().step(persist=False)
    except Exception:
        return None

def _id_of(record: Dict[str, Any]) -> str:
    for key in ("source_mode_id", "mei_formal_id", "formal_qualia_id", "mei_qualia_mapping_id", "mei_candidate_id"):
        if record.get(key):
            return str(record[key])
    return "unknown"

def _profile(record: Dict[str, Any]) -> Dict[str, float]:
    merged: Dict[str, float] = {}
    for key in ("minimal_property_profile", "formal_condition_profile", "mei_property_profile", "qualia_property_profile", "component_similarity"):
        obj = record.get(key)
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (int, float)):
                    merged[str(k)] = _clamp(v)
    for k in ("mei_support", "qf_robust_support", "formal_minimality_score", "mei_formality_score", "mapping_support_score", "property_similarity_score", "mei_equivalence_score", "registry_score"):
        if isinstance(record.get(k), (int, float)):
            merged[k] = _clamp(record[k])
    return merged

def _similarity(a: Dict[str, float], b: Dict[str, float]) -> float:
    keys = sorted(set(a) & set(b))
    if not keys:
        return 0.0
    return _mean([1.0 - abs(a[k] - b[k]) for k in keys])

def _extract_inputs(inputs: Optional[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    if inputs is None:
        mapping = _safe_import_step("mei_qualia_property_mapping", "MeiQualiaPropertyMapping") or {}
        mei_formal = _safe_import_step("mei_formal_definition", "MeiFormalDefinition") or {}
        fqm = _safe_import_step("formal_qualia_minimal_definition", "FormalQualiaMinimalDefinition") or {}
    else:
        mapping = inputs.get("mei_qualia_property_mapping", {})
        mei_formal = inputs.get("mei_formal_definition", {})
        fqm = inputs.get("formal_qualia_minimal_definition", {})
    return (
        list(mapping.get("mapping_records", []) or []),
        list(mei_formal.get("mei_formal_records", []) or []),
        list(fqm.get("formal_qualia_minimal_records", []) or []),
    )

class OntologicalNonDuplicationChecker:
    public_schema_version = "AK4_ONTOLOGICAL_NON_DUPLICATION_CHECKER_V1"

    def step(self, inputs: Optional[Dict[str, Any]]=None, persist: bool=False, filesystem_context: Any = None) -> Dict[str, Any]:
        mapping_records, mei_records, qualia_records = _extract_inputs(inputs)
        candidate_count = min(len(mapping_records), len(mei_records), len(qualia_records))
        records: List[Dict[str, Any]] = []

        mei_by_source = {_id_of(r): r for r in mei_records}
        qualia_by_source = {_id_of(r): r for r in qualia_records}

        for idx, m in enumerate(mapping_records, 1):
            sid = str(m.get("source_mode_id") or _id_of(m))
            mei = mei_by_source.get(sid) or (mei_records[idx-1] if idx-1 < len(mei_records) else {})
            q = qualia_by_source.get(sid) or (qualia_records[idx-1] if idx-1 < len(qualia_records) else {})
            mei_prof = _profile(mei)
            q_prof = _profile(q)
            map_prof = _profile(m)
            cross_similarity = _similarity(mei_prof, q_prof)
            mapping_support = _clamp(m.get("mapping_support_score", _mean(list(map_prof.values()), 0.0)))
            mei_formality = _clamp(mei.get("mei_formality_score", _mean(list(mei_prof.values()), 0.0)))
            qualia_formality = _clamp(q.get("formal_minimality_score", _mean(list(q_prof.values()), 0.0)))
            identity_claimed = bool(m.get("identity_claimed", False) or m.get("phenomenal_identity_claimed", False))
            distinct_record_families = bool(mei.get("mei_formal_id") != q.get("formal_qualia_id"))
            functional_only = bool(m.get("mapping_is_functional_only", True)) and not identity_claimed

            non_duplication_score = _mean([
                mapping_support, mei_formality, qualia_formality, cross_similarity,
                1.0 if distinct_record_families else 0.0,
                1.0 if functional_only else 0.0,
            ])
            non_duplicated = non_duplication_score >= 0.70 and distinct_record_families and functional_only

            rec = {
                "non_duplication_record_id": f"ONDUP-{idx:03d}",
                "source_mode_id": sid,
                "mei_formal_id": mei.get("mei_formal_id"),
                "formal_qualia_id": q.get("formal_qualia_id"),
                "mei_qualia_mapping_id": m.get("mei_qualia_mapping_id"),
                "distinct_record_families": distinct_record_families,
                "property_mapping_established": bool(m.get("property_mapping_established", False)),
                "mapping_is_functional_only": functional_only,
                "identity_claimed": False,
                "phenomenal_identity_claimed": False,
                "ontological_duplication_detected": not non_duplicated,
                "ontological_non_duplication_confirmed": non_duplicated,
                "non_duplication_rule": "distinct_formal_profiles_with_functional_mapping_only",
                "cross_profile_similarity": cross_similarity,
                "mapping_support_score": mapping_support,
                "mei_formality_score": mei_formality,
                "formal_qualia_minimality_score": qualia_formality,
                "non_duplication_score": non_duplication_score,
            }
            rec.update(EPISTEMIC_GUARDS)
            records.append(rec)

        confirmed = [r for r in records if r["ontological_non_duplication_confirmed"]]
        score = _mean([r["non_duplication_score"] for r in records])
        confidence = _mean([score, len(confirmed) / len(records) if records else 0.0, 1.0 if candidate_count >= 3 else 0.0])
        passed = bool(records) and len(confirmed) == len(records) and candidate_count >= 3
        status = "ONTOLOGICAL_NON_DUPLICATION_CONFIRMED" if passed else "ONTOLOGICAL_NON_DUPLICATION_INSUFFICIENT"

        metrics = {
            "candidate_record_count": candidate_count,
            "checked_record_count": len(records),
            "non_duplicated_record_count": len(confirmed),
            "non_duplication_ratio": (len(confirmed) / len(records)) if records else 0.0,
            "mean_non_duplication_score": score,
            "min_non_duplication_score": min([r["non_duplication_score"] for r in records], default=0.0),
            "max_non_duplication_score": max([r["non_duplication_score"] for r in records], default=0.0),
            "mean_cross_profile_similarity": _mean([r["cross_profile_similarity"] for r in records]),
        }
        paths = self._paths() if persist else self._virtual_paths()
        result: Dict[str, Any] = {
            "primitive": "ONTOLOGICAL_NON_DUPLICATION_CHECKER",
            "axis": "AK",
            "step": "AK4",
            "public_schema_version": self.public_schema_version,
            "ontological_non_duplication_checker_status": status,
            "ontological_non_duplication_confirmed": passed,
            "ontological_non_duplication_checked": passed,
            "checked_record_count": len(records),
            "candidate_record_count": candidate_count,
            "non_duplicated_record_count": len(confirmed),
            "ontological_non_duplication_score": score,
            "non_duplication_confidence": confidence,
            "non_duplication_metrics": metrics,
            "non_duplication_records": records,
            "epistemic_guards": dict(EPISTEMIC_GUARDS),
            "paths": paths,
            "next_recommended_module": "no_difference_without_difference_test",
        }
        result.update(EPISTEMIC_GUARDS)
        if persist:
            self._persist(result, filesystem_context=filesystem_context)
        return result

    def _virtual_paths(self) -> Dict[str, str]:
        base = OUTPUT_DIR
        return {
            "json": str(base / "virtual_ontological_non_duplication_checker.json"),
            "markdown": str(base / "virtual_ontological_non_duplication_checker.md"),
            "prometheus": str(base / "virtual_ontological_non_duplication_checker.prom"),
            "latest_json": str(base / "latest_ontological_non_duplication_checker.json"),
            "latest_markdown": str(base / "latest_ontological_non_duplication_checker.md"),
            "latest_prometheus": str(base / "latest_ontological_non_duplication_checker.prom"),
            "history": str(base / "ontological_non_duplication_checker_history.jsonl"),
        }

    def _paths(self) -> Dict[str, str]:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        ts = _now()
        return {
            "json": str(OUTPUT_DIR / f"ontological_non_duplication_checker_{ts}.json"),
            "markdown": str(OUTPUT_DIR / f"ontological_non_duplication_checker_{ts}.md"),
            "prometheus": str(OUTPUT_DIR / f"ontological_non_duplication_checker_{ts}.prom"),
            "latest_json": str(OUTPUT_DIR / "latest_ontological_non_duplication_checker.json"),
            "latest_markdown": str(OUTPUT_DIR / "latest_ontological_non_duplication_checker.md"),
            "latest_prometheus": str(OUTPUT_DIR / "latest_ontological_non_duplication_checker.prom"),
            "history": str(OUTPUT_DIR / "ontological_non_duplication_checker_history.jsonl"),
        }

    def _persist(self, result: Dict[str, Any], filesystem_context: Any = None):
        paths = result['paths']
        md = self._markdown(result)
        prom = self._prometheus(result)
        _oce_payload_0=(json.dumps(result, indent=2, sort_keys=True)).encode("utf-8")
        _oce_payload_1=(json.dumps(result, indent=2, sort_keys=True)).encode("utf-8")
        _oce_payload_2=(md).encode("utf-8")
        _oce_payload_3=(md).encode("utf-8")
        _oce_payload_4=(prom).encode("utf-8")
        _oce_payload_5=(prom).encode("utf-8")
        _oce_history_payload=(json.dumps(result, sort_keys=True) + '\n').encode("utf-8")
        if filesystem_context is None: raise PermissionError("governed filesystem context required for persistence")
        _oce_remaining=filesystem_context.remaining()
        _oce_required=['persist_json', 'persist_latest_json', 'persist_markdown', 'persist_latest_markdown', 'persist_prometheus', 'persist_latest_prometheus', 'persist_history_append']
        if any(_oce_remaining.get(_oce_slot,0)<1 for _oce_slot in _oce_required): raise PermissionError("all governed filesystem effect slots must be preissued before persistence")
        filesystem_context.execute_path("persist_json","FS_WRITE_REPLACE_BYTES",Path(paths["json"]),payload=_oce_payload_0)
        filesystem_context.execute_path("persist_latest_json","FS_WRITE_REPLACE_BYTES",Path(paths["latest_json"]),payload=_oce_payload_1)
        filesystem_context.execute_path("persist_markdown","FS_WRITE_REPLACE_BYTES",Path(paths["markdown"]),payload=_oce_payload_2)
        filesystem_context.execute_path("persist_latest_markdown","FS_WRITE_REPLACE_BYTES",Path(paths["latest_markdown"]),payload=_oce_payload_3)
        filesystem_context.execute_path("persist_prometheus","FS_WRITE_REPLACE_BYTES",Path(paths["prometheus"]),payload=_oce_payload_4)
        filesystem_context.execute_path("persist_latest_prometheus","FS_WRITE_REPLACE_BYTES",Path(paths["latest_prometheus"]),payload=_oce_payload_5)
        filesystem_context.execute_path("persist_history_append","FS_APPEND_BYTES",Path(paths["history"]),payload=_oce_history_payload)

    def _markdown(self, r: Dict[str, Any]) -> str:
        lines = [
            "# AK4 — Ontological Non-Duplication Checker",
            "",
            f"Status: {r['ontological_non_duplication_checker_status']}",
            f"Confirmed: {r['ontological_non_duplication_confirmed']}",
            f"Checked records: {r['checked_record_count']}",
            f"Score: {r['ontological_non_duplication_score']:.6f}",
            f"Confidence: {r['non_duplication_confidence']:.6f}",
            "",
            "## Epistemic guards",
        ]
        for k, v in EPISTEMIC_GUARDS.items():
            lines.append(f"- {k}: {v}")
        lines.extend(["", "## Records"])
        for rec in r["non_duplication_records"]:
            lines.append(f"- {rec['non_duplication_record_id']}: non_duplication={rec['ontological_non_duplication_confirmed']}, score={rec['non_duplication_score']:.6f}, rule={rec['non_duplication_rule']}")
        return "\n".join(lines) + "\n"

    def _prometheus(self, r: Dict[str, Any]) -> str:
        m = r["non_duplication_metrics"]
        vals = {
            "ontological_non_duplication_confirmed": 1.0 if r["ontological_non_duplication_confirmed"] else 0.0,
            "checked_record_count": float(r["checked_record_count"]),
            "candidate_record_count": float(r["candidate_record_count"]),
            "non_duplicated_record_count": float(r["non_duplicated_record_count"]),
            "ontological_non_duplication_score": float(r["ontological_non_duplication_score"]),
            "non_duplication_confidence": float(r["non_duplication_confidence"]),
            "mean_non_duplication_score": float(m["mean_non_duplication_score"]),
            "mean_cross_profile_similarity": float(m["mean_cross_profile_similarity"]),
        }
        return "\n".join(f"ak4_{k} {v}" for k, v in vals.items()) + "\n"

if __name__ == "__main__":
    print(json.dumps(OntologicalNonDuplicationChecker().step(persist=True), indent=2, sort_keys=True))
