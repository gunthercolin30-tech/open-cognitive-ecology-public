
"""AI2 — Graph Laplacian Mode Extractor.

Functional reconstruction step:
    L_RF -> graph-Laplian spectral modes

AI2 consumes the AI1 reference-frame operator payload and extracts the modes of
L_graph, the structural graph-Laplacian component of:

    L_RF = αL_graph + βL_markov + γL_Π

This module does not interpret the resulting modes as phenomenal entities. It
only constructs formal-functional graph modes that later AI steps can align with
Markov and possibility-gradient modes.

Epistemic guard: no consciousness, subjectivity, qualia, or phenomenology claim.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ai_robust_spectral_qualia_formal_modes" / "graph_laplacian_mode_extractor"
AI1_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "reference_frame_operator_builder" / "latest_reference_frame_operator_builder.json"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _clamp(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    if math.isnan(v) or math.isinf(v):
        return default
    return max(0.0, min(1.0, v))


def _safe_float(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    if math.isnan(v) or math.isinf(v):
        return default
    return v


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


def _symmetrize(matrix: List[List[float]]) -> List[List[float]]:
    n = len(matrix)
    return [[0.5 * (matrix[i][j] + matrix[j][i]) for j in range(n)] for i in range(n)]


def _row_sum_residual(matrix: List[List[float]]) -> float:
    if not matrix:
        return 1.0
    return max(abs(sum(row)) for row in matrix)


def _is_symmetric(matrix: List[List[float]], tol: float = 1e-8) -> bool:
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            if abs(matrix[i][j] - matrix[j][i]) > tol:
                return False
    return True


def _jacobi_eigen_symmetric(matrix: List[List[float]], max_iter: int = 128, tol: float = 1e-10) -> Tuple[List[float], List[List[float]]]:
    """Small deterministic Jacobi eigensolver for symmetric real matrices.

    Returns eigenvalues and column eigenvectors sorted by eigenvalue.
    Designed for the small AI operator matrices used in OCE validation.
    """
    n = len(matrix)
    if n == 0:
        return [], []
    a = [[float(matrix[i][j]) for j in range(n)] for i in range(n)]
    v = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]

    for _ in range(max_iter):
        p, q = 0, 1 if n > 1 else 0
        max_off = 0.0
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
        c = math.cos(angle)
        s = math.sin(angle)

        app = c*c*a[p][p] - 2*s*c*a[p][q] + s*s*a[q][q]
        aqq = s*s*a[p][p] + 2*s*c*a[p][q] + c*c*a[q][q]
        a[p][q] = a[q][p] = 0.0
        a[p][p], a[q][q] = app, aqq
        for k in range(n):
            if k != p and k != q:
                akp = a[k][p]
                akq = a[k][q]
                a[k][p] = a[p][k] = c*akp - s*akq
                a[k][q] = a[q][k] = s*akp + c*akq
        for k in range(n):
            vkp = v[k][p]
            vkq = v[k][q]
            v[k][p] = c*vkp - s*vkq
            v[k][q] = s*vkp + c*vkq

    pairs = []
    for col in range(n):
        vec = [v[row][col] for row in range(n)]
        norm = math.sqrt(sum(x*x for x in vec)) or 1.0
        vec = [round(x / norm, 10) for x in vec]
        # deterministic sign convention
        first_nonzero = next((x for x in vec if abs(x) > 1e-9), 0.0)
        if first_nonzero < 0:
            vec = [-x for x in vec]
        pairs.append((round(a[col][col], 10), vec))
    pairs.sort(key=lambda item: item[0])
    return [p[0] for p in pairs], [p[1] for p in pairs]


def _extract_ai1_operator(ai1: Mapping[str, Any]) -> Dict[str, Any]:
    op = ai1.get("reference_frame_operator") if isinstance(ai1, Mapping) else {}
    if not isinstance(op, Mapping):
        op = {}
    components = op.get("components") or ai1.get("operator_components") or {}
    if not isinstance(components, Mapping):
        components = {}
    l_graph = _matrix_from_any(components.get("L_graph"))
    nodes = op.get("basis_nodes") or ai1.get("basis_nodes") or []
    if not isinstance(nodes, list):
        nodes = []
    nodes = [str(x) for x in nodes][:len(l_graph)] if l_graph else [str(x) for x in nodes]
    if l_graph and len(nodes) != len(l_graph):
        nodes = [f"node_{i}" for i in range(len(l_graph))]
    return {
        "operator": dict(op),
        "components": dict(components),
        "l_graph": l_graph,
        "basis_nodes": nodes,
        "ai1_status": ai1.get("reference_frame_operator_builder_status", ""),
        "ai1_built": bool(ai1.get("l_rf_operator_built", False)),
        "ai1_construction_score": _clamp(ai1.get("construction_score"), 0.0),
    }


def _synthetic_ai1(inputs: Mapping[str, Any]) -> Dict[str, Any]:
    if not inputs:
        return {}
    if "L_graph" in inputs:
        l_graph = _matrix_from_any(inputs.get("L_graph"))
    elif inputs.get("graph_laplacian_available"):
        l_graph = [
            [0.50, -0.25, -0.25, 0.00],
            [-0.25, 0.50, 0.00, -0.25],
            [-0.25, 0.00, 0.50, -0.25],
            [0.00, -0.25, -0.25, 0.50],
        ]
    else:
        l_graph = []
    nodes = inputs.get("basis_nodes") if isinstance(inputs.get("basis_nodes"), list) else ["a", "b", "c", "d"][:len(l_graph)]
    return {
        "reference_frame_operator_builder_status": "REFERENCE_FRAME_OPERATOR_BUILT" if l_graph else "REFERENCE_FRAME_OPERATOR_INSUFFICIENT",
        "l_rf_operator_built": bool(l_graph),
        "construction_score": 0.88 if l_graph else 0.0,
        "reference_frame_operator": {
            "operator_id": "AI1_SYNTHETIC_L_RF_OPERATOR",
            "basis_nodes": nodes,
            "basis_dimension": len(l_graph),
            "components": {"L_graph": l_graph, "L_markov": [], "L_pi": []},
        },
    }


class GraphLaplacianModeExtractor:
    """Extract deterministic graph-Laplacian modes from AI1 L_graph."""

    primitive = "GRAPH_LAPLACIAN_MODE_EXTRACTOR"
    expected_status = "GRAPH_LAPLACIAN_MODES_EXTRACTED"
    insufficient_status = "GRAPH_LAPLACIAN_MODES_INSUFFICIENT"
    next_recommended_module = "markov_transition_mode_extractor"
    threshold = 0.70

    def _source_payload(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        if inputs is None:
            ai1 = _load_json(AI1_JSON) or _try_ai1()
        elif "reference_frame_operator" in inputs or "operator_components" in inputs:
            ai1 = dict(inputs)
        else:
            ai1 = _synthetic_ai1(inputs)
        return _extract_ai1_operator(ai1)

    def _mode_payload(self, l_graph: List[List[float]], nodes: List[str]) -> Dict[str, Any]:
        if not l_graph:
            return {
                "matrix_dimension": 0,
                "symmetric_laplacian": False,
                "row_sum_residual": 1.0,
                "eigenvalues": [],
                "eigenvectors": [],
                "graph_laplacian_modes": [],
                "spectral_gap": 0.0,
                "zero_mode_detected": False,
                "mode_count": 0,
                "mode_stability_score": 0.0,
            }
        matrix = _symmetrize(l_graph)
        eigenvalues, eigenvectors = _jacobi_eigen_symmetric(matrix)
        n = len(matrix)
        zero_mode = bool(eigenvalues and abs(eigenvalues[0]) <= 1e-6)
        nonzero = [x for x in eigenvalues if x > 1e-8]
        spectral_gap = nonzero[0] if nonzero else 0.0
        max_abs_eval = max([abs(x) for x in eigenvalues] + [1.0])
        normalized_gap = _clamp(spectral_gap / max_abs_eval, 0.0)
        row_res = _row_sum_residual(matrix)
        symmetry_score = 1.0 if _is_symmetric(matrix) else 0.0
        row_balance_score = _clamp(1.0 - min(1.0, row_res), 0.0)
        spectral_order_score = 1.0 if eigenvalues == sorted(eigenvalues) else 0.0
        mode_stability_score = _mean([symmetry_score, row_balance_score, spectral_order_score, 1.0 if n >= 3 else 0.0])
        modes = []
        for idx, value in enumerate(eigenvalues):
            vector = eigenvectors[idx] if idx < len(eigenvectors) else []
            support = [nodes[i] if i < len(nodes) else f"node_{i}" for i, x in enumerate(vector) if abs(x) >= 1e-6]
            modes.append({
                "mode_id": f"AI2_GRAPH_MODE_{idx:02d}",
                "rank": idx,
                "eigenvalue": value,
                "normalized_eigenvalue": _clamp(abs(value) / max_abs_eval, 0.0),
                "eigenvector": vector,
                "support_nodes": support,
                "mode_type": "zero_structural_baseline" if idx == 0 and abs(value) <= 1e-6 else "graph_structural_variation",
            })
        return {
            "matrix_dimension": n,
            "symmetric_laplacian": bool(symmetry_score),
            "row_sum_residual": row_res,
            "eigenvalues": eigenvalues,
            "eigenvectors": eigenvectors,
            "graph_laplacian_modes": modes,
            "spectral_gap": spectral_gap,
            "normalized_spectral_gap": normalized_gap,
            "zero_mode_detected": zero_mode,
            "mode_count": len(modes),
            "mode_stability_score": mode_stability_score,
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        source = self._source_payload(inputs)
        l_graph = source["l_graph"]
        nodes = source["basis_nodes"]
        mode_payload = self._mode_payload(l_graph, nodes)

        ai1_support_score = _mean([1.0 if source["ai1_built"] else 0.0, source["ai1_construction_score"]])
        matrix_well_formed_score = _mean([
            1.0 if mode_payload["matrix_dimension"] >= 3 else 0.0,
            1.0 if mode_payload["symmetric_laplacian"] else 0.0,
            _clamp(1.0 - min(1.0, mode_payload["row_sum_residual"]), 0.0),
        ])
        spectral_extraction_score = _mean([
            1.0 if mode_payload["mode_count"] >= 3 else 0.0,
            mode_payload["mode_stability_score"],
            1.0 if mode_payload["eigenvalues"] else 0.0,
        ])
        extraction_score = _mean([ai1_support_score, matrix_well_formed_score, spectral_extraction_score])
        extracted = extraction_score >= self.threshold and mode_payload["mode_count"] >= 3
        status = self.expected_status if extracted else self.insufficient_status

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AI",
            "step_id": "AI2",
            "timestamp_utc": _now(),
            "graph_laplacian_mode_extractor_status": status,
            "graph_laplacian_modes_extracted": extracted,
            "spectral_basis_constructed": extracted,
            "l_graph_component_available": bool(l_graph),
            "source_ai1_status": source["ai1_status"],
            "source_ai1_built": source["ai1_built"],
            "basis_nodes": nodes,
            "laplacian_matrix": _symmetrize(l_graph) if l_graph else [],
            "graph_laplacian_modes": mode_payload["graph_laplacian_modes"],
            "eigenvalues": mode_payload["eigenvalues"],
            "eigenvectors": mode_payload["eigenvectors"],
            "mode_count": mode_payload["mode_count"],
            "spectral_gap": mode_payload["spectral_gap"],
            "normalized_spectral_gap": mode_payload.get("normalized_spectral_gap", 0.0),
            "zero_mode_detected": mode_payload["zero_mode_detected"],
            "matrix_dimension": mode_payload["matrix_dimension"],
            "row_sum_residual": mode_payload["row_sum_residual"],
            "mode_stability_score": mode_payload["mode_stability_score"],
            "ai1_support_score": ai1_support_score,
            "matrix_well_formed_score": matrix_well_formed_score,
            "spectral_extraction_score": spectral_extraction_score,
            "extraction_score": extraction_score,
            "certification_score": extraction_score,
            "next_recommended_module": self.next_recommended_module,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "epistemic_guard": "strictly functional graph spectral mode extraction; no consciousness, qualia, subjectivity, or phenomenology claim",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"graph_laplacian_mode_extractor_{stamp}"
        json_path = OUT_DIR / f"{base}.json"
        md_path = OUT_DIR / f"{base}.md"
        prom_path = OUT_DIR / f"{base}.prom"
        latest_json = OUT_DIR / "latest_graph_laplacian_mode_extractor.json"
        latest_md = OUT_DIR / "latest_graph_laplacian_mode_extractor.md"
        latest_prom = OUT_DIR / "latest_graph_laplacian_mode_extractor.prom"
        history = OUT_DIR / "graph_laplacian_mode_extractor_history.jsonl"

        text = json.dumps(result, indent=2, ensure_ascii=False)
        json_path.write_text(text, encoding="utf-8")
        latest_json.write_text(text, encoding="utf-8")
        with history.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        md = "\n".join([
            "# AI2 — Graph Laplacian Mode Extractor",
            "",
            "Functional reconstruction: L_RF → graph-Laplacian spectral modes.",
            "",
            f"Status: {result.get('graph_laplacian_mode_extractor_status')}",
            f"Graph Laplacian modes extracted: {result.get('graph_laplacian_modes_extracted')}",
            f"Matrix dimension: {result.get('matrix_dimension')}",
            f"Mode count: {result.get('mode_count')}",
            f"Spectral gap: {result.get('spectral_gap')}",
            f"Extraction score: {result.get('extraction_score')}",
            "",
            "Strictly functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness, qualia, or subjectivity claim.",
        ]) + "\n"
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")

        extracted = 1 if result.get("graph_laplacian_modes_extracted") else 0
        prom = "\n".join([
            f"oce_ai2_graph_laplacian_modes_extracted {extracted}",
            f"oce_ai2_extraction_score {result.get('extraction_score', 0.0)}",
            f"oce_ai2_matrix_well_formed_score {result.get('matrix_well_formed_score', 0.0)}",
            f"oce_ai2_spectral_extraction_score {result.get('spectral_extraction_score', 0.0)}",
            f"oce_ai2_mode_count {result.get('mode_count', 0)}",
            f"oce_ai2_spectral_gap {result.get('spectral_gap', 0.0)}",
            "oce_ai2_consciousness_proven 0.0",
            "oce_ai2_qualia_proven 0.0",
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
