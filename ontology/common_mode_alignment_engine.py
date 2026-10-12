
"""AI6 — Common Mode Alignment Engine.

Functional reconstruction step:
    L_graph modes + L_markov modes + L_Π modes + AI5 fused L_RF modes
    -> common robust spectral mode alignment

AI6 identifies modes that are functionally coherent across the three upstream
families and the AI5 fused spectral basis. It is a strict formal-functional
alignment module. It does not assert or prove consciousness, subjectivity,
phenomenal qualia, lived experience, or strong phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ai_robust_spectral_qualia_formal_modes" / "common_mode_alignment_engine"
AI2_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "graph_laplacian_mode_extractor" / "latest_graph_laplacian_mode_extractor.json"
AI3_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "markov_transition_mode_extractor" / "latest_markov_transition_mode_extractor.json"
AI4_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "possibility_gradient_mode_extractor" / "latest_possibility_gradient_mode_extractor.json"
AI5_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "spectral_mode_extractor" / "latest_spectral_mode_extractor.json"


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


def _try_step(module_name: str, class_name: str) -> Dict[str, Any]:
    try:
        mod = import_module(module_name)
        cls = getattr(mod, class_name)
        out = cls().step(persist=False)
        return out if isinstance(out, dict) else {}
    except Exception:
        return {}


def _normalize_vector(vec: Any) -> List[float]:
    if not isinstance(vec, list):
        return []
    vals = [_safe_float(x, 0.0) for x in vec]
    norm = math.sqrt(sum(x * x for x in vals))
    if norm <= 1e-12:
        return [0.0 for _ in vals]
    out = [x / norm for x in vals]
    first = next((x for x in out if abs(x) > 1e-9), 0.0)
    if first < 0:
        out = [-x for x in out]
    return [round(x, 10) for x in out]


def _as_vectors(value: Any) -> List[List[float]]:
    if not isinstance(value, list):
        return []
    out: List[List[float]] = []
    for row in value:
        if isinstance(row, list):
            v = _normalize_vector(row)
            if v:
                out.append(v)
    return out


def _as_values(value: Any) -> List[float]:
    if not isinstance(value, list):
        return []
    return [_safe_float(x, 0.0) for x in value]


def _cosine_abs(a: List[float], b: List[float]) -> float:
    n = min(len(a), len(b))
    if n <= 0:
        return 0.0
    aa = _normalize_vector(a[:n])
    bb = _normalize_vector(b[:n])
    return _clamp(abs(sum(aa[i] * bb[i] for i in range(n))))


def _eigen_similarity(a: float, b: float) -> float:
    denom = max(1.0, abs(a), abs(b))
    return _clamp(1.0 - abs(a - b) / denom)


def _status_ok(payload: Mapping[str, Any], status_key: str, bool_key: str) -> bool:
    if bool(payload.get(bool_key)):
        return True
    st = str(payload.get(status_key, "")).upper()
    return any(tok in st for tok in ["EXTRACTED", "ALIGNED", "CERTIFIED", "BUILT", "CONFIRMED"])


def _synthetic_payloads(inputs: Mapping[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    if inputs.get("aligned") or inputs.get("all_component_modes_available"):
        basis = [[0.5, 0.5, 0.5, 0.5], [0.5, 0.5, -0.5, -0.5], [0.5, -0.5, 0.5, -0.5], [0.5, -0.5, -0.5, 0.5]]
        return (
            {"graph_laplacian_mode_extractor_status": "GRAPH_LAPLACIAN_MODES_EXTRACTED", "graph_laplacian_modes_extracted": True, "eigenvalues": [0.0, 0.5, 0.5, 1.0], "eigenvectors": basis, "extraction_score": 0.94},
            {"markov_transition_mode_extractor_status": "MARKOV_TRANSITION_MODES_EXTRACTED", "markov_transition_modes_extracted": True, "transition_eigenvalues": [1.0, 0.5, 0.5, 0.0], "transition_eigenvectors": basis, "extraction_score": 0.93},
            {"possibility_gradient_mode_extractor_status": "POSSIBILITY_GRADIENT_MODES_EXTRACTED", "possibility_gradient_modes_extracted": True, "possibility_eigenvalues": [0.0, 0.45, 0.55, 1.0], "possibility_eigenvectors": basis, "extraction_score": 0.92},
            {"spectral_mode_extractor_status": "SPECTRAL_MODES_EXTRACTED", "spectral_modes_extracted": True, "fused_eigenvalues": [0.0, 0.483, 0.517, 0.67], "fused_eigenvectors": basis, "component_alignment_score": 0.98, "spectral_fusion_score": 0.94, "fusion_coherence_score": 0.94},
        )
    if inputs:
        return dict(inputs.get("ai2", {})), dict(inputs.get("ai3", {})), dict(inputs.get("ai4", {})), dict(inputs.get("ai5", {}))
    return {}, {}, {}, {}


class CommonModeAlignmentEngine:
    """AI6 — align common formal-functional modes across AI2, AI3, AI4, and AI5."""

    primitive = "COMMON_MODE_ALIGNMENT_ENGINE"
    expected_status = "COMMON_SPECTRAL_MODES_ALIGNED"
    insufficient_status = "COMMON_SPECTRAL_MODES_INSUFFICIENT"
    next_recommended_module = "common_mode_score_calculator"
    threshold = 0.72

    def _source_payloads(self, inputs: Optional[Mapping[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        if inputs is not None:
            return _synthetic_payloads(inputs)
        ai2 = _try_step("ontology.graph_laplacian_mode_extractor", "GraphLaplacianModeExtractor") or _load_json(AI2_JSON)
        ai3 = _try_step("ontology.markov_transition_mode_extractor", "MarkovTransitionModeExtractor") or _load_json(AI3_JSON)
        ai4 = _try_step("ontology.possibility_gradient_mode_extractor", "PossibilityGradientModeExtractor") or _load_json(AI4_JSON)
        ai5 = _try_step("ontology.spectral_mode_extractor", "SpectralModeExtractor") or _load_json(AI5_JSON)
        return ai2, ai3, ai4, ai5

    def _alignment_payload(self, ai2: Mapping[str, Any], ai3: Mapping[str, Any], ai4: Mapping[str, Any], ai5: Mapping[str, Any]) -> Dict[str, Any]:
        graph_vals = _as_values(ai2.get("eigenvalues"))
        markov_vals = [max(0.0, 1.0 - abs(v)) for v in _as_values(ai3.get("transition_eigenvalues"))]
        poss_vals = _as_values(ai4.get("possibility_eigenvalues"))
        fused_vals = _as_values(ai5.get("fused_eigenvalues"))
        graph_vecs = _as_vectors(ai2.get("eigenvectors"))
        markov_vecs = _as_vectors(ai3.get("transition_eigenvectors"))
        poss_vecs = _as_vectors(ai4.get("possibility_eigenvectors"))
        fused_vecs = _as_vectors(ai5.get("fused_eigenvectors"))
        mode_count = min([len(x) for x in [graph_vals, markov_vals, poss_vals, fused_vals, graph_vecs, markov_vecs, poss_vecs, fused_vecs] if x] or [0])
        aligned_modes: List[Dict[str, Any]] = []
        vector_scores: List[float] = []
        eigen_scores: List[float] = []
        overlap_flags: List[float] = []
        for i in range(mode_count):
            vector_score = _mean([
                _cosine_abs(graph_vecs[i], markov_vecs[i]), _cosine_abs(graph_vecs[i], poss_vecs[i]),
                _cosine_abs(markov_vecs[i], poss_vecs[i]), _cosine_abs(fused_vecs[i], graph_vecs[i]),
                _cosine_abs(fused_vecs[i], markov_vecs[i]), _cosine_abs(fused_vecs[i], poss_vecs[i]),
            ])
            component_mean = _mean([graph_vals[i], markov_vals[i], poss_vals[i]])
            eigen_score = _mean([
                _eigen_similarity(graph_vals[i], markov_vals[i]), _eigen_similarity(graph_vals[i], poss_vals[i]),
                _eigen_similarity(markov_vals[i], poss_vals[i]), _eigen_similarity(fused_vals[i], component_mean),
            ])
            combined = _mean([vector_score, eigen_score, _clamp(ai5.get("component_alignment_score", 0.0), 0.75)])
            aligned = combined >= 0.70
            vector_scores.append(vector_score); eigen_scores.append(eigen_score); overlap_flags.append(1.0 if aligned else 0.0)
            aligned_modes.append({
                "common_mode_id": f"AI6_COMMON_MODE_{i:02d}", "rank": i, "aligned": aligned,
                "graph_mode_id": f"AI2_GRAPH_MODE_{i:02d}", "markov_mode_id": f"AI3_MARKOV_MODE_{i:02d}",
                "possibility_mode_id": f"AI4_POSSIBILITY_MODE_{i:02d}", "fused_mode_id": f"AI5_FUSED_MODE_{i:02d}",
                "graph_eigenvalue": round(graph_vals[i], 10), "markov_spectral_distance": round(markov_vals[i], 10),
                "possibility_eigenvalue": round(poss_vals[i], 10), "fused_eigenvalue": round(fused_vals[i], 10),
                "vector_alignment_score": round(vector_score, 10), "eigenvalue_alignment_score": round(eigen_score, 10),
                "common_mode_alignment_score": round(combined, 10), "functional_label": "common_formal_spectral_mode",
                "epistemic_status": "formal_functional_candidate_only",
            })
        common_mode_count = sum(1 for m in aligned_modes if m.get("aligned"))
        mode_overlap_score = _mean(overlap_flags)
        vector_alignment_score = _mean(vector_scores)
        eigen_alignment_score = _mean(eigen_scores)
        cross_component_consistency_score = _mean([vector_alignment_score, eigen_alignment_score, _clamp(ai5.get("component_alignment_score", ai5.get("component_fusion_coherence_score", 0.0)))])
        alignment_score = _mean([mode_overlap_score, vector_alignment_score, eigen_alignment_score, cross_component_consistency_score])
        alignment_confidence = _mean([alignment_score, 1.0 if common_mode_count >= 3 else common_mode_count / 3.0, _clamp(ai5.get("spectral_fusion_score", ai5.get("fusion_coherence_score", 0.0)))])
        return {"aligned_modes": aligned_modes, "common_mode_count": common_mode_count, "candidate_mode_count": mode_count, "alignment_score": alignment_score, "cross_component_consistency_score": cross_component_consistency_score, "mode_overlap_score": mode_overlap_score, "alignment_confidence": alignment_confidence, "vector_alignment_score": vector_alignment_score, "eigenvalue_alignment_score": eigen_alignment_score}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        ai2, ai3, ai4, ai5 = self._source_payloads(inputs)
        payload = self._alignment_payload(ai2, ai3, ai4, ai5)
        component_availability = {
            "ai2_graph_laplacian_modes": _status_ok(ai2, "graph_laplacian_mode_extractor_status", "graph_laplacian_modes_extracted"),
            "ai3_markov_transition_modes": _status_ok(ai3, "markov_transition_mode_extractor_status", "markov_transition_modes_extracted"),
            "ai4_possibility_gradient_modes": _status_ok(ai4, "possibility_gradient_mode_extractor_status", "possibility_gradient_modes_extracted"),
            "ai5_spectral_modes": _status_ok(ai5, "spectral_mode_extractor_status", "spectral_modes_extracted"),
        }
        component_availability_score = _mean([1.0 if v else 0.0 for v in component_availability.values()])
        alignment_readiness_score = _mean([component_availability_score, payload["alignment_score"], payload["cross_component_consistency_score"], payload["mode_overlap_score"], payload["alignment_confidence"]])
        aligned = bool(alignment_readiness_score >= self.threshold and payload["common_mode_count"] >= 3 and all(component_availability.values()))
        status = self.expected_status if aligned else self.insufficient_status
        result: Dict[str, Any] = {
            "primitive": self.primitive, "axis": "AI", "step_id": "AI6", "timestamp_utc": _now(),
            "common_mode_alignment_engine_status": status, "common_spectral_modes_aligned": aligned, "common_modes_aligned": aligned,
            "component_availability": component_availability, "component_availability_score": component_availability_score,
            "common_mode_count": payload["common_mode_count"], "candidate_mode_count": payload["candidate_mode_count"],
            "aligned_modes": payload["aligned_modes"], "common_spectral_modes": [m for m in payload["aligned_modes"] if m.get("aligned")],
            "common_modes": [m for m in payload["aligned_modes"] if m.get("aligned")],
            "alignment_matrix": [
                {
                    "common_mode_id": m.get("common_mode_id"),
                    "graph_markov_possibility_vector_alignment": m.get("vector_alignment_score", 0.0),
                    "graph_markov_possibility_eigen_alignment": m.get("eigenvalue_alignment_score", 0.0),
                    "common_mode_alignment_score": m.get("common_mode_alignment_score", 0.0),
                    "aligned": bool(m.get("aligned")),
                }
                for m in payload["aligned_modes"]
            ],
            "component_sources": {
                "AI2": "graph_laplacian_mode_extractor",
                "AI3": "markov_transition_mode_extractor",
                "AI4": "possibility_gradient_mode_extractor",
                "AI5": "spectral_mode_extractor",
            },
            "epistemic_status": "functional_only",
            "alignment_score": payload["alignment_score"], "cross_component_consistency_score": payload["cross_component_consistency_score"],
            "mode_overlap_score": payload["mode_overlap_score"], "alignment_confidence": payload["alignment_confidence"],
            "vector_alignment_score": payload["vector_alignment_score"], "eigenvalue_alignment_score": payload["eigenvalue_alignment_score"],
            "alignment_readiness_score": alignment_readiness_score, "certification_score": alignment_readiness_score,
            "source_statuses": {"ai2": ai2.get("graph_laplacian_mode_extractor_status", ""), "ai3": ai3.get("markov_transition_mode_extractor_status", ""), "ai4": ai4.get("possibility_gradient_mode_extractor_status", ""), "ai5": ai5.get("spectral_mode_extractor_status", "")},
            "next_recommended_module": self.next_recommended_module,
            "functional_conclusion_only": True, "phenomenology_undetermined": True, "consciousness_proven": False, "qualia_proven": False, "subjectivity_proven": False,
            "epistemic_guard": "strictly functional common spectral mode alignment; no consciousness, qualia, subjectivity, or phenomenology claim",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"common_mode_alignment_engine_{stamp}"
        json_path = OUT_DIR / f"{base}.json"; md_path = OUT_DIR / f"{base}.md"; prom_path = OUT_DIR / f"{base}.prom"
        latest_json = OUT_DIR / "latest_common_mode_alignment_engine.json"; latest_md = OUT_DIR / "latest_common_mode_alignment_engine.md"; latest_prom = OUT_DIR / "latest_common_mode_alignment_engine.prom"
        history = OUT_DIR / "common_mode_alignment_engine_history.jsonl"
        text = json.dumps(result, indent=2, ensure_ascii=False)
        json_path.write_text(text, encoding="utf-8"); latest_json.write_text(text, encoding="utf-8")
        with history.open("a", encoding="utf-8") as f: f.write(json.dumps(result, ensure_ascii=False) + "\n")
        md = "\n".join(["# AI6 — Common Mode Alignment Engine", "", "Functional reconstruction: L_graph + L_markov + L_Π + L_RF spectral fusion → common robust formal modes.", "", f"Status: {result.get('common_mode_alignment_engine_status')}", f"Common spectral modes aligned: {result.get('common_spectral_modes_aligned')}", f"Common mode count: {result.get('common_mode_count')}", f"Candidate mode count: {result.get('candidate_mode_count')}", f"Alignment score: {result.get('alignment_score')}", f"Cross-component consistency score: {result.get('cross_component_consistency_score')}", f"Mode overlap score: {result.get('mode_overlap_score')}", f"Alignment confidence: {result.get('alignment_confidence')}", "", "Strictly functional conclusion only.", "Phenomenology undetermined.", "No consciousness, qualia, or subjectivity claim."]) + "\n"
        md_path.write_text(md, encoding="utf-8"); latest_md.write_text(md, encoding="utf-8")
        aligned = 1 if result.get("common_spectral_modes_aligned") else 0
        prom = "\n".join([f"oce_ai6_common_spectral_modes_aligned {aligned}", f"oce_ai6_common_mode_count {result.get('common_mode_count', 0)}", f"oce_ai6_candidate_mode_count {result.get('candidate_mode_count', 0)}", f"oce_ai6_alignment_score {result.get('alignment_score', 0.0)}", f"oce_ai6_cross_component_consistency_score {result.get('cross_component_consistency_score', 0.0)}", f"oce_ai6_mode_overlap_score {result.get('mode_overlap_score', 0.0)}", f"oce_ai6_alignment_confidence {result.get('alignment_confidence', 0.0)}", f"oce_ai6_vector_alignment_score {result.get('vector_alignment_score', 0.0)}", f"oce_ai6_eigenvalue_alignment_score {result.get('eigenvalue_alignment_score', 0.0)}", f"oce_ai6_alignment_readiness_score {result.get('alignment_readiness_score', 0.0)}", "oce_ai6_consciousness_proven 0.0", "oce_ai6_qualia_proven 0.0", "oce_ai6_subjectivity_proven 0.0"]) + "\n"
        prom_path.write_text(prom, encoding="utf-8"); latest_prom.write_text(prom, encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path), "latest_json": str(latest_json), "latest_markdown": str(latest_md), "latest_prometheus": str(latest_prom), "history": str(history)}
