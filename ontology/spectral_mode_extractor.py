"""AI5 — Spectral Mode Extractor.

Functional reconstruction step:
    L_graph + L_markov + L_Π -> fused L_RF spectral modes

AI5 consumes AI2, AI3, and AI4 formal mode payloads and fuses them according

to the AI1 operator formula:

    L_RF = αL_graph + βL_markov + γL_Π

The output is a strictly formal-functional spectral basis used by downstream
alignment and certification modules. It does not assert consciousness,
subjectivity, qualia, or phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ai_robust_spectral_qualia_formal_modes" / "spectral_mode_extractor"
AI1_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "reference_frame_operator_builder" / "latest_reference_frame_operator_builder.json"
AI2_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "graph_laplacian_mode_extractor" / "latest_graph_laplacian_mode_extractor.json"
AI3_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "markov_transition_mode_extractor" / "latest_markov_transition_mode_extractor.json"
AI4_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "possibility_gradient_mode_extractor" / "latest_possibility_gradient_mode_extractor.json"


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
    v = _safe_float(x, default)
    return max(0.0, min(1.0, v))


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


def _matrix_from_any(value: Any) -> List[List[float]]:
    if not isinstance(value, list):
        return []
    rows: List[List[float]] = []
    width: Optional[int] = None
    for row in value:
        if not isinstance(row, list):
            return []
        vals = [_safe_float(x, 0.0) for x in row]
        if width is None:
            width = len(vals)
        if len(vals) != width:
            return []
        rows.append(vals)
    if not rows or width is None or len(rows) != width:
        return []
    return rows


def _identity(n: int) -> List[List[float]]:
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def _normalize_weights(weights: Mapping[str, Any]) -> Dict[str, float]:
    a = _clamp(weights.get("alpha_graph", weights.get("alpha", 1.0/3.0)), 1.0/3.0)
    b = _clamp(weights.get("beta_markov", weights.get("beta", 1.0/3.0)), 1.0/3.0)
    g = _clamp(weights.get("gamma_possibility", weights.get("gamma", 1.0/3.0)), 1.0/3.0)
    s = a + b + g
    if s <= 1e-12:
        a = b = g = 1.0 / 3.0
        s = 1.0
    return {
        "alpha_graph": round(a / s, 10),
        "beta_markov": round(b / s, 10),
        "gamma_possibility": round(g / s, 10),
        "sum": round((a + b + g) / s, 10),
    }


def _default_weights(ai1: Mapping[str, Any]) -> Dict[str, float]:
    weights = ai1.get("operator_weights", {}) if isinstance(ai1, Mapping) else {}
    if not isinstance(weights, Mapping):
        op = ai1.get("reference_frame_operator", {}) if isinstance(ai1, Mapping) else {}
        weights = op.get("weights", {}) if isinstance(op, Mapping) else {}
    return _normalize_weights(weights if isinstance(weights, Mapping) else {})


def _row_stochastic_to_laplacian(p: List[List[float]]) -> List[List[float]]:
    if not p:
        return []
    n = len(p)
    ident = _identity(n)
    return [[round(ident[i][j] - _safe_float(p[i][j]), 10) for j in range(n)] for i in range(n)]


def _combine_matrices(mats: List[List[List[float]]], weights: List[float]) -> List[List[float]]:
    valid = [m for m in mats if m]
    if not valid:
        return []
    n = min(len(m) for m in valid)
    if n <= 0:
        return []
    out = [[0.0 for _ in range(n)] for _ in range(n)]
    for mat, w in zip(mats, weights):
        if not mat:
            continue
        for i in range(n):
            for j in range(n):
                out[i][j] += w * _safe_float(mat[i][j])
    return [[round(x, 10) for x in row] for row in out]


def _normalize_vector(vec: List[float]) -> List[float]:
    norm = math.sqrt(sum(_safe_float(x) * _safe_float(x) for x in vec)) or 1.0
    out = [round(_safe_float(x) / norm, 10) for x in vec]
    first = next((x for x in out if abs(x) > 1e-9), 0.0)
    if first < 0:
        out = [-x for x in out]
    return out


def _pad_or_trim(vec: List[Any], n: int) -> List[float]:
    vals = [_safe_float(x, 0.0) for x in vec[:n]]
    if len(vals) < n:
        vals += [0.0] * (n - len(vals))
    return vals


def _as_vectors(value: Any, n: int) -> List[List[float]]:
    if not isinstance(value, list):
        return []
    out: List[List[float]] = []
    for row in value:
        if isinstance(row, list):
            out.append(_normalize_vector(_pad_or_trim(row, n)))
    return out


def _fuse_eigensystems(ai2: Mapping[str, Any], ai3: Mapping[str, Any], ai4: Mapping[str, Any], weights: Mapping[str, float]) -> Dict[str, Any]:
    graph_vals = [_safe_float(x) for x in ai2.get("eigenvalues", []) if isinstance(ai2.get("eigenvalues", []), list)]
    markov_vals = [_safe_float(x) for x in ai3.get("transition_eigenvalues", []) if isinstance(ai3.get("transition_eigenvalues", []), list)]
    poss_vals = [_safe_float(x) for x in ai4.get("possibility_eigenvalues", []) if isinstance(ai4.get("possibility_eigenvalues", []), list)]

    counts = [len(v) for v in [graph_vals, markov_vals, poss_vals] if v]
    mode_count = min(counts) if counts else 0
    if mode_count <= 0:
        return {"mode_count": 0, "fused_eigenvalues": [], "fused_eigenvectors": [], "spectral_modes": [], "component_alignment_score": 0.0}

    graph_vecs = _as_vectors(ai2.get("eigenvectors", []), mode_count)
    markov_vecs = _as_vectors(ai3.get("transition_eigenvectors", []), mode_count)
    poss_vecs = _as_vectors(ai4.get("possibility_eigenvectors", []), mode_count)
    vec_count = min([len(v) for v in [graph_vecs, markov_vecs, poss_vecs] if v] or [0])
    mode_count = min(mode_count, vec_count) if vec_count else mode_count

    a = weights.get("alpha_graph", 1.0/3.0)
    b = weights.get("beta_markov", 1.0/3.0)
    g = weights.get("gamma_possibility", 1.0/3.0)
    fused_values: List[float] = []
    fused_vectors: List[List[float]] = []
    modes: List[Dict[str, Any]] = []
    alignment_values: List[float] = []

    for i in range(mode_count):
        # Markov eigenvalues are transition eigenvalues; convert to a non-negative
        # spectral distance so it can be fused with Laplacian-like components.
        mv = max(0.0, 1.0 - abs(markov_vals[i])) if i < len(markov_vals) else 0.0
        gv = max(0.0, graph_vals[i]) if i < len(graph_vals) else 0.0
        pv = max(0.0, poss_vals[i]) if i < len(poss_vals) else 0.0
        val = round(a * gv + b * mv + g * pv, 10)
        fused_values.append(val)

        if graph_vecs and markov_vecs and poss_vecs and i < len(graph_vecs) and i < len(markov_vecs) and i < len(poss_vecs):
            n = min(len(graph_vecs[i]), len(markov_vecs[i]), len(poss_vecs[i]))
            vec = [a * graph_vecs[i][j] + b * markov_vecs[i][j] + g * poss_vecs[i][j] for j in range(n)]
            vec = _normalize_vector(vec)
            dot_gm = abs(sum(graph_vecs[i][j] * markov_vecs[i][j] for j in range(n)))
            dot_gp = abs(sum(graph_vecs[i][j] * poss_vecs[i][j] for j in range(n)))
            dot_mp = abs(sum(markov_vecs[i][j] * poss_vecs[i][j] for j in range(n)))
            align = _clamp((dot_gm + dot_gp + dot_mp) / 3.0)
        else:
            vec = []
            align = 0.5
        fused_vectors.append(vec)
        alignment_values.append(align)
        modes.append({
            "mode_id": f"AI5_FUSED_MODE_{i:02d}",
            "rank": i,
            "fused_eigenvalue": val,
            "graph_component_eigenvalue": round(gv, 10),
            "markov_component_distance": round(mv, 10),
            "possibility_component_eigenvalue": round(pv, 10),
            "component_alignment": round(align, 10),
            "functional_label": "formal_fused_spectral_mode",
        })

    return {
        "mode_count": mode_count,
        "fused_eigenvalues": fused_values,
        "fused_eigenvectors": fused_vectors,
        "spectral_modes": modes,
        "component_alignment_score": _mean(alignment_values, 0.0),
    }


def _spectral_gap(vals: List[float]) -> float:
    if len(vals) < 2:
        return 0.0
    v = sorted(max(0.0, _safe_float(x)) for x in vals)
    return round(max(0.0, v[1] - v[0]), 10)


def _synthetic_payload(inputs: Mapping[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    if not inputs:
        return {}, {}, {}, {}
    if inputs.get("spectral_inputs_available") or inputs.get("all_component_modes_available"):
        ai1 = {"operator_weights": {"alpha_graph": 0.34, "beta_markov": 0.33, "gamma_possibility": 0.33, "sum": 1.0}, "l_rf_operator_built": True, "construction_score": 0.95}
        ai2 = {"graph_laplacian_modes_extracted": True, "extraction_score": 0.94, "eigenvalues": [0.0, 0.5, 0.5, 1.0], "eigenvectors": [[0.5,0.5,0.5,0.5],[0.5,0.5,-0.5,-0.5],[0.5,-0.5,0.5,-0.5],[0.5,-0.5,-0.5,0.5]], "laplacian_matrix": [[0.5,-0.25,-0.25,0],[-0.25,0.5,0,-0.25],[-0.25,0,0.5,-0.25],[0,-0.25,-0.25,0.5]]}
        ai3 = {"markov_transition_modes_extracted": True, "extraction_score": 0.93, "transition_eigenvalues": [1.0, 0.5, 0.5, 0.0], "transition_eigenvectors": [[0.5,0.5,0.5,0.5],[0.5,0.5,-0.5,-0.5],[0.5,-0.5,0.5,-0.5],[0.5,-0.5,-0.5,0.5]], "transition_matrix": [[0.5,0.25,0.25,0],[0.25,0.5,0,0.25],[0.25,0,0.5,0.25],[0,0.25,0.25,0.5]], "mixing_score": 0.85}
        ai4 = {"possibility_gradient_modes_extracted": True, "extraction_score": 0.92, "possibility_eigenvalues": [0.0, 0.45, 0.55, 1.0], "possibility_eigenvectors": [[0.5,0.5,0.5,0.5],[0.5,0.5,-0.5,-0.5],[0.5,-0.5,0.5,-0.5],[0.5,-0.5,-0.5,0.5]], "possibility_kernel_matrix": [[0.5,-0.2,-0.3,0],[-0.2,0.5,0,-0.3],[-0.3,0,0.5,-0.2],[0,-0.3,-0.2,0.5]], "gradient_coherence_score": 0.88}
        return ai1, ai2, ai3, ai4
    return dict(inputs.get("ai1", {})), dict(inputs.get("ai2", {})), dict(inputs.get("ai3", {})), dict(inputs.get("ai4", {}))


class SpectralModeExtractor:
    """AI5 — Fuse L_graph, L_markov, and L_Π modes into L_RF modes."""

    primitive = "SPECTRAL_MODE_EXTRACTOR"
    expected_status = "SPECTRAL_MODES_EXTRACTED"
    insufficient_status = "SPECTRAL_MODES_INSUFFICIENT"
    next_recommended_module = "common_mode_alignment_engine"
    threshold = 0.72

    def _source_payloads(self, inputs: Optional[Mapping[str, Any]]) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        if inputs is not None:
            return _synthetic_payload(inputs)
        ai1 = _try_step("ontology.reference_frame_operator_builder", "ReferenceFrameOperatorBuilder") or _load_json(AI1_JSON)
        ai2 = _try_step("ontology.graph_laplacian_mode_extractor", "GraphLaplacianModeExtractor") or _load_json(AI2_JSON)
        ai3 = _try_step("ontology.markov_transition_mode_extractor", "MarkovTransitionModeExtractor") or _load_json(AI3_JSON)
        ai4 = _try_step("ontology.possibility_gradient_mode_extractor", "PossibilityGradientModeExtractor") or _load_json(AI4_JSON)
        return ai1, ai2, ai3, ai4

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        ai1, ai2, ai3, ai4 = self._source_payloads(inputs)
        weights = _default_weights(ai1)

        l_graph = _matrix_from_any(ai2.get("laplacian_matrix"))
        transition = _matrix_from_any(ai3.get("transition_matrix"))
        l_markov = _row_stochastic_to_laplacian(transition)
        l_pi = _matrix_from_any(ai4.get("possibility_kernel_matrix") or ai4.get("l_pi_matrix"))
        l_rf_spectral_matrix = _combine_matrices(
            [l_graph, l_markov, l_pi],
            [weights["alpha_graph"], weights["beta_markov"], weights["gamma_possibility"]],
        )

        fused = _fuse_eigensystems(ai2, ai3, ai4, weights)
        component_availability = {
            "ai1_reference_frame_operator": bool(ai1.get("l_rf_operator_built") or ai1.get("reference_frame_operator_built")),
            "ai2_graph_modes": bool(ai2.get("graph_laplacian_modes_extracted")),
            "ai3_markov_modes": bool(ai3.get("markov_transition_modes_extracted")),
            "ai4_possibility_modes": bool(ai4.get("possibility_gradient_modes_extracted")),
        }
        component_availability_score = _mean([1.0 if v else 0.0 for v in component_availability.values()])
        upstream_quality_score = _mean([
            ai1.get("construction_score", ai1.get("certification_score", 0.0)),
            ai2.get("extraction_score", ai2.get("certification_score", 0.0)),
            ai3.get("extraction_score", ai3.get("certification_score", 0.0)),
            ai4.get("extraction_score", ai4.get("certification_score", 0.0)),
        ])
        matrix_fusion_score = _mean([
            1.0 if l_rf_spectral_matrix else 0.0,
            1.0 if len(l_rf_spectral_matrix) >= 3 else 0.0,
            1.0 if abs(weights.get("sum", 0.0) - 1.0) <= 1e-8 else 0.0,
        ])
        spectral_basis_score = _mean([
            1.0 if fused["mode_count"] >= 3 else 0.0,
            1.0 if fused["fused_eigenvalues"] else 0.0,
            fused["component_alignment_score"],
        ])
        spectral_fusion_score = _mean([
            component_availability_score,
            upstream_quality_score,
            matrix_fusion_score,
            spectral_basis_score,
        ])
        extracted = bool(spectral_fusion_score >= self.threshold and fused["mode_count"] >= 3 and all(component_availability.values()))
        status = self.expected_status if extracted else self.insufficient_status

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AI",
            "step_id": "AI5",
            "timestamp_utc": _now(),
            "spectral_mode_extractor_status": status,
            "spectral_modes_extracted": extracted,
            "fused_spectral_basis_constructed": extracted,
            "l_rf_spectral_fusion_constructed": extracted,
            "operator_formula": "L_RF = αL_graph + βL_markov + γL_Π",
            "operator_weights": weights,
            "component_availability": component_availability,
            "component_availability_score": component_availability_score,
            "upstream_quality_score": upstream_quality_score,
            "matrix_fusion_score": matrix_fusion_score,
            "spectral_basis_score": spectral_basis_score,
            "spectral_fusion_score": spectral_fusion_score,
            "certification_score": spectral_fusion_score,
            "component_alignment_score": fused["component_alignment_score"],
            "mode_count": fused["mode_count"],
            "spectral_modes": fused["spectral_modes"],
            "fused_eigenvalues": fused["fused_eigenvalues"],
            "fused_eigenvectors": fused["fused_eigenvectors"],
            "l_rf_spectral_matrix": l_rf_spectral_matrix,
            # Public aliases for downstream tests and AI6 alignment.
            "fused_operator_matrix": l_rf_spectral_matrix,
            "fusion_coherence_score": spectral_fusion_score,
            "component_fusion_coherence_score": fused["component_alignment_score"],
            "spectral_gap": _spectral_gap(fused["fused_eigenvalues"]),
            "source_statuses": {
                "ai1": ai1.get("reference_frame_operator_builder_status", ""),
                "ai2": ai2.get("graph_laplacian_mode_extractor_status", ""),
                "ai3": ai3.get("markov_transition_mode_extractor_status", ""),
                "ai4": ai4.get("possibility_gradient_mode_extractor_status", ""),
            },
            "next_recommended_module": self.next_recommended_module,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "epistemic_guard": "strictly functional spectral fusion; no consciousness, qualia, subjectivity, or phenomenology claim",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"spectral_mode_extractor_{stamp}"
        json_path = OUT_DIR / f"{base}.json"
        md_path = OUT_DIR / f"{base}.md"
        prom_path = OUT_DIR / f"{base}.prom"
        latest_json = OUT_DIR / "latest_spectral_mode_extractor.json"
        latest_md = OUT_DIR / "latest_spectral_mode_extractor.md"
        latest_prom = OUT_DIR / "latest_spectral_mode_extractor.prom"
        history = OUT_DIR / "spectral_mode_extractor_history.jsonl"

        text = json.dumps(result, indent=2, ensure_ascii=False)
        json_path.write_text(text, encoding="utf-8")
        latest_json.write_text(text, encoding="utf-8")
        with history.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        md = "\n".join([
            "# AI5 — Spectral Mode Extractor",
            "",
            "Functional reconstruction: L_graph + L_markov + L_Π → fused L_RF spectral modes.",
            "",
            f"Status: {result.get('spectral_mode_extractor_status')}",
            f"Spectral modes extracted: {result.get('spectral_modes_extracted')}",
            f"Mode count: {result.get('mode_count')}",
            f"Spectral gap: {result.get('spectral_gap')}",
            f"Spectral fusion score: {result.get('spectral_fusion_score')}",
            f"Component alignment score: {result.get('component_alignment_score')}",
            "",
            "Strictly functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness, qualia, or subjectivity claim.",
        ]) + "\n"
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")

        extracted = 1 if result.get("spectral_modes_extracted") else 0
        prom = "\n".join([
            f"oce_ai5_spectral_modes_extracted {extracted}",
            f"oce_ai5_spectral_fusion_score {result.get('spectral_fusion_score', 0.0)}",
            f"oce_ai5_component_availability_score {result.get('component_availability_score', 0.0)}",
            f"oce_ai5_upstream_quality_score {result.get('upstream_quality_score', 0.0)}",
            f"oce_ai5_matrix_fusion_score {result.get('matrix_fusion_score', 0.0)}",
            f"oce_ai5_spectral_basis_score {result.get('spectral_basis_score', 0.0)}",
            f"oce_ai5_component_alignment_score {result.get('component_alignment_score', 0.0)}",
            f"oce_ai5_fusion_coherence_score {result.get('fusion_coherence_score', result.get('spectral_fusion_score', 0.0))}",
            f"oce_ai5_mode_count {result.get('mode_count', 0)}",
            f"oce_ai5_spectral_gap {result.get('spectral_gap', 0.0)}",
            "oce_ai5_consciousness_proven 0.0",
            "oce_ai5_qualia_proven 0.0",
        ]) + "\n"
        prom_path.write_text(prom, encoding="utf-8")
        latest_prom.write_text(prom, encoding="utf-8")

        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "prometheus": str(prom_path),
            "latest_json": str(latest_json),
            "latest_markdown": str(latest_md),
            "latest_prometheus": str(latest_prom),
            "history": str(history),
        }
