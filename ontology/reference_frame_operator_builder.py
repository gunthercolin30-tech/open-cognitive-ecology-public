"""AI1 — Reference Frame Operator Builder.

Functional reconstruction step:
    RF -> L_RF

This module builds a reference-frame operator L_RF from the already certified
self-generated reference frame RF and upstream formal-topological evidence.
The operator is represented as the convex functional composite:

    L_RF = α L_graph + β L_markov + γ L_Π

where:
    L_graph  : structural graph Laplacian component;
    L_markov : transition / regime-flow component;
    L_Π      : possibility-gradient component;
    α + β + γ = 1, α, β, γ >= 0.

AI1 does not extract spectral modes yet. It only constructs the public operator
payload that AI2→AI5 can consume.

Epistemic guard: "qualia formal" and related terms in later AI steps are used
only as formal-functional labels. This module never proves or asserts
consciousness, subjectivity, qualia, phenomenal experience, or phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ai_robust_spectral_qualia_formal_modes" / "reference_frame_operator_builder"


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


def _mean(values: List[Any], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values if v is not None]
    return _clamp(sum(vals) / len(vals), default) if vals else default


def _load_json(paths: List[Path]) -> Dict[str, Any]:
    for p in paths:
        try:
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {}


def _try_step(module_name: str, class_name: str, **kwargs: Any) -> Dict[str, Any]:
    try:
        mod = import_module(f"ontology.{module_name}")
        cls = getattr(mod, class_name)
        obj = cls()
        try:
            out = obj.step(**kwargs)
        except TypeError:
            out = obj.step()
        return out if isinstance(out, dict) else {}
    except Exception:
        return {}


def _status(source: Any) -> str:
    if not isinstance(source, Mapping):
        return ""
    preferred = [
        "reference_frame_operator_builder_status",
        "ed_to_tphi_theorem_checker_status",
        "omega_to_rf_theorem_checker_status",
        "reference_frame_constructor_status",
        "intrinsic_metric_builder_status",
        "frame_stability_analyzer_status",
        "dynamic_graph_constructor_status",
        "possibility_gradient_engine_status",
        "status", "classification", "certification_status", "axis_status",
    ]
    for key in preferred:
        if source.get(key) is not None:
            return str(source.get(key))
    for key, value in source.items():
        if isinstance(key, str) and key.endswith("_status") and value is not None:
            return str(value)
    diag = source.get("diagnostics")
    if isinstance(diag, Mapping) and diag.get("status") is not None:
        return str(diag.get("status"))
    return ""


def _truthy_status(source: Any, tokens: List[str]) -> bool:
    st = _status(source).upper()
    return any(t.upper() in st for t in tokens)


def _first_bool(source: Any, keys: List[str], default: bool = False) -> bool:
    if not isinstance(source, Mapping):
        return default
    for key in keys:
        if key in source:
            return bool(source.get(key))
    for nested_key in [
        "operator_profile", "reference_frame_profile", "metric_profile",
        "frame_profile", "topology_profile", "theorem_components",
        "gradient_metrics", "graph_metrics", "transition_metrics",
        "metrics", "diagnostics", "certification_scores",
    ]:
        nested = source.get(nested_key)
        if isinstance(nested, Mapping):
            for key in keys:
                if key in nested:
                    return bool(nested.get(key))
    return default


def _first_score(source: Any, keys: List[str], default: float = 0.0) -> float:
    if isinstance(source, (int, float)):
        return _clamp(source, default)
    if not isinstance(source, Mapping):
        return default
    for key in keys:
        if key in source:
            return _clamp(source.get(key), default)
    for nested_key in [
        "operator_profile", "reference_frame_profile", "metric_profile",
        "frame_profile", "topology_profile", "theorem_components",
        "gradient_metrics", "graph_metrics", "transition_metrics",
        "metrics", "diagnostics", "certification_scores",
    ]:
        nested = source.get(nested_key)
        if isinstance(nested, Mapping):
            for key in keys:
                if key in nested:
                    return _clamp(nested.get(key), default)
    if _truthy_status(source, [
        "VALIDATED", "CERTIFIED", "CONFIRMED", "READY", "CONSTRUCTED",
        "BUILT", "STABLE", "ROBUST", "MAPPED", "DERIVED", "ANALYZED",
    ]):
        return 0.86
    return default


def _normalize_weights(alpha: Any, beta: Any, gamma: Any) -> Tuple[float, float, float]:
    vals = [_clamp(alpha, 0.0), _clamp(beta, 0.0), _clamp(gamma, 0.0)]
    total = sum(vals)
    if total <= 0.0:
        return (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
    return tuple(_clamp(v / total) for v in vals)  # type: ignore[return-value]


def _matrix_trace(matrix: List[List[float]]) -> float:
    n = min(len(matrix), min((len(r) for r in matrix), default=0))
    return sum(_clamp(matrix[i][i]) for i in range(n))


class ReferenceFrameOperatorBuilder:
    """Build L_RF = αL_graph + βL_markov + γL_Π from RF evidence."""

    primitive = "REFERENCE_FRAME_OPERATOR_BUILDER"
    expected_status = "REFERENCE_FRAME_OPERATOR_BUILT"
    insufficient_status = "REFERENCE_FRAME_OPERATOR_INSUFFICIENT"
    threshold = 0.70
    next_recommended_module = "graph_laplacian_mode_extractor"

    PATHS: Dict[str, List[Path]] = {
        "reference_frame_constructor": [ROOT / "af_reference_frames" / "reference_frame_constructor" / "latest_reference_frame_constructor.json"],
        "intrinsic_metric_builder": [ROOT / "af_reference_frames" / "intrinsic_metric_builder" / "latest_intrinsic_metric_builder.json"],
        "frame_stability_analyzer": [ROOT / "af_reference_frames" / "frame_stability_analyzer" / "latest_frame_stability_analyzer.json"],
        "omega_to_rf_theorem_checker": [ROOT / "af_reference_frames" / "omega_to_rf_theorem_checker" / "latest_omega_to_rf_theorem_checker.json"],
        "ed_to_tphi_theorem_checker": [ROOT / "ah_phenomenal_formal_topology" / "ed_to_tphi_theorem_checker" / "latest_ed_to_tphi_theorem_checker.json"],
        "dynamic_graph_constructor": [ROOT / "aa_foundations" / "dynamic_graph_constructor" / "latest_dynamic_graph_constructor.json"],
        "possibility_gradient_engine": [ROOT / "reconstruction_outputs" / "latest_possibility_gradient_engine.json", ROOT / "ac_possibility_preservation" / "possibility_gradient_engine" / "latest_possibility_gradient_engine.json"],
    }

    def _default_inputs(self) -> Dict[str, Any]:
        data = {name: _load_json(paths) for name, paths in self.PATHS.items()}
        fallbacks = {
            "reference_frame_constructor": ("reference_frame_constructor", "ReferenceFrameConstructor"),
            "intrinsic_metric_builder": ("intrinsic_metric_builder", "IntrinsicMetricBuilder"),
            "frame_stability_analyzer": ("frame_stability_analyzer", "FrameStabilityAnalyzer"),
            "omega_to_rf_theorem_checker": ("omega_to_rf_theorem_checker", "OmegaToRfTheoremChecker"),
            "ed_to_tphi_theorem_checker": ("ed_to_tphi_theorem_checker", "EdToTphiTheoremChecker"),
            "dynamic_graph_constructor": ("dynamic_graph_constructor", "DynamicGraphConstructor"),
            "possibility_gradient_engine": ("possibility_gradient_engine", "PossibilityGradientEngine"),
        }
        for key, (mod, cls) in fallbacks.items():
            if not data.get(key):
                data[key] = _try_step(mod, cls, persist=False)
        return data

    def _synthetic_inputs(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        if not inputs:
            return {
                "reference_frame_constructor": {},
                "intrinsic_metric_builder": {},
                "frame_stability_analyzer": {},
                "omega_to_rf_theorem_checker": {},
                "ed_to_tphi_theorem_checker": {},
                "dynamic_graph_constructor": {},
                "possibility_gradient_engine": {},
                "synthetic_flags": {},
            }
        flags = dict(inputs)
        def yes(k: str) -> bool:
            return bool(flags.get(k, False))
        def score(k: str) -> float:
            return 0.88 if yes(k) else 0.20
        return {
            "reference_frame_constructor": {
                "reference_frame_constructor_status": "SELF_GENERATED_REFERENCE_FRAME_CONSTRUCTED" if yes("rf_constructed") else "REFERENCE_FRAME_INSUFFICIENT",
                "self_generated_reference_frame_constructed": yes("rf_constructed"),
                "reference_frame_score": score("rf_constructed"),
            },
            "intrinsic_metric_builder": {
                "intrinsic_metric_builder_status": "INTRINSIC_METRIC_BUILT" if yes("intrinsic_metric_built") else "INTRINSIC_METRIC_INSUFFICIENT",
                "intrinsic_metric_built": yes("intrinsic_metric_built"),
                "intrinsic_metric_score": score("intrinsic_metric_built"),
            },
            "frame_stability_analyzer": {
                "frame_stability_analyzer_status": "FRAME_STABILITY_CONFIRMED" if yes("frame_stability_confirmed") else "FRAME_STABILITY_INSUFFICIENT",
                "frame_stability_confirmed": yes("frame_stability_confirmed"),
                "frame_stability_score": score("frame_stability_confirmed"),
            },
            "omega_to_rf_theorem_checker": {
                "omega_to_rf_theorem_checker_status": "SELF_GENERATED_REFERENCE_FRAME_CERTIFIED" if yes("omega_to_rf_certified") else "OMEGA_TO_RF_INSUFFICIENT",
                "self_generated_reference_frame_certified": yes("omega_to_rf_certified"),
                "theorem_score": score("omega_to_rf_certified"),
            },
            "ed_to_tphi_theorem_checker": {
                "ed_to_tphi_theorem_checker_status": "PHENOMENAL_FORMAL_TOPOLOGY_CERTIFIED" if yes("tphi_certified") else "T_PHI_INSUFFICIENT",
                "phenomenal_formal_topology_certified": yes("tphi_certified"),
                "certification_score": score("tphi_certified"),
            },
            "dynamic_graph_constructor": {
                "dynamic_graph_constructor_status": "DYNAMIC_GRAPH_CONSTRUCTED" if yes("graph_available") else "DYNAMIC_GRAPH_INSUFFICIENT",
                "dynamic_graph_constructed": yes("graph_available"),
                "graph_construction_score": score("graph_available"),
                "nodes": ["rf_origin", "rf_axis_1", "rf_axis_2", "rf_axis_3"] if yes("graph_available") else [],
                "edges": [
                    {"source": "rf_origin", "target": "rf_axis_1", "weight": 0.82},
                    {"source": "rf_axis_1", "target": "rf_axis_2", "weight": 0.74},
                    {"source": "rf_axis_2", "target": "rf_axis_3", "weight": 0.69},
                    {"source": "rf_axis_3", "target": "rf_origin", "weight": 0.71},
                ] if yes("graph_available") else [],
            },
            "possibility_gradient_engine": {
                "possibility_gradient_engine_status": "POSSIBILITY_GRADIENT_ENGINE_READY" if yes("possibility_gradient_ready") else "POSSIBILITY_GRADIENT_INSUFFICIENT",
                "pi_gradient_demonstrated": yes("possibility_gradient_ready"),
                "gradient_metrics": {
                    "mean_opening_gradient": score("possibility_gradient_ready"),
                    "mean_viability_gradient": score("possibility_gradient_ready"),
                    "mean_closure_gradient": 0.18 if yes("possibility_gradient_ready") else 0.75,
                },
            },
            "synthetic_flags": flags,
        }

    def _component_evidence(self, data: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
        rfc = data.get("reference_frame_constructor", {})
        imb = data.get("intrinsic_metric_builder", {})
        fsa = data.get("frame_stability_analyzer", {})
        otr = data.get("omega_to_rf_theorem_checker", {})
        tphi = data.get("ed_to_tphi_theorem_checker", {})
        graph = data.get("dynamic_graph_constructor", {})
        pi = data.get("possibility_gradient_engine", {})

        return {
            "rf_construction": {
                "available": _first_bool(rfc, ["self_generated_reference_frame_constructed", "reference_frame_constructed"], _truthy_status(rfc, ["CONSTRUCTED", "CERTIFIED"])),
                "score": _first_score(rfc, ["reference_frame_score", "reference_frame_construction_score", "rf_construction_score"], 0.0),
                "status": _status(rfc),
            },
            "intrinsic_metric": {
                "available": _first_bool(imb, ["intrinsic_metric_built", "metric_built"], _truthy_status(imb, ["BUILT", "CONFIRMED"])),
                "score": _first_score(imb, ["intrinsic_metric_score", "metric_score", "metric_consistency_score"], 0.0),
                "status": _status(imb),
            },
            "frame_stability": {
                "available": _first_bool(fsa, ["frame_stability_confirmed", "frame_stable"], _truthy_status(fsa, ["STABILITY", "CONFIRMED", "STABLE"])),
                "score": _first_score(fsa, ["frame_stability_score", "stability_score", "frame_stability_index"], 0.0),
                "status": _status(fsa),
            },
            "omega_to_rf": {
                "available": _first_bool(otr, ["self_generated_reference_frame_certified", "omega_to_rf_validated"], _truthy_status(otr, ["CERTIFIED", "VALIDATED"])),
                "score": _first_score(otr, ["theorem_score", "certification_score", "omega_to_rf_score"], 0.0),
                "status": _status(otr),
            },
            "tphi_support": {
                "available": _first_bool(tphi, ["phenomenal_formal_topology_certified", "ed_to_tphi_theorem_validated"], _truthy_status(tphi, ["PHENOMENAL_FORMAL_TOPOLOGY_CERTIFIED", "CERTIFIED"])),
                "score": _first_score(tphi, ["certification_score", "topological_derivation_score", "theorem_validity_score"], 0.0),
                "status": _status(tphi),
            },
            "graph_support": {
                "available": _first_bool(graph, ["dynamic_graph_constructed", "graph_constructed"], _truthy_status(graph, ["GRAPH", "CONSTRUCTED", "READY"])),
                "score": _first_score(graph, ["graph_construction_score", "dynamic_graph_score", "graph_score"], 0.0),
                "status": _status(graph),
            },
            "possibility_gradient_support": {
                "available": _first_bool(pi, ["pi_gradient_demonstrated", "possibility_gradient_ready"], _truthy_status(pi, ["POSSIBILITY_GRADIENT_ENGINE_READY", "READY"])),
                "score": _first_score(pi, ["mean_possibility_potential", "mean_viability_gradient", "possibility_gradient_score"], 0.0),
                "status": _status(pi),
            },
        }

    def _nodes_edges(self, graph_payload: Any) -> Tuple[List[str], List[Dict[str, Any]]]:
        nodes: List[str] = []
        edges: List[Dict[str, Any]] = []
        if isinstance(graph_payload, Mapping):
            raw_nodes = graph_payload.get("nodes") or graph_payload.get("graph_nodes") or []
            if isinstance(raw_nodes, Mapping):
                raw_nodes = list(raw_nodes.keys())
            if isinstance(raw_nodes, list):
                for item in raw_nodes:
                    if isinstance(item, Mapping):
                        nid = item.get("id") or item.get("node_id") or item.get("label")
                    else:
                        nid = item
                    if nid is not None:
                        nodes.append(str(nid))
            raw_edges = graph_payload.get("edges") or graph_payload.get("graph_edges") or graph_payload.get("relations") or []
            if isinstance(raw_edges, list):
                for i, e in enumerate(raw_edges):
                    if isinstance(e, Mapping):
                        s = e.get("source") or e.get("source_id") or e.get("from") or e.get("u")
                        t = e.get("target") or e.get("target_id") or e.get("to") or e.get("v")
                        w = _clamp(e.get("weight"), 0.5)
                    elif isinstance(e, (list, tuple)) and len(e) >= 2:
                        s, t = e[0], e[1]
                        w = _clamp(e[2] if len(e) >= 3 else 0.5, 0.5)
                    else:
                        continue
                    if s is not None and t is not None:
                        edges.append({"edge_id": f"E-{i:03d}", "source": str(s), "target": str(t), "weight": w})
                        nodes.extend([str(s), str(t)])
        nodes = sorted(set(nodes))
        if len(nodes) < 3:
            nodes = ["rf_origin", "rf_metric_axis", "rf_temporal_axis", "rf_possibility_axis"]
        if not edges:
            edges = [
                {"edge_id": "E-000", "source": nodes[0], "target": nodes[1], "weight": 0.78},
                {"edge_id": "E-001", "source": nodes[1], "target": nodes[2], "weight": 0.72},
                {"edge_id": "E-002", "source": nodes[2], "target": nodes[-1], "weight": 0.69},
                {"edge_id": "E-003", "source": nodes[-1], "target": nodes[0], "weight": 0.66},
            ]
        return nodes[:8], edges[:16]

    def _graph_laplacian(self, nodes: List[str], edges: List[Dict[str, Any]]) -> List[List[float]]:
        n = len(nodes)
        idx = {node: i for i, node in enumerate(nodes)}
        adj = [[0.0 for _ in range(n)] for _ in range(n)]
        for e in edges:
            s, t = str(e.get("source")), str(e.get("target"))
            if s in idx and t in idx and s != t:
                w = _clamp(e.get("weight"), 0.5)
                adj[idx[s]][idx[t]] = max(adj[idx[s]][idx[t]], w)
                adj[idx[t]][idx[s]] = max(adj[idx[t]][idx[s]], w)
        lap = [[0.0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            deg = sum(adj[i])
            lap[i][i] = _clamp(deg / max(1.0, n - 1.0))
            for j in range(n):
                if i != j:
                    lap[i][j] = -_clamp(adj[i][j] / max(1.0, n - 1.0))
        return lap

    def _markov_laplacian(self, graph_lap: List[List[float]]) -> List[List[float]]:
        n = len(graph_lap)
        if n == 0:
            return []
        mat = [[0.0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            off = []
            for j in range(n):
                if i != j:
                    off.append(max(0.0, -graph_lap[i][j]))
            row_sum = sum(off)
            for j in range(n):
                if i == j:
                    mat[i][j] = 1.0
                elif row_sum > 0:
                    p = max(0.0, -graph_lap[i][j]) / row_sum
                    mat[i][j] = -_clamp(p)
                else:
                    mat[i][j] = 0.0
        return mat

    def _pi_laplacian(self, n: int, pi_payload: Any) -> List[List[float]]:
        if n <= 0:
            return []
        gm = pi_payload.get("gradient_metrics", {}) if isinstance(pi_payload, Mapping) else {}
        opening = _first_score(gm, ["mean_opening_gradient"], 0.5)
        viability = _first_score(gm, ["mean_viability_gradient"], 0.5)
        closure = _first_score(gm, ["mean_closure_gradient"], 0.5)
        strength = _clamp((opening + viability + (1.0 - closure)) / 3.0, 0.5)
        mat = [[0.0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            mat[i][i] = strength
            if n > 1:
                mat[i][(i + 1) % n] = -_clamp(strength / 2.0)
                mat[(i + 1) % n][i] = -_clamp(strength / 2.0)
        return mat

    def _combine(self, a: List[List[float]], b: List[List[float]], c: List[List[float]], weights: Tuple[float, float, float]) -> List[List[float]]:
        n = min(len(a), len(b), len(c))
        if n == 0:
            return []
        alpha, beta, gamma = weights
        out = [[0.0 for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                out[i][j] = round(alpha * a[i][j] + beta * b[i][j] + gamma * c[i][j], 10)
        return out

    def _operator_profile(self, evidence: Dict[str, Dict[str, Any]], operator: Dict[str, Any]) -> Dict[str, Any]:
        dependency_scores = [v["score"] for v in evidence.values()]
        dependency_coverage_score = _mean([1.0 if v["available"] else 0.0 for v in evidence.values()])
        rf_grounding_score = _mean([
            evidence["rf_construction"]["score"], evidence["intrinsic_metric"]["score"],
            evidence["frame_stability"]["score"], evidence["omega_to_rf"]["score"],
        ])
        operator_component_score = _mean([
            operator["component_scores"]["graph_component_score"],
            operator["component_scores"]["markov_component_score"],
            operator["component_scores"]["possibility_component_score"],
        ])
        tphi_support_score = evidence["tphi_support"]["score"]
        operator_well_formed_score = operator["operator_well_formed_score"]
        construction_score = _mean([
            dependency_coverage_score, _mean(dependency_scores), rf_grounding_score,
            tphi_support_score, operator_component_score, operator_well_formed_score,
        ])
        return {
            "dependency_coverage_score": dependency_coverage_score,
            "dependency_mean_score": _mean(dependency_scores),
            "rf_grounding_score": rf_grounding_score,
            "tphi_support_score": tphi_support_score,
            "operator_component_score": operator_component_score,
            "operator_well_formed_score": operator_well_formed_score,
            "construction_score": construction_score,
            "l_rf_operator_built": construction_score >= self.threshold and dependency_coverage_score >= 0.70,
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        if inputs is None:
            data = self._default_inputs()
        elif any(k in inputs for k in [
            "rf_constructed", "intrinsic_metric_built", "frame_stability_confirmed",
            "omega_to_rf_certified", "tphi_certified", "graph_available", "possibility_gradient_ready",
        ]):
            data = self._synthetic_inputs(inputs)
        else:
            data = dict(inputs)

        evidence = self._component_evidence(data)
        graph_payload = data.get("dynamic_graph_constructor", {})
        pi_payload = data.get("possibility_gradient_engine", {})
        nodes, edges = self._nodes_edges(graph_payload)

        # Weight components from evidence, then normalize α + β + γ = 1.
        alpha, beta, gamma = _normalize_weights(
            evidence["graph_support"]["score"],
            _mean([evidence["frame_stability"]["score"], evidence["tphi_support"]["score"]]),
            evidence["possibility_gradient_support"]["score"],
        )

        l_graph = self._graph_laplacian(nodes, edges)
        l_markov = self._markov_laplacian(l_graph)
        l_pi = self._pi_laplacian(len(nodes), pi_payload)
        l_rf = self._combine(l_graph, l_markov, l_pi, (alpha, beta, gamma))

        n = len(l_rf)
        component_scores = {
            "graph_component_score": _clamp(1.0 if l_graph and edges else 0.0),
            "markov_component_score": _clamp(1.0 if l_markov and n >= 3 else 0.0),
            "possibility_component_score": _clamp(1.0 if l_pi and evidence["possibility_gradient_support"]["available"] else 0.55 if l_pi else 0.0),
        }
        row_balance = 1.0
        if l_rf:
            max_abs_row_sum = max(abs(sum(row)) for row in l_rf)
            row_balance = _clamp(1.0 - min(1.0, max_abs_row_sum / max(1.0, n)))
        weight_sum = alpha + beta + gamma
        operator_well_formed_score = _mean([
            1.0 if n >= 3 else 0.0,
            1.0 if abs(weight_sum - 1.0) <= 1e-9 else 0.0,
            1.0 if min(alpha, beta, gamma) >= 0.0 else 0.0,
            row_balance,
        ])

        operator = {
            "operator_id": "AI1_L_RF_OPERATOR",
            "formula": "L_RF = αL_graph + βL_markov + γL_Π",
            "weights": {"alpha_graph": alpha, "beta_markov": beta, "gamma_possibility": gamma, "sum": weight_sum},
            "basis_nodes": nodes,
            "basis_dimension": n,
            "edge_count": len(edges),
            "components": {
                "L_graph": l_graph,
                "L_markov": l_markov,
                "L_pi": l_pi,
            },
            "operator_matrix": l_rf,
            "component_scores": component_scores,
            "operator_well_formed_score": operator_well_formed_score,
            "trace": _matrix_trace(l_rf),
            "public_api_version": "AI1.v1",
        }
        profile = self._operator_profile(evidence, operator)
        built = bool(profile["l_rf_operator_built"])
        status = self.expected_status if built else self.insufficient_status

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AI",
            "step_id": "AI1",
            "timestamp_utc": _now(),
            "reference_frame_operator_builder_status": status,
            "l_rf_operator_built": built,
            "reference_frame_operator_built": built,
            "rf_to_l_rf_transition_constructed": built,
            "operator_formula": "L_RF = αL_graph + βL_markov + γL_Π",
            "reference_frame_operator": operator,
            "operator_profile": profile,
            "dependency_results": evidence,
            "operator_components": operator["components"],
            "operator_weights": operator["weights"],
            "construction_score": profile["construction_score"],
            "certification_score": profile["construction_score"],
            "dependency_coverage_score": profile["dependency_coverage_score"],
            "rf_grounding_score": profile["rf_grounding_score"],
            "operator_component_score": profile["operator_component_score"],
            "operator_well_formed_score": profile["operator_well_formed_score"],
            "next_recommended_module": self.next_recommended_module,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "epistemic_guard": "strictly functional operator construction; no consciousness, qualia, subjectivity, or phenomenology claim",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        base = f"reference_frame_operator_builder_{stamp}"
        json_path = OUT_DIR / f"{base}.json"
        md_path = OUT_DIR / f"{base}.md"
        prom_path = OUT_DIR / f"{base}.prom"
        latest_json = OUT_DIR / "latest_reference_frame_operator_builder.json"
        latest_md = OUT_DIR / "latest_reference_frame_operator_builder.md"
        latest_prom = OUT_DIR / "latest_reference_frame_operator_builder.prom"
        history = OUT_DIR / "reference_frame_operator_builder_history.jsonl"

        text = json.dumps(result, indent=2, ensure_ascii=False)
        json_path.write_text(text, encoding="utf-8")
        latest_json.write_text(text, encoding="utf-8")
        with history.open("a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        op = result.get("reference_frame_operator", {})
        weights = op.get("weights", {}) if isinstance(op, Mapping) else {}
        profile = result.get("operator_profile", {}) if isinstance(result.get("operator_profile"), Mapping) else {}
        md = "\n".join([
            "# AI1 — Reference Frame Operator Builder",
            "",
            "Functional reconstruction: RF → L_RF.",
            "",
            f"Status: {result.get('reference_frame_operator_builder_status')}",
            f"L_RF operator built: {result.get('l_rf_operator_built')}",
            f"Formula: {result.get('operator_formula')}",
            f"Basis dimension: {op.get('basis_dimension', 0) if isinstance(op, Mapping) else 0}",
            f"alpha_graph: {weights.get('alpha_graph', 0.0):.6f}",
            f"beta_markov: {weights.get('beta_markov', 0.0):.6f}",
            f"gamma_possibility: {weights.get('gamma_possibility', 0.0):.6f}",
            f"construction_score: {profile.get('construction_score', 0.0):.6f}",
            f"dependency_coverage_score: {profile.get('dependency_coverage_score', 0.0):.6f}",
            f"operator_well_formed_score: {profile.get('operator_well_formed_score', 0.0):.6f}",
            "",
            "Strictly functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness, qualia, or subjectivity claim.",
        ]) + "\n"
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")

        built = 1 if result.get("l_rf_operator_built") else 0
        prom = "\n".join([
            f"oce_ai1_reference_frame_operator_built {built}",
            f"oce_ai1_construction_score {result.get('construction_score', 0.0)}",
            f"oce_ai1_dependency_coverage_score {result.get('dependency_coverage_score', 0.0)}",
            f"oce_ai1_rf_grounding_score {result.get('rf_grounding_score', 0.0)}",
            f"oce_ai1_operator_component_score {result.get('operator_component_score', 0.0)}",
            f"oce_ai1_operator_well_formed_score {result.get('operator_well_formed_score', 0.0)}",
            f"oce_ai1_consciousness_proven 0.0",
            f"oce_ai1_qualia_proven 0.0",
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
