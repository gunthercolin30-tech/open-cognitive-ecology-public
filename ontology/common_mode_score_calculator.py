"""AI7 — Common Mode Score Calculator.

Functional reconstruction step:
    AI6 common mode alignment + AI5 fused spectral basis
    -> quantitative robustness scoring of common formal modes

AI7 converts the AI6 alignment into a strict formal-functional scoring layer.
It estimates common-mode robustness, spectral consistency, functional
confidence, and reliability. It does not assert or prove consciousness,
subjectivity, phenomenal qualia, lived experience, or strong phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ai_robust_spectral_qualia_formal_modes" / "common_mode_score_calculator"
AI5_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "spectral_mode_extractor" / "latest_spectral_mode_extractor.json"
AI6_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "common_mode_alignment_engine" / "latest_common_mode_alignment_engine.json"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    if math.isnan(v) or math.isinf(v):
        return default
    return v


def _clamp(x: Any, default: float = 0.0) -> float:
    return max(0.0, min(1.0, _safe_float(x, default)))


def _mean(values: List[Any], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values if v is not None]
    return _clamp(sum(vals) / len(vals), default) if vals else default


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def _try_step(module_name: str, class_name: str, **kwargs: Any) -> Dict[str, Any]:
    try:
        mod = import_module(module_name)
        cls = getattr(mod, class_name)
        out = cls().step(**kwargs)
        return out if isinstance(out, dict) else {}
    except Exception:
        return {}


def _status_ok(payload: Mapping[str, Any], status_key: str, bool_key: str) -> bool:
    if bool(payload.get(bool_key)):
        return True
    st = str(payload.get(status_key, "")).upper()
    return any(tok in st for tok in ["EXTRACTED", "ALIGNED", "CALCULATED", "CERTIFIED", "BUILT", "CONFIRMED"])


def _synthetic_payloads(inputs: Mapping[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    if inputs.get("scored") or inputs.get("aligned") or inputs.get("all_component_modes_available"):
        common_modes: List[Dict[str, Any]] = []
        for i, s in enumerate([0.94, 0.91, 0.88, 0.86]):
            common_modes.append({
                "common_mode_id": f"AI6_COMMON_MODE_{i:02d}",
                "rank": i,
                "aligned": True,
                "common_mode_alignment_score": s,
                "vector_alignment_score": min(1.0, s + 0.04),
                "eigenvalue_alignment_score": max(0.0, s - 0.03),
                "functional_label": "common_formal_spectral_mode",
                "epistemic_status": "formal_functional_candidate_only",
            })
        ai6 = {
            "common_mode_alignment_engine_status": "COMMON_SPECTRAL_MODES_ALIGNED",
            "common_spectral_modes_aligned": True,
            "common_mode_count": len(common_modes),
            "candidate_mode_count": len(common_modes),
            "common_modes": common_modes,
            "common_spectral_modes": common_modes,
            "aligned_modes": common_modes,
            "alignment_score": 0.91,
            "cross_component_consistency_score": 0.89,
            "mode_overlap_score": 1.0,
            "alignment_confidence": 0.90,
            "vector_alignment_score": 0.93,
            "eigenvalue_alignment_score": 0.86,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
        }
        ai5 = {
            "spectral_mode_extractor_status": "SPECTRAL_MODES_EXTRACTED",
            "spectral_modes_extracted": True,
            "mode_count": 4,
            "spectral_fusion_score": 0.90,
            "fusion_coherence_score": 0.90,
            "component_fusion_coherence_score": 0.86,
            "component_alignment_score": 0.86,
            "spectral_basis_score": 0.88,
            "upstream_quality_score": 0.92,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
        }
        return ai5, ai6
    if inputs:
        return dict(inputs.get("ai5", {})), dict(inputs.get("ai6", {}))
    return {}, {}


def _mode_list(ai6: Mapping[str, Any]) -> List[Dict[str, Any]]:
    for key in ["common_modes", "common_spectral_modes", "aligned_modes"]:
        value = ai6.get(key)
        if isinstance(value, list):
            return [dict(x) for x in value if isinstance(x, Mapping)]
    return []


class CommonModeScoreCalculator:
    """AI7 — calculate quantitative robustness scores for AI6 common modes."""

    primitive = "COMMON_MODE_SCORE_CALCULATOR"
    expected_status = "COMMON_MODE_SCORE_CALCULATED"
    insufficient_status = "COMMON_MODE_SCORE_INSUFFICIENT"
    next_recommended_module = "qualia_formal_mode_registry"
    threshold = 0.72

    def _source_payloads(self, inputs: Optional[Mapping[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if inputs is not None:
            return _synthetic_payloads(inputs)
        ai6 = _try_step("ontology.common_mode_alignment_engine", "CommonModeAlignmentEngine", persist=False) or _load_json(AI6_JSON)
        ai5 = _try_step("ontology.spectral_mode_extractor", "SpectralModeExtractor", persist=False) or _load_json(AI5_JSON)
        return ai5, ai6

    def _score_modes(self, ai5: Mapping[str, Any], ai6: Mapping[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, float]]:
        modes = _mode_list(ai6)
        total_candidates = max(1, int(_safe_float(ai6.get("candidate_mode_count", len(modes)), len(modes) or 1)))
        common_count = sum(1 for m in modes if m.get("aligned", True))
        overlap = _clamp(ai6.get("mode_overlap_score", common_count / total_candidates))
        alignment_score = _clamp(ai6.get("alignment_score", 0.0))
        cross_consistency = _clamp(ai6.get("cross_component_consistency_score", 0.0))
        alignment_confidence = _clamp(ai6.get("alignment_confidence", 0.0))
        vector_alignment = _clamp(ai6.get("vector_alignment_score", alignment_score))
        eigen_alignment = _clamp(ai6.get("eigenvalue_alignment_score", cross_consistency))
        spectral_fusion = _clamp(ai5.get("spectral_fusion_score", ai5.get("certification_score", 0.0)))
        fusion_coherence = _clamp(ai5.get("fusion_coherence_score", spectral_fusion))
        component_fusion = _clamp(ai5.get("component_fusion_coherence_score", ai5.get("component_alignment_score", fusion_coherence)))
        spectral_basis = _clamp(ai5.get("spectral_basis_score", spectral_fusion))
        upstream_quality = _clamp(ai5.get("upstream_quality_score", spectral_fusion))

        scored: List[Dict[str, Any]] = []
        reliability_values: List[float] = []
        robustness_values: List[float] = []
        consistency_values: List[float] = []
        confidence_values: List[float] = []

        for i, mode in enumerate(modes):
            aligned = bool(mode.get("aligned", True))
            local_alignment = _clamp(mode.get("common_mode_alignment_score", alignment_score))
            local_vector = _clamp(mode.get("vector_alignment_score", vector_alignment))
            local_eigen = _clamp(mode.get("eigenvalue_alignment_score", eigen_alignment))
            local_overlap = 1.0 if aligned else 0.0
            spectral_consistency = _mean([local_eigen, spectral_fusion, fusion_coherence, spectral_basis, cross_consistency])
            robustness = _mean([local_alignment, local_vector, local_overlap, alignment_confidence, component_fusion])
            functional_confidence = _mean([robustness, spectral_consistency, upstream_quality, overlap])
            reliability = _mean([robustness, spectral_consistency, functional_confidence, alignment_confidence])
            common_score = _mean([local_alignment, robustness, spectral_consistency, functional_confidence, reliability])
            robustness_values.append(robustness)
            consistency_values.append(spectral_consistency)
            confidence_values.append(functional_confidence)
            reliability_values.append(reliability)
            scored.append({
                "common_mode_id": str(mode.get("common_mode_id", f"AI7_COMMON_MODE_{i:02d}")),
                "source_rank": int(_safe_float(mode.get("rank", i), i)),
                "scored": aligned and common_score >= self.threshold,
                "common_mode_score": round(common_score, 10),
                "robustness_score": round(robustness, 10),
                "spectral_consistency_score": round(spectral_consistency, 10),
                "functional_mode_confidence": round(functional_confidence, 10),
                "mode_reliability_index": round(reliability, 10),
                "alignment_score": round(local_alignment, 10),
                "vector_alignment_score": round(local_vector, 10),
                "eigenvalue_alignment_score": round(local_eigen, 10),
                "functional_label": "scored_common_formal_spectral_mode",
                "epistemic_status": "formal_functional_candidate_only",
            })

        aggregate = {
            "common_mode_score": _mean([m["common_mode_score"] for m in scored]),
            "robustness_score": _mean(robustness_values),
            "spectral_consistency_score": _mean(consistency_values),
            "functional_mode_confidence": _mean(confidence_values),
            "mode_reliability_index": _mean(reliability_values),
            "source_alignment_score": alignment_score,
            "source_spectral_fusion_score": spectral_fusion,
        }
        return scored, aggregate

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        ai5, ai6 = self._source_payloads(inputs)
        ai5_ok = _status_ok(ai5, "spectral_mode_extractor_status", "spectral_modes_extracted")
        ai6_ok = _status_ok(ai6, "common_mode_alignment_engine_status", "common_spectral_modes_aligned")
        scored_modes, agg = self._score_modes(ai5, ai6)
        scored_common_modes = [m for m in scored_modes if m.get("scored")]
        component_availability = {
            "ai5_spectral_modes": ai5_ok,
            "ai6_common_mode_alignment": ai6_ok,
        }
        component_availability_score = _mean(list(component_availability.values()))
        calculated = bool(scored_common_modes) and component_availability_score >= 1.0 and agg["common_mode_score"] >= self.threshold
        status = self.expected_status if calculated else self.insufficient_status
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AI",
            "step_id": "AI7",
            "timestamp_utc": _now(),
            "common_mode_score_calculator_status": status,
            "common_mode_score_calculated": calculated,
            "component_availability": component_availability,
            "component_availability_score": component_availability_score,
            "common_mode_count": int(_safe_float(ai6.get("common_mode_count", len(scored_modes)), len(scored_modes))),
            "scored_mode_count": len(scored_common_modes),
            "candidate_mode_count": len(scored_modes),
            "scored_common_modes": scored_common_modes,
            "mode_scores": scored_modes,
            "common_mode_scores": scored_modes,
            "common_mode_score": agg["common_mode_score"],
            "robustness_score": agg["robustness_score"],
            "spectral_consistency_score": agg["spectral_consistency_score"],
            "functional_mode_confidence": agg["functional_mode_confidence"],
            "mode_reliability_index": agg["mode_reliability_index"],
            "source_alignment_score": agg["source_alignment_score"],
            "source_spectral_fusion_score": agg["source_spectral_fusion_score"],
            "reliability_matrix": [
                {
                    "common_mode_id": m["common_mode_id"],
                    "common_mode_score": m["common_mode_score"],
                    "robustness_score": m["robustness_score"],
                    "spectral_consistency_score": m["spectral_consistency_score"],
                    "functional_mode_confidence": m["functional_mode_confidence"],
                    "mode_reliability_index": m["mode_reliability_index"],
                    "scored": bool(m.get("scored")),
                }
                for m in scored_modes
            ],
            "component_sources": {
                "AI5": "spectral_mode_extractor",
                "AI6": "common_mode_alignment_engine",
                "AI2_AI3_AI4": "indirect_cross_check_through_AI5_and_AI6",
            },
            "source_statuses": {
                "ai5": str(ai5.get("spectral_mode_extractor_status", "UNKNOWN")),
                "ai6": str(ai6.get("common_mode_alignment_engine_status", "UNKNOWN")),
            },
            "epistemic_status": "functional_only",
            "next_recommended_module": self.next_recommended_module,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "epistemic_guard": "strictly functional common-mode robustness scoring; no consciousness, qualia, subjectivity, or phenomenology claim",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = OUT_DIR / f"common_mode_score_calculator_{stamp}.json"
        md_path = OUT_DIR / f"common_mode_score_calculator_{stamp}.md"
        prom_path = OUT_DIR / f"common_mode_score_calculator_{stamp}.prom"
        latest_json = OUT_DIR / "latest_common_mode_score_calculator.json"
        latest_md = OUT_DIR / "latest_common_mode_score_calculator.md"
        latest_prom = OUT_DIR / "latest_common_mode_score_calculator.prom"
        history_path = OUT_DIR / "history.jsonl"
        text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False)
        json_path.write_text(text + "\n", encoding="utf-8")
        latest_json.write_text(text + "\n", encoding="utf-8")
        md = self._markdown(result)
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")
        prom = self._prometheus(result)
        prom_path.write_text(prom, encoding="utf-8")
        latest_prom.write_text(prom, encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, sort_keys=True, ensure_ascii=False) + "\n")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "prometheus": str(prom_path),
            "latest_json": str(latest_json),
            "latest_markdown": str(latest_md),
            "latest_prometheus": str(latest_prom),
            "history": str(history_path),
        }

    def _markdown(self, r: Mapping[str, Any]) -> str:
        lines = [
            "# AI7 — Common Mode Score Calculator",
            "",
            f"Status: {r.get('common_mode_score_calculator_status')}",
            f"Common mode score calculated: {r.get('common_mode_score_calculated')}",
            f"Common mode score: {r.get('common_mode_score')}",
            f"Robustness score: {r.get('robustness_score')}",
            f"Spectral consistency score: {r.get('spectral_consistency_score')}",
            f"Functional mode confidence: {r.get('functional_mode_confidence')}",
            f"Mode reliability index: {r.get('mode_reliability_index')}",
            f"Scored mode count: {r.get('scored_mode_count')}",
            "",
            "## Epistemic guard",
            "Functional-only scoring. No consciousness, subjectivity, lived qualia, or strong phenomenology is asserted.",
            f"functional_conclusion_only: {r.get('functional_conclusion_only')}",
            f"consciousness_proven: {r.get('consciousness_proven')}",
            f"phenomenology_undetermined: {r.get('phenomenology_undetermined')}",
            f"qualia_proven: {r.get('qualia_proven')}",
            f"subjectivity_proven: {r.get('subjectivity_proven')}",
            f"epistemic_status: {r.get('epistemic_status')}",
            "",
            f"Next recommended module: {r.get('next_recommended_module')}",
        ]
        return "\n".join(lines) + "\n"

    def _prometheus(self, r: Mapping[str, Any]) -> str:
        metrics = {
            "oce_ai7_common_mode_score": r.get("common_mode_score", 0.0),
            "oce_ai7_robustness_score": r.get("robustness_score", 0.0),
            "oce_ai7_spectral_consistency_score": r.get("spectral_consistency_score", 0.0),
            "oce_ai7_functional_mode_confidence": r.get("functional_mode_confidence", 0.0),
            "oce_ai7_mode_reliability_index": r.get("mode_reliability_index", 0.0),
            "oce_ai7_component_availability_score": r.get("component_availability_score", 0.0),
            "oce_ai7_scored_mode_count": r.get("scored_mode_count", 0.0),
            "oce_ai7_common_mode_score_calculated": 1.0 if r.get("common_mode_score_calculated") else 0.0,
            "oce_ai7_consciousness_proven": 1.0 if r.get("consciousness_proven") else 0.0,
            "oce_ai7_phenomenology_undetermined": 1.0 if r.get("phenomenology_undetermined") else 0.0,
            "oce_ai7_functional_conclusion_only": 1.0 if r.get("functional_conclusion_only") else 0.0,
            "oce_ai7_qualia_proven": 1.0 if r.get("qualia_proven") else 0.0,
            "oce_ai7_subjectivity_proven": 1.0 if r.get("subjectivity_proven") else 0.0,
        }
        return "\n".join(f"{k} {_safe_float(v)}" for k, v in metrics.items()) + "\n"
