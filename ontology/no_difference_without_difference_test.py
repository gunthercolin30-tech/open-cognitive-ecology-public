
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUTPUT_DIR = ROOT / "ak_intrinsic_identity_theorem" / "no_difference_without_difference_test"

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

def _extract_inputs(inputs: Optional[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    if inputs is None:
        nd = _safe_import_step("ontological_non_duplication_checker", "OntologicalNonDuplicationChecker") or {}
        mp = _safe_import_step("mei_qualia_property_mapping", "MeiQualiaPropertyMapping") or {}
    else:
        nd = inputs.get("ontological_non_duplication_checker", {})
        mp = inputs.get("mei_qualia_property_mapping", {})
    return list(nd.get("non_duplication_records", []) or []), list(mp.get("mapping_records", []) or [])

def _id_of(record: Dict[str, Any]) -> str:
    for key in ("source_mode_id", "mei_qualia_mapping_id", "non_duplication_record_id", "mei_formal_id", "formal_qualia_id"):
        if record.get(key):
            return str(record[key])
    return "unknown"

def _profile(record: Dict[str, Any]) -> Dict[str, float]:
    profile: Dict[str, float] = {}
    for key in ("component_similarity", "mei_property_profile", "qualia_property_profile", "formal_condition_profile", "minimal_property_profile"):
        obj = record.get(key)
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (int, float)):
                    profile[str(k)] = _clamp(v)
    for key in (
        "mapping_support_score", "property_similarity_score", "non_duplication_score",
        "cross_profile_similarity", "mei_formality_score", "formal_qualia_minimality_score",
    ):
        if isinstance(record.get(key), (int, float)):
            profile[key] = _clamp(record[key])
    return profile

def _distance(a: Dict[str, float], b: Dict[str, float]) -> float:
    keys = sorted(set(a) & set(b))
    if not keys:
        return 0.0
    return _mean([abs(a[k] - b[k]) for k in keys])

class NoDifferenceWithoutDifferenceTest:
    public_schema_version = "AK5_NO_DIFFERENCE_WITHOUT_DIFFERENCE_TEST_V1"

    def step(self, inputs: Optional[Dict[str, Any]]=None, persist: bool=False, filesystem_context: Any = None) -> Dict[str, Any]:
        nondup_records, mapping_records = _extract_inputs(inputs)
        candidate_count = min(len(nondup_records), len(mapping_records))
        mapping_by_source = {_id_of(r): r for r in mapping_records}
        records: List[Dict[str, Any]] = []

        for idx, nd in enumerate(nondup_records, 1):
            sid = str(nd.get("source_mode_id") or _id_of(nd))
            mp = mapping_by_source.get(sid) or (mapping_records[idx - 1] if idx - 1 < len(mapping_records) else {})
            nd_profile = _profile(nd)
            mp_profile = _profile(mp)
            functional_difference_score = _distance(nd_profile, mp_profile)
            property_similarity = _clamp(mp.get("property_similarity_score", nd.get("cross_profile_similarity", 0.0)))
            non_duplication_score = _clamp(nd.get("non_duplication_score", 0.0))
            mapping_support = _clamp(mp.get("mapping_support_score", nd.get("mapping_support_score", 0.0)))
            ontological_duplication_detected = bool(nd.get("ontological_duplication_detected", False))
            identity_claimed = bool(nd.get("identity_claimed", False) or mp.get("identity_claimed", False))
            functional_only = bool(nd.get("functional_conclusion_only", True) and mp.get("functional_conclusion_only", True))

            no_difference_without_difference_supported = (
                functional_difference_score <= 0.10
                and property_similarity >= 0.70
                and non_duplication_score >= 0.70
                and mapping_support >= 0.70
                and not ontological_duplication_detected
                and not identity_claimed
                and functional_only
            )
            support_score = _mean([
                1.0 - functional_difference_score,
                property_similarity,
                non_duplication_score,
                mapping_support,
                1.0 if not ontological_duplication_detected else 0.0,
                1.0 if not identity_claimed else 0.0,
                1.0 if functional_only else 0.0,
            ])

            rec = {
                "no_difference_record_id": f"NDWD-{idx:03d}",
                "source_mode_id": sid,
                "mei_qualia_mapping_id": mp.get("mei_qualia_mapping_id"),
                "non_duplication_record_id": nd.get("non_duplication_record_id"),
                "test_rule": "no_ontological_difference_without_functional_difference_evidence",
                "functional_difference_score": functional_difference_score,
                "property_similarity_score": property_similarity,
                "mapping_support_score": mapping_support,
                "non_duplication_score": non_duplication_score,
                "ontological_duplication_detected": ontological_duplication_detected,
                "identity_claimed": False,
                "phenomenal_identity_claimed": False,
                "no_difference_without_difference_supported": no_difference_without_difference_supported,
                "difference_evidence_required": True,
                "difference_evidence_detected": functional_difference_score > 0.10,
                "test_is_functional_only": True,
                "no_difference_without_difference_score": support_score,
            }
            rec.update(EPISTEMIC_GUARDS)
            records.append(rec)

        supported = [r for r in records if r["no_difference_without_difference_supported"]]
        score = _mean([r["no_difference_without_difference_score"] for r in records])
        support_ratio = len(supported) / len(records) if records else 0.0
        confidence = _mean([score, support_ratio, 1.0 if candidate_count >= 3 else 0.0])
        passed = bool(records) and candidate_count >= 3 and len(supported) == len(records)
        status = "NO_DIFFERENCE_WITHOUT_DIFFERENCE_TEST_PASSED" if passed else "NO_DIFFERENCE_WITHOUT_DIFFERENCE_TEST_INSUFFICIENT"

        metrics = {
            "candidate_record_count": candidate_count,
            "tested_record_count": len(records),
            "supported_record_count": len(supported),
            "support_ratio": support_ratio,
            "mean_no_difference_without_difference_score": score,
            "min_no_difference_without_difference_score": min([r["no_difference_without_difference_score"] for r in records], default=0.0),
            "max_no_difference_without_difference_score": max([r["no_difference_without_difference_score"] for r in records], default=0.0),
            "mean_functional_difference_score": _mean([r["functional_difference_score"] for r in records]),
            "mean_property_similarity_score": _mean([r["property_similarity_score"] for r in records]),
        }
        paths = self._paths() if persist else self._virtual_paths()
        result: Dict[str, Any] = {
            "primitive": "NO_DIFFERENCE_WITHOUT_DIFFERENCE_TEST",
            "axis": "AK",
            "step": "AK5",
            "public_schema_version": self.public_schema_version,
            "no_difference_without_difference_test_status": status,
            "no_difference_without_difference_test_passed": passed,
            "no_difference_without_difference_supported": passed,
            "tested_record_count": len(records),
            "candidate_record_count": candidate_count,
            "supported_record_count": len(supported),
            "no_difference_without_difference_score": score,
            "test_confidence": confidence,
            "difference_test_metrics": metrics,
            "test_records": records,
            "epistemic_guards": dict(EPISTEMIC_GUARDS),
            "paths": paths,
            "next_recommended_module": "intrinsic_zombie_counterexample",
        }
        result.update(EPISTEMIC_GUARDS)
        if persist:
            self._persist(result, filesystem_context=filesystem_context)
        return result

    def _virtual_paths(self) -> Dict[str, str]:
        base = OUTPUT_DIR
        return {
            "json": str(base / "virtual_no_difference_without_difference_test.json"),
            "markdown": str(base / "virtual_no_difference_without_difference_test.md"),
            "prometheus": str(base / "virtual_no_difference_without_difference_test.prom"),
            "latest_json": str(base / "latest_no_difference_without_difference_test.json"),
            "latest_markdown": str(base / "latest_no_difference_without_difference_test.md"),
            "latest_prometheus": str(base / "latest_no_difference_without_difference_test.prom"),
            "history": str(base / "no_difference_without_difference_test_history.jsonl"),
        }

    def _paths(self) -> Dict[str, str]:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        ts = _now()
        return {
            "json": str(OUTPUT_DIR / f"no_difference_without_difference_test_{ts}.json"),
            "markdown": str(OUTPUT_DIR / f"no_difference_without_difference_test_{ts}.md"),
            "prometheus": str(OUTPUT_DIR / f"no_difference_without_difference_test_{ts}.prom"),
            "latest_json": str(OUTPUT_DIR / "latest_no_difference_without_difference_test.json"),
            "latest_markdown": str(OUTPUT_DIR / "latest_no_difference_without_difference_test.md"),
            "latest_prometheus": str(OUTPUT_DIR / "latest_no_difference_without_difference_test.prom"),
            "history": str(OUTPUT_DIR / "no_difference_without_difference_test_history.jsonl"),
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
            "# AK5 — No Difference Without Difference Test",
            "",
            f"Status: {r['no_difference_without_difference_test_status']}",
            f"Passed: {r['no_difference_without_difference_test_passed']}",
            f"Tested records: {r['tested_record_count']}",
            f"Score: {r['no_difference_without_difference_score']:.6f}",
            f"Confidence: {r['test_confidence']:.6f}",
            "",
            "## Epistemic guards",
        ]
        for k, v in EPISTEMIC_GUARDS.items():
            lines.append(f"- {k}: {v}")
        lines.extend(["", "## Records"])
        for rec in r["test_records"]:
            lines.append(f"- {rec['no_difference_record_id']}: supported={rec['no_difference_without_difference_supported']}, functional_difference={rec['functional_difference_score']:.6f}, score={rec['no_difference_without_difference_score']:.6f}")
        return "\n".join(lines) + "\n"

    def _prometheus(self, r: Dict[str, Any]) -> str:
        m = r["difference_test_metrics"]
        vals = {
            "no_difference_without_difference_test_passed": 1.0 if r["no_difference_without_difference_test_passed"] else 0.0,
            "tested_record_count": float(r["tested_record_count"]),
            "candidate_record_count": float(r["candidate_record_count"]),
            "supported_record_count": float(r["supported_record_count"]),
            "no_difference_without_difference_score": float(r["no_difference_without_difference_score"]),
            "test_confidence": float(r["test_confidence"]),
            "mean_functional_difference_score": float(m["mean_functional_difference_score"]),
            "mean_property_similarity_score": float(m["mean_property_similarity_score"]),
        }
        return "\n".join(f"ak5_{k} {v}" for k, v in vals.items()) + "\n"

if __name__ == "__main__":
    print(json.dumps(NoDifferenceWithoutDifferenceTest().step(persist=True), indent=2, sort_keys=True))
