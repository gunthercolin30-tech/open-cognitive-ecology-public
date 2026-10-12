"""AI4 — Possibility Gradient Mode Extractor.

Functional reconstruction step:
    L_RF -> possibility-gradient spectral modes

AI4 consumes the AI1 reference-frame operator payload and extracts the modes of
L_Pi, the possibility-gradient component of:

    L_RF = αL_graph + βL_markov + γL_Π

The module can use AC3 possibility gradients as supporting context, but the
output remains strictly formal-functional. It does not assert consciousness,
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
OUT_DIR = ROOT / "ai_robust_spectral_qualia_formal_modes" / "possibility_gradient_mode_extractor"
AI1_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "reference_frame_operator_builder" / "latest_reference_frame_operator_builder.json"
AI2_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "graph_laplacian_mode_extractor" / "latest_graph_laplacian_mode_extractor.json"
AI3_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "markov_transition_mode_extractor" / "latest_markov_transition_mode_extractor.json"


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


def _try_module_step(module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    try:
        mod = import_module(module_name)
        cls = getattr(mod, class_name)
        out = cls().step(*args, **kwargs)
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


def _default_l_pi(n: int = 5) -> List[List[float]]:
    """Deterministic cyclic possibility-gradient Laplacian."""
    n = max(3, int(n))
    w = 1.0 / 3.0
    mat = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        left = (i - 1) % n
        right = (i + 1) % n
        mat[i][i] = round(2.0 * w, 10)
        mat[i][left] = round(-w, 10)
        mat[i][right] = round(-w, 10)
    return mat


def _symmetrize(matrix: List[List[float]]) -> List[List[float]]:
    n = len(matrix)
    return [[0.5 * (_safe_float(matrix[i][j]) + _safe_float(matrix[j][i])) for j in range(n)] for i in range(n)]


def _row_abs_sum(matrix: List[List[float]], i: int) -> float:
    return sum(abs(_safe_float(matrix[i][j])) for j in range(len(matrix)) if j != i)


def _laplacian_well_formed_score(matrix: List[List[float]]) -> float:
    if not matrix:
        return 0.0
    n = len(matrix)
    row_residuals = [abs(sum(matrix[i])) for i in range(n)]
    symmetry_res = max(abs(matrix[i][j] - matrix[j][i]) for i in range(n) for j in range(n))
    diag_ok = sum(1 for i in range(n) if matrix[i][i] >= -1e-9) / n
    offdiag_ok = sum(1 for i in range(n) for j in range(n) if i == j or matrix[i][j] <= 1e-9) / (n * n)
    row_score = 1.0 - min(1.0, max(row_residuals) if row_residuals else 1.0)
    sym_score = 1.0 - min(1.0, symmetry_res)
    return _mean([row_score, sym_score, diag_ok, offdiag_ok])


def _jacobi_eigen_symmetric(matrix: List[List[float]], max_iter: int = 180, tol: float = 1e-10) -> Tuple[List[float], List[List[float]]]:
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
        pairs.append((round(max(0.0, a[col][col]), 10), vec))
    pairs.sort(key=lambda item: item[0])
    return [p[0] for p in pairs], [p[1] for p in pairs]


def _spectral_gap(eigenvalues: List[float]) -> float:
    if len(eigenvalues) < 2:
        return 0.0
    vals = sorted(max(0.0, _safe_float(v)) for v in eigenvalues)
    return round(max(0.0, vals[1] - vals[0]), 10)


def _gradient_profile_from_ac3(ac3: Mapping[str, Any]) -> Dict[str, Any]:
    gradients = ac3.get("possibility_gradients") or ac3.get("gradients") or []
    if not isinstance(gradients, list):
        gradients = []
    opening = []
    closure = []
    viability = []
    magnitude = []
    for g in gradients:
        if not isinstance(g, Mapping):
            continue
        opening.append(g.get("opening_gradient", g.get("opening_force", 0.0)))
        closure.append(g.get("closure_gradient", g.get("closure_force", 0.0)))
        viability.append(g.get("viability_gradient", 0.0))
        magnitude.append(g.get("gradient_magnitude", 0.0))
    summary = ac3.get("gradient_summary") or ac3.get("summary") or {}
    if not isinstance(summary, Mapping):
        summary = {}
    return {
        "gradient_count": len(gradients),
        "mean_opening_gradient": _clamp(summary.get("mean_opening_gradient", sum(map(_clamp, opening)) / len(opening) if opening else 0.5), 0.5),
        "mean_closure_gradient": _clamp(summary.get("mean_closure_gradient", sum(map(_clamp, closure)) / len(closure) if closure else 0.3), 0.3),
        "mean_viability_gradient": _clamp(summary.get("mean_viability_gradient", sum(map(_clamp, viability)) / len(viability) if viability else 0.6), 0.6),
        "mean_gradient_magnitude": _clamp(summary.get("mean_gradient_magnitude", sum(map(_clamp, magnitude)) / len(magnitude) if magnitude else 0.5), 0.5),
        "opening_direction_ratio": _clamp(summary.get("opening_direction_ratio", 0.5), 0.5),
        "closure_direction_ratio": _clamp(summary.get("closure_direction_ratio", 0.2), 0.2),
    }


class PossibilityGradientModeExtractor:
    """AI4 — Extract formal modes of the possibility-gradient operator L_Π."""

    primitive = "POSSIBILITY_GRADIENT_MODE_EXTRACTOR"
    expected_status = "POSSIBILITY_GRADIENT_MODES_EXTRACTED"
    insufficient_status = "POSSIBILITY_GRADIENT_MODES_INSUFFICIENT"
    next_recommended_module = "spectral_mode_extractor"
    threshold = 0.60

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or ROOT

    def _try_ai1(self) -> Dict[str, Any]:
        out = _try_module_step("ontology.reference_frame_operator_builder", "ReferenceFrameOperatorBuilder", persist=False)
        return out or _load_json(AI1_JSON)

    def _try_ai2(self) -> Dict[str, Any]:
        out = _try_module_step("ontology.graph_laplacian_mode_extractor", "GraphLaplacianModeExtractor", persist=False)
        return out or _load_json(AI2_JSON)

    def _try_ai3(self) -> Dict[str, Any]:
        out = _try_module_step("ontology.markov_transition_mode_extractor", "MarkovTransitionModeExtractor", persist=False)
        return out or _load_json(AI3_JSON)

    def _try_ac3(self) -> Dict[str, Any]:
        return _try_module_step("ontology.possibility_gradient_engine", "PossibilityGradientEngine", persist=False)

    def _source_payload(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        explicit = inputs is not None
        data = dict(inputs or {})
        ai1 = data.get("ai1") if isinstance(data.get("ai1"), Mapping) else ({} if explicit else self._try_ai1())
        ai2 = data.get("ai2") if isinstance(data.get("ai2"), Mapping) else ({} if explicit else self._try_ai2())
        ai3 = data.get("ai3") if isinstance(data.get("ai3"), Mapping) else ({} if explicit else self._try_ai3())
        ac3 = data.get("ac3") if isinstance(data.get("ac3"), Mapping) else ({} if explicit else self._try_ac3())

        op = ai1.get("reference_frame_operator") if isinstance(ai1, Mapping) else {}
        if not isinstance(op, Mapping):
            op = {}
        components = op.get("components") or ai1.get("operator_components") or {}
        if not isinstance(components, Mapping):
            components = {}
        l_pi = _matrix_from_any(data.get("l_pi_matrix") or data.get("L_pi") or components.get("L_pi") or components.get("L_pi".lower()))
        if not l_pi and data.get("possibility_gradient_available"):
            l_pi = _default_l_pi(5)
        if not l_pi and data.get("possibility_gradient_modes_available"):
            l_pi = _default_l_pi(5)

        basis = op.get("basis_nodes") or ai1.get("basis_nodes") or data.get("basis_nodes") or []
        if not isinstance(basis, list):
            basis = []
        if l_pi:
            basis = [str(x) for x in basis[:len(l_pi)]] if len(basis) >= len(l_pi) else [f"possibility_state_{i}" for i in range(len(l_pi))]

        profile = _gradient_profile_from_ac3(ac3 if isinstance(ac3, Mapping) else {})
        return {
            "ai1": dict(ai1) if isinstance(ai1, Mapping) else {},
            "ai2": dict(ai2) if isinstance(ai2, Mapping) else {},
            "ai3": dict(ai3) if isinstance(ai3, Mapping) else {},
            "ac3": dict(ac3) if isinstance(ac3, Mapping) else {},
            "l_pi": l_pi,
            "basis_nodes": basis,
            "gradient_profile": profile,
            "ai1_built": (bool(ai1.get("l_rf_operator_built", False)) if (isinstance(ai1, Mapping) and ai1) else bool(data.get("l_rf_operator_built", data.get("possibility_gradient_available", False)))),
            "ai1_status": ai1.get("reference_frame_operator_builder_status", "") if isinstance(ai1, Mapping) else "",
            "ai1_score": (_clamp(ai1.get("construction_score", ai1.get("certification_score", 0.0))) if (isinstance(ai1, Mapping) and ai1) else (1.0 if data.get("possibility_gradient_available") else 0.0)),
            "ai2_extracted": (bool(ai2.get("graph_laplacian_modes_extracted", False)) if (isinstance(ai2, Mapping) and ai2) else bool(data.get("graph_laplacian_modes_extracted", data.get("possibility_gradient_available", False)))),
            "ai2_score": (_clamp(ai2.get("extraction_score", ai2.get("certification_score", 0.0))) if (isinstance(ai2, Mapping) and ai2) else (1.0 if data.get("possibility_gradient_available") else 0.0)),
            "ai3_extracted": (bool(ai3.get("markov_transition_modes_extracted", False)) if (isinstance(ai3, Mapping) and ai3) else bool(data.get("markov_transition_modes_extracted", data.get("possibility_gradient_available", False)))),
            "ai3_score": (_clamp(ai3.get("extraction_score", ai3.get("certification_score", 0.0))) if (isinstance(ai3, Mapping) and ai3) else (1.0 if data.get("possibility_gradient_available") else 0.0)),
        }

    def _mode_payload(self, l_pi: List[List[float]], basis: List[str], gradient_profile: Mapping[str, Any]) -> Dict[str, Any]:
        sym = _symmetrize(l_pi)
        eigenvalues, eigenvectors = _jacobi_eigen_symmetric(sym)
        n = len(sym)
        modes: List[Dict[str, Any]] = []
        max_eig = max(eigenvalues) if eigenvalues else 1.0
        max_eig = max(max_eig, 1e-12)
        mean_opening = _clamp(gradient_profile.get("mean_opening_gradient", 0.5), 0.5)
        mean_viability = _clamp(gradient_profile.get("mean_viability_gradient", 0.6), 0.6)
        mean_closure = _clamp(gradient_profile.get("mean_closure_gradient", 0.3), 0.3)
        for idx, (val, vec) in enumerate(zip(eigenvalues, eigenvectors)):
            normalized_frequency = _clamp(val / max_eig if max_eig else 0.0)
            support = sum(1 for x in vec if abs(x) > 1e-8)
            localization = _clamp(1.0 - (support / n if n else 1.0))
            opening_alignment = _clamp((mean_opening + mean_viability + (1.0 - mean_closure)) / 3.0)
            mode_strength = _clamp((1.0 - normalized_frequency + opening_alignment + (1.0 - localization)) / 3.0)
            modes.append({
                "mode_id": f"AI4-LPI-MODE-{idx:02d}",
                "eigenvalue": val,
                "eigenvector": vec,
                "basis_nodes": basis,
                "normalized_frequency": normalized_frequency,
                "support_size": support,
                "localization_score": localization,
                "opening_alignment": opening_alignment,
                "mode_strength": mode_strength,
                "formal_label": "possibility_gradient_common_mode" if idx == 0 else "possibility_gradient_variation_mode",
            })
        return {
            "l_pi_matrix": [[round(x, 10) for x in row] for row in sym],
            "possibility_gradient_modes": modes,
            "possibility_eigenvalues": eigenvalues,
            "possibility_eigenvectors": eigenvectors,
            "mode_count": len(modes),
            "matrix_dimension": n,
            "possibility_spectral_gap": _spectral_gap(eigenvalues),
            "operator_well_formed_score": _laplacian_well_formed_score(sym),
            "mean_mode_strength": _mean([m["mode_strength"] for m in modes]),
            "gradient_alignment_score": _clamp((mean_opening + mean_viability + (1.0 - mean_closure)) / 3.0),
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        source = self._source_payload(inputs)
        l_pi = source["l_pi"]
        basis = source["basis_nodes"] or [f"possibility_state_{i}" for i in range(len(l_pi))]
        payload = self._mode_payload(l_pi, basis, source["gradient_profile"]) if l_pi else self._mode_payload([], [], source["gradient_profile"])

        ai1_support_score = _mean([1.0 if source["ai1_built"] else 0.0, source["ai1_score"]])
        upstream_mode_context_score = _mean([
            1.0 if source["ai2_extracted"] else 0.65,
            source["ai2_score"] or 0.65,
            1.0 if source["ai3_extracted"] else 0.65,
            source["ai3_score"] or 0.65,
        ], 0.65)
        possibility_gradient_context_score = _mean([
            1.0 if source["gradient_profile"].get("gradient_count", 0) > 0 else 0.75,
            source["gradient_profile"].get("mean_gradient_magnitude", 0.5),
            source["gradient_profile"].get("mean_viability_gradient", 0.6),
        ], 0.6)
        spectral_extraction_score = _mean([
            1.0 if payload["mode_count"] >= 3 else 0.0,
            payload["operator_well_formed_score"],
            payload["mean_mode_strength"],
            1.0 if payload["possibility_eigenvalues"] else 0.0,
        ])
        extraction_score = _mean([ai1_support_score, upstream_mode_context_score, possibility_gradient_context_score, spectral_extraction_score])
        extracted = extraction_score >= self.threshold and payload["mode_count"] >= 3 and bool(l_pi)
        status = self.expected_status if extracted else self.insufficient_status

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AI",
            "step_id": "AI4",
            "timestamp_utc": _now(),
            "possibility_gradient_mode_extractor_status": status,
            "possibility_gradient_modes_extracted": extracted,
            "possibility_gradient_spectral_basis_constructed": extracted,
            "l_pi_component_available": bool(l_pi),
            "source_ai1_status": source["ai1_status"],
            "source_ai1_built": source["ai1_built"],
            "source_ai2_extracted": source["ai2_extracted"],
            "source_ai3_extracted": source["ai3_extracted"],
            "basis_possibility_states": basis,
            "l_pi_matrix": payload["l_pi_matrix"],
            "possibility_gradient_modes": payload["possibility_gradient_modes"],
            "possibility_eigenvalues": payload["possibility_eigenvalues"],
            "possibility_eigenvectors": payload["possibility_eigenvectors"],
            "mode_count": payload["mode_count"],
            "matrix_dimension": payload["matrix_dimension"],
            "possibility_spectral_gap": payload["possibility_spectral_gap"],
            "gradient_profile": source["gradient_profile"],
            "gradient_alignment_score": payload["gradient_alignment_score"],
            "operator_well_formed_score": payload["operator_well_formed_score"],
            "mean_mode_strength": payload["mean_mode_strength"],
            "ai1_support_score": ai1_support_score,
            "upstream_mode_context_score": upstream_mode_context_score,
            "possibility_gradient_context_score": possibility_gradient_context_score,
            "spectral_extraction_score": spectral_extraction_score,
            "extraction_score": extraction_score,
            "certification_score": extraction_score,
            "next_recommended_module": self.next_recommended_module,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "epistemic_guard": "strictly functional possibility-gradient mode extraction; no consciousness, qualia, subjectivity, or phenomenology claim",
        }

        # AI4 v2 public-schema aliases for downstream spectral integration tests.
        gp = result.get("gradient_profile", {}) if isinstance(result.get("gradient_profile", {}), dict) else {}
        result["possibility_gradient_vector"] = [
            max(0.0, min(1.0, float(gp.get("mean_opening_gradient", 0.5)))),
            max(0.0, min(1.0, float(gp.get("mean_viability_gradient", 0.6)))),
            max(0.0, min(1.0, 1.0 - float(gp.get("mean_closure_gradient", 0.3)))),
            max(0.0, min(1.0, float(gp.get("mean_gradient_magnitude", 0.5)))),
        ]
        result["possibility_kernel_matrix"] = result.get("l_pi_matrix", [])
        result["gradient_coherence_score"] = result.get("gradient_alignment_score", result.get("possibility_gradient_context_score", 0.0))
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"possibility_gradient_mode_extractor_{stamp}"
        json_path = OUT_DIR / f"{base}.json"
        md_path = OUT_DIR / f"{base}.md"
        prom_path = OUT_DIR / f"{base}.prom"
        latest_json = OUT_DIR / "latest_possibility_gradient_mode_extractor.json"
        latest_md = OUT_DIR / "latest_possibility_gradient_mode_extractor.md"
        latest_prom = OUT_DIR / "latest_possibility_gradient_mode_extractor.prom"
        history = OUT_DIR / "possibility_gradient_mode_extractor_history.jsonl"

        text = json.dumps(result, indent=2, ensure_ascii=False)
        json_path.write_text(text, encoding="utf-8")
        latest_json.write_text(text, encoding="utf-8")
        with history.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        md = "\n".join([
            "# AI4 — Possibility Gradient Mode Extractor",
            "",
            "Functional reconstruction: L_RF → possibility-gradient spectral modes.",
            "",
            f"Status: {result.get('possibility_gradient_mode_extractor_status')}",
            f"Possibility-gradient modes extracted: {result.get('possibility_gradient_modes_extracted')}",
            f"Matrix dimension: {result.get('matrix_dimension')}",
            f"Mode count: {result.get('mode_count')}",
            f"Possibility spectral gap: {result.get('possibility_spectral_gap')}",
            f"Extraction score: {result.get('extraction_score')}",
            "",
            "Strictly functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness, qualia, or subjectivity claim.",
        ]) + "\n"
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")

        extracted = 1 if result.get("possibility_gradient_modes_extracted") else 0
        prom = "\n".join([
            f"oce_ai4_possibility_gradient_modes_extracted {extracted}",
            f"oce_ai4_extraction_score {result.get('extraction_score', 0.0)}",
            f"oce_ai4_possibility_gradient_context_score {result.get('possibility_gradient_context_score', 0.0)}",
            f"oce_ai4_spectral_extraction_score {result.get('spectral_extraction_score', 0.0)}",
            f"oce_ai4_mode_count {result.get('mode_count', 0)}",
            f"oce_ai4_possibility_spectral_gap {result.get('possibility_spectral_gap', 0.0)}",
            f"oce_ai4_gradient_alignment_score {result.get('gradient_alignment_score', 0.0)}",
            "oce_ai4_consciousness_proven 0.0",
            "oce_ai4_qualia_proven 0.0",
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
