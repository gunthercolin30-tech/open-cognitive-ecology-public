"""AI3 — Markov Transition Mode Extractor.

Functional reconstruction step:
    L_RF -> Markov transition spectral modes

AI3 consumes the AI1 reference-frame operator payload and extracts the modes of
L_markov, the transition/regime-flow component of:

    L_RF = αL_graph + βL_markov + γL_Π

The module reconstructs a row-stochastic transition kernel P from L_markov
when needed, estimates stationary flow, and computes deterministic transition
modes using a small built-in eigensolver for symmetrized transition geometry.

Epistemic guard: formal mode labels are strictly functional. This module never
asserts consciousness, subjectivity, qualia, or phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ai_robust_spectral_qualia_formal_modes" / "markov_transition_mode_extractor"
AI1_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "reference_frame_operator_builder" / "latest_reference_frame_operator_builder.json"
AI2_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "graph_laplacian_mode_extractor" / "latest_graph_laplacian_mode_extractor.json"


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


def _try_ai1() -> Dict[str, Any]:
    try:
        mod = import_module("ontology.reference_frame_operator_builder")
        cls = getattr(mod, "ReferenceFrameOperatorBuilder")
        out = cls().step(persist=False)
        return out if isinstance(out, dict) else {}
    except Exception:
        return {}


def _try_ai2() -> Dict[str, Any]:
    try:
        mod = import_module("ontology.graph_laplacian_mode_extractor")
        cls = getattr(mod, "GraphLaplacianModeExtractor")
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


def _row_sums(matrix: List[List[float]]) -> List[float]:
    return [sum(row) for row in matrix]


def _is_row_stochastic(matrix: List[List[float]], tol: float = 1e-8) -> bool:
    if not matrix:
        return False
    for row in matrix:
        if any(x < -tol or x > 1.0 + tol for x in row):
            return False
        if abs(sum(row) - 1.0) > tol:
            return False
    return True


def _transition_from_l_markov(l_markov: List[List[float]]) -> List[List[float]]:
    """Convert L_markov ≈ I-P into a row-stochastic transition kernel P."""
    n = len(l_markov)
    if n == 0:
        return []
    raw = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                raw[i][j] = max(0.0, 1.0 - _safe_float(l_markov[i][i], 1.0))
            else:
                raw[i][j] = max(0.0, -_safe_float(l_markov[i][j], 0.0))
        s = sum(raw[i])
        if s <= 1e-12:
            raw[i][i] = 1.0
            s = 1.0
        raw[i] = [round(x / s, 10) for x in raw[i]]
    return raw


def _l_markov_from_transition(p: List[List[float]]) -> List[List[float]]:
    n = len(p)
    return [[round((1.0 if i == j else 0.0) - p[i][j], 10) for j in range(n)] for i in range(n)]


def _symmetrize(matrix: List[List[float]]) -> List[List[float]]:
    n = len(matrix)
    return [[0.5 * (matrix[i][j] + matrix[j][i]) for j in range(n)] for i in range(n)]


def _jacobi_eigen_symmetric(matrix: List[List[float]], max_iter: int = 160, tol: float = 1e-10) -> Tuple[List[float], List[List[float]]]:
    """Deterministic Jacobi eigensolver for small symmetric matrices."""
    n = len(matrix)
    if n == 0:
        return [], []
    a = [[float(matrix[i][j]) for j in range(n)] for i in range(n)]
    v = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for _ in range(max_iter):
        p, q, max_off = 0, 1 if n > 1 else 0, 0.0
        for i in range(n):
            for j in range(i + 1, n):
                val = abs(a[i][j])
                if val > max_off:
                    max_off, p, q = val, i, j
        if max_off < tol or n == 1:
            break
        if abs(a[p][p] - a[q][q]) < tol:
            angle = math.pi / 4.0
        else:
            angle = 0.5 * math.atan2(2.0 * a[p][q], a[q][q] - a[p][p])
        c, s = math.cos(angle), math.sin(angle)
        app = c*c*a[p][p] - 2*s*c*a[p][q] + s*s*a[q][q]
        aqq = s*s*a[p][p] + 2*s*c*a[p][q] + c*c*a[q][q]
        a[p][q] = a[q][p] = 0.0
        a[p][p], a[q][q] = app, aqq
        for k in range(n):
            if k != p and k != q:
                akp, akq = a[k][p], a[k][q]
                a[k][p] = a[p][k] = c*akp - s*akq
                a[k][q] = a[q][k] = s*akp + c*akq
        for k in range(n):
            vkp, vkq = v[k][p], v[k][q]
            v[k][p] = c*vkp - s*vkq
            v[k][q] = s*vkp + c*vkq
    pairs = []
    for col in range(n):
        vec = [v[row][col] for row in range(n)]
        norm = math.sqrt(sum(x*x for x in vec)) or 1.0
        vec = [round(x / norm, 10) for x in vec]
        first = next((x for x in vec if abs(x) > 1e-9), 0.0)
        if first < 0:
            vec = [-x for x in vec]
        pairs.append((round(a[col][col], 10), vec))
    # For transition kernels, sort descending: principal stationary/common flow first.
    pairs.sort(key=lambda item: item[0], reverse=True)
    return [p[0] for p in pairs], [p[1] for p in pairs]


def _stationary_distribution(p: List[List[float]], iterations: int = 128) -> List[float]:
    n = len(p)
    if n == 0:
        return []
    dist = [1.0 / n for _ in range(n)]
    for _ in range(iterations):
        nxt = [0.0 for _ in range(n)]
        for i in range(n):
            for j in range(n):
                nxt[j] += dist[i] * p[i][j]
        total = sum(max(0.0, x) for x in nxt)
        if total <= 1e-12:
            return [1.0 / n for _ in range(n)]
        dist = [max(0.0, x) / total for x in nxt]
    return [round(x, 10) for x in dist]


def _matrix_power(p: List[List[float]], steps: int) -> List[List[float]]:
    n = len(p)
    if n == 0:
        return []
    result = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    base = [[p[i][j] for j in range(n)] for i in range(n)]
    for _ in range(steps):
        nxt = [[0.0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                nxt[i][j] = sum(result[i][k] * base[k][j] for k in range(n))
        result = nxt
    return result


def _mixing_score(p: List[List[float]]) -> float:
    n = len(p)
    if n == 0:
        return 0.0
    p4 = _matrix_power(p, 4)
    min_entry = min((x for row in p4 for x in row), default=0.0)
    return _clamp(min_entry * n, 0.0)


def _extract_ai1_operator(ai1: Mapping[str, Any]) -> Dict[str, Any]:
    op = ai1.get("reference_frame_operator") if isinstance(ai1, Mapping) else {}
    if not isinstance(op, Mapping):
        op = {}
    components = op.get("components") or ai1.get("operator_components") or {}
    if not isinstance(components, Mapping):
        components = {}
    l_markov = _matrix_from_any(components.get("L_markov"))
    p = _matrix_from_any(ai1.get("transition_matrix")) or _matrix_from_any(op.get("transition_matrix"))
    if p and not l_markov:
        l_markov = _l_markov_from_transition(p)
    if l_markov and not p:
        p = _transition_from_l_markov(l_markov)
    nodes = op.get("basis_nodes") or ai1.get("basis_nodes") or []
    if not isinstance(nodes, list):
        nodes = []
    if l_markov and len(nodes) != len(l_markov):
        nodes = [f"state_{i}" for i in range(len(l_markov))]
    return {
        "operator": dict(op),
        "components": dict(components),
        "l_markov": l_markov,
        "transition_matrix": p,
        "basis_nodes": [str(x) for x in nodes],
        "ai1_status": ai1.get("reference_frame_operator_builder_status", ""),
        "ai1_built": bool(ai1.get("l_rf_operator_built", False)),
        "ai1_construction_score": _clamp(ai1.get("construction_score"), 0.0),
    }


def _synthetic_ai1(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    if not inputs:
        return {}
    p = _matrix_from_any(inputs.get("transition_matrix"))
    if not p and inputs.get("markov_transition_available"):
        p = [
            [0.10, 0.50, 0.30, 0.10],
            [0.20, 0.20, 0.45, 0.15],
            [0.25, 0.15, 0.25, 0.35],
            [0.40, 0.20, 0.10, 0.30],
        ]
    l_markov = _matrix_from_any(inputs.get("L_markov")) or (_l_markov_from_transition(p) if p else [])
    nodes = inputs.get("basis_nodes") if isinstance(inputs.get("basis_nodes"), list) else ["rf_origin", "rf_metric_axis", "rf_temporal_axis", "rf_possibility_axis"][:len(l_markov)]
    return {
        "reference_frame_operator_builder_status": "REFERENCE_FRAME_OPERATOR_BUILT" if l_markov else "REFERENCE_FRAME_OPERATOR_INSUFFICIENT",
        "l_rf_operator_built": bool(l_markov),
        "construction_score": 0.88 if l_markov else 0.0,
        "reference_frame_operator": {
            "operator_id": "AI1_SYNTHETIC_L_RF_OPERATOR",
            "basis_nodes": nodes,
            "basis_dimension": len(l_markov),
            "components": {"L_graph": [], "L_markov": l_markov, "L_pi": []},
            "transition_matrix": p,
        },
    }


class MarkovTransitionModeExtractor:
    """Extract deterministic Markov transition modes from AI1 L_markov."""

    primitive = "MARKOV_TRANSITION_MODE_EXTRACTOR"
    expected_status = "MARKOV_TRANSITION_MODES_EXTRACTED"
    insufficient_status = "MARKOV_TRANSITION_MODES_INSUFFICIENT"
    next_recommended_module = "possibility_gradient_mode_extractor"
    threshold = 0.70

    def _source_payload(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        if inputs is None:
            ai1 = _load_json(AI1_JSON) or _try_ai1()
        elif "reference_frame_operator" in inputs or "operator_components" in inputs or "transition_matrix" in inputs or "L_markov" in inputs:
            ai1 = dict(inputs)
            if "transition_matrix" in inputs or "L_markov" in inputs:
                ai1 = _synthetic_ai1(inputs)
        else:
            ai1 = _synthetic_ai1(inputs)
        payload = _extract_ai1_operator(ai1)
        ai2 = _load_json(AI2_JSON) or _try_ai2()
        payload["ai2_status"] = ai2.get("graph_laplacian_mode_extractor_status", "") if isinstance(ai2, Mapping) else ""
        payload["ai2_extracted"] = bool(ai2.get("graph_laplacian_modes_extracted", False)) if isinstance(ai2, Mapping) else False
        payload["ai2_score"] = _clamp(ai2.get("extraction_score") or ai2.get("certification_score"), 0.0) if isinstance(ai2, Mapping) else 0.0
        return payload

    def _mode_payload(self, transition: List[List[float]], nodes: List[str]) -> Dict[str, Any]:
        if not transition:
            return {
                "matrix_dimension": 0,
                "row_stochastic": False,
                "row_sum_residual": 1.0,
                "transition_matrix": [],
                "transition_eigenvalues": [],
                "transition_eigenvectors": [],
                "markov_transition_modes": [],
                "stationary_distribution": [],
                "stationarity_residual": 1.0,
                "transition_spectral_gap": 0.0,
                "mixing_score": 0.0,
                "mode_count": 0,
                "mode_stability_score": 0.0,
            }
        p = _transition_from_l_markov(_l_markov_from_transition(transition)) if not _is_row_stochastic(transition) else transition
        n = len(p)
        sym = _symmetrize(p)
        eigenvalues, eigenvectors = _jacobi_eigen_symmetric(sym)
        stationary = _stationary_distribution(p)
        principal = eigenvalues[0] if eigenvalues else 0.0
        second = eigenvalues[1] if len(eigenvalues) > 1 else 0.0
        transition_gap = max(0.0, abs(principal) - abs(second))
        rows = _row_sums(p)
        row_res = max(abs(x - 1.0) for x in rows) if rows else 1.0
        stochastic_score = 1.0 if _is_row_stochastic(p, tol=1e-7) else _clamp(1.0 - min(1.0, row_res), 0.0)
        stationarity_res = 0.0
        if stationary:
            for j in range(n):
                proj = sum(stationary[i] * p[i][j] for i in range(n))
                stationarity_res = max(stationarity_res, abs(proj - stationary[j]))
        stationarity_score = _clamp(1.0 - min(1.0, stationarity_res * 10.0), 0.0)
        mixing = _mixing_score(p)
        spectral_order_score = 1.0 if eigenvalues == sorted(eigenvalues, reverse=True) else 0.0
        mode_stability_score = _mean([stochastic_score, stationarity_score, spectral_order_score, mixing, 1.0 if n >= 3 else 0.0])
        modes = []
        for idx, value in enumerate(eigenvalues):
            vector = eigenvectors[idx] if idx < len(eigenvectors) else []
            support = [nodes[i] if i < len(nodes) else f"state_{i}" for i, x in enumerate(vector) if abs(x) >= 1e-6]
            modes.append({
                "mode_id": f"AI3_MARKOV_MODE_{idx:02d}",
                "rank": idx,
                "eigenvalue": value,
                "relaxation_strength": _clamp(1.0 - abs(value), 0.0),
                "eigenvector": vector,
                "support_states": support,
                "mode_type": "stationary_transition_baseline" if idx == 0 else "transition_relaxation_mode",
            })
        return {
            "matrix_dimension": n,
            "row_stochastic": bool(_is_row_stochastic(p, tol=1e-7)),
            "row_sum_residual": row_res,
            "transition_matrix": p,
            "transition_eigenvalues": eigenvalues,
            "transition_eigenvectors": eigenvectors,
            "markov_transition_modes": modes,
            "stationary_distribution": stationary,
            "stationarity_residual": stationarity_res,
            "transition_spectral_gap": transition_gap,
            "mixing_score": mixing,
            "mode_count": len(modes),
            "mode_stability_score": mode_stability_score,
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        source = self._source_payload(inputs)
        l_markov = source["l_markov"]
        transition = source["transition_matrix"]
        nodes = source["basis_nodes"] or [f"state_{i}" for i in range(len(transition))]
        mode_payload = self._mode_payload(transition, nodes)

        ai1_support_score = _mean([1.0 if source["ai1_built"] else 0.0, source["ai1_construction_score"]])
        ai2_context_score = _mean([1.0 if source.get("ai2_extracted") else 0.65, source.get("ai2_score", 0.65)], 0.65)
        transition_well_formed_score = _mean([
            1.0 if mode_payload["matrix_dimension"] >= 3 else 0.0,
            1.0 if mode_payload["row_stochastic"] else 0.0,
            _clamp(1.0 - min(1.0, mode_payload["row_sum_residual"]), 0.0),
        ])
        spectral_extraction_score = _mean([
            1.0 if mode_payload["mode_count"] >= 3 else 0.0,
            mode_payload["mode_stability_score"],
            1.0 if mode_payload["transition_eigenvalues"] else 0.0,
        ])
        extraction_score = _mean([ai1_support_score, ai2_context_score, transition_well_formed_score, spectral_extraction_score])
        extracted = extraction_score >= self.threshold and mode_payload["mode_count"] >= 3 and bool(transition)
        status = self.expected_status if extracted else self.insufficient_status

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AI",
            "step_id": "AI3",
            "timestamp_utc": _now(),
            "markov_transition_mode_extractor_status": status,
            "markov_transition_modes_extracted": extracted,
            "transition_spectral_basis_constructed": extracted,
            "l_markov_component_available": bool(l_markov),
            "source_ai1_status": source["ai1_status"],
            "source_ai1_built": source["ai1_built"],
            "source_ai2_status": source.get("ai2_status", ""),
            "basis_states": nodes,
            "l_markov_matrix": l_markov,
            "transition_matrix": mode_payload["transition_matrix"],
            "markov_transition_modes": mode_payload["markov_transition_modes"],
            "transition_eigenvalues": mode_payload["transition_eigenvalues"],
            "transition_eigenvectors": mode_payload["transition_eigenvectors"],
            "stationary_distribution": mode_payload["stationary_distribution"],
            "stationarity_residual": mode_payload["stationarity_residual"],
            "mode_count": mode_payload["mode_count"],
            "transition_spectral_gap": mode_payload["transition_spectral_gap"],
            "mixing_score": mode_payload["mixing_score"],
            "matrix_dimension": mode_payload["matrix_dimension"],
            "row_sum_residual": mode_payload["row_sum_residual"],
            "row_stochastic": mode_payload["row_stochastic"],
            "mode_stability_score": mode_payload["mode_stability_score"],
            "ai1_support_score": ai1_support_score,
            "ai2_context_score": ai2_context_score,
            "transition_well_formed_score": transition_well_formed_score,
            "spectral_extraction_score": spectral_extraction_score,
            "extraction_score": extraction_score,
            "certification_score": extraction_score,
            "next_recommended_module": self.next_recommended_module,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "epistemic_guard": "strictly functional Markov transition mode extraction; no consciousness, qualia, subjectivity, or phenomenology claim",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"markov_transition_mode_extractor_{stamp}"
        json_path = OUT_DIR / f"{base}.json"
        md_path = OUT_DIR / f"{base}.md"
        prom_path = OUT_DIR / f"{base}.prom"
        latest_json = OUT_DIR / "latest_markov_transition_mode_extractor.json"
        latest_md = OUT_DIR / "latest_markov_transition_mode_extractor.md"
        latest_prom = OUT_DIR / "latest_markov_transition_mode_extractor.prom"
        history = OUT_DIR / "markov_transition_mode_extractor_history.jsonl"

        text = json.dumps(result, indent=2, ensure_ascii=False)
        json_path.write_text(text, encoding="utf-8")
        latest_json.write_text(text, encoding="utf-8")
        with history.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        md = "\n".join([
            "# AI3 — Markov Transition Mode Extractor",
            "",
            "Functional reconstruction: L_RF → Markov transition spectral modes.",
            "",
            f"Status: {result.get('markov_transition_mode_extractor_status')}",
            f"Markov transition modes extracted: {result.get('markov_transition_modes_extracted')}",
            f"Matrix dimension: {result.get('matrix_dimension')}",
            f"Mode count: {result.get('mode_count')}",
            f"Transition spectral gap: {result.get('transition_spectral_gap')}",
            f"Extraction score: {result.get('extraction_score')}",
            "",
            "Strictly functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness, qualia, or subjectivity claim.",
        ]) + "\n"
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")

        extracted = 1 if result.get("markov_transition_modes_extracted") else 0
        prom = "\n".join([
            f"oce_ai3_markov_transition_modes_extracted {extracted}",
            f"oce_ai3_extraction_score {result.get('extraction_score', 0.0)}",
            f"oce_ai3_transition_well_formed_score {result.get('transition_well_formed_score', 0.0)}",
            f"oce_ai3_spectral_extraction_score {result.get('spectral_extraction_score', 0.0)}",
            f"oce_ai3_mode_count {result.get('mode_count', 0)}",
            f"oce_ai3_transition_spectral_gap {result.get('transition_spectral_gap', 0.0)}",
            f"oce_ai3_mixing_score {result.get('mixing_score', 0.0)}",
            "oce_ai3_consciousness_proven 0.0",
            "oce_ai3_qualia_proven 0.0",
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
