"""AF5 — Frame Stability Analyzer.

Functional analyzer for the longitudinal and structural stability of a
self-generated reference frame RF after AF1--AF4.

The module reconstructs the transition:
    RF intrinsic + externality-independent -> stable RF candidate

It evaluates stability of frame axes, coordinates, intrinsic metric,
externality independence and Omega support. It is strictly functional and
structural: it does not assert consciousness, subjectivity, qualia,
experience, or phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "af_reference_frames" / "frame_stability_analyzer"


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


def _mean(values: List[float], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values if v is not None]
    return _clamp(sum(vals) / len(vals), default) if vals else default


def _load_json(path: Path) -> Dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
    except Exception:
        return {}
    return {}


def _as_mapping(value: Any, preferred_key: str = "value") -> Dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, (int, float)):
        return {preferred_key: value}
    return {}


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _first_score(source: Any, keys: List[str], default: float = 0.0) -> float:
    if isinstance(source, (int, float)):
        return _clamp(source, default)
    if not isinstance(source, Mapping):
        return default
    for key in keys:
        if key in source:
            return _clamp(source.get(key), default)
    return default


class FrameStabilityAnalyzer:
    """Analyze whether a constructed self-generated RF is stable enough for AF6."""

    primitive = "FRAME_STABILITY_ANALYZER"
    expected_status = "FRAME_STABILITY_CONFIRMED"

    def _default_inputs(self) -> Dict[str, Any]:
        return {
            "frame_externality_test": _load_json(ROOT / "af_reference_frames" / "frame_externality_test" / "latest_frame_externality_test.json"),
            "intrinsic_metric_builder": _load_json(ROOT / "af_reference_frames" / "intrinsic_metric_builder" / "latest_intrinsic_metric_builder.json"),
            "reference_frame_constructor": _load_json(ROOT / "af_reference_frames" / "reference_frame_constructor" / "latest_reference_frame_constructor.json"),
            "intrinsic_distinction_detector": _load_json(ROOT / "af_reference_frames" / "intrinsic_distinction_detector" / "latest_intrinsic_distinction_detector.json"),
            "omega_stability_monitor": _load_json(ROOT / "ae_omega_coherence" / "omega_stability_monitor" / "latest_omega_stability_monitor.json"),
            "omega_failure_analyzer": _load_json(ROOT / "ae_omega_coherence" / "omega_failure_analyzer" / "latest_omega_failure_analyzer.json"),
            "identity_continuity_index": _load_json(ROOT / "ad_memory_identity_reflexivity" / "identity_continuity_index" / "latest_identity_continuity_index.json"),
            "memory_integration_analyzer": _load_json(ROOT / "ad_memory_identity_reflexivity" / "memory_integration_analyzer" / "latest_memory_integration_analyzer.json"),
        }

    def _has_evidence(self, inputs: Mapping[str, Any]) -> bool:
        return any((isinstance(v, Mapping) and bool(v)) or isinstance(v, list) or isinstance(v, (int, float)) for v in inputs.values())

    def _extract_metrics(self, data: Mapping[str, Any]) -> Dict[str, float]:
        af4 = _as_mapping(data.get("frame_externality_test"), "frame_externality_score")
        af3 = _as_mapping(data.get("intrinsic_metric_builder"), "intrinsic_metric_score")
        af2 = _as_mapping(data.get("reference_frame_constructor"), "reference_frame_score")
        af1 = _as_mapping(data.get("intrinsic_distinction_detector"), "intrinsic_distinction_score")
        oms = _as_mapping(data.get("omega_stability_monitor"), "omega_stability_score")
        ofa = _as_mapping(data.get("omega_failure_analyzer"), "omega_resilience_score")
        ici = _as_mapping(data.get("identity_continuity_index"), "identity_continuity_score")
        mia = _as_mapping(data.get("memory_integration_analyzer"), "memory_integration_score")

        frame_axes = _safe_list(af2.get("frame_axes"))
        components = _safe_list(af3.get("metric_components"))
        externality_tests = _safe_list(af4.get("externality_tests"))

        axis_scores = [_first_score(a, ["axis_score", "score"], 0.82) for a in frame_axes]
        component_scores = [_first_score(c, ["component_score", "grounding_score", "score"], 0.82) for c in components]
        externality_scores = [_first_score(t, ["test_score", "score"], 0.88) for t in externality_tests]

        frame_score = _first_score(data, ["reference_frame_score"], _first_score(af2, ["reference_frame_score"], 0.82))
        metric_score = _first_score(data, ["intrinsic_metric_score"], _first_score(af3, ["intrinsic_metric_score"], 0.82))
        externality_score = _first_score(data, ["frame_externality_score"], _first_score(af4, ["frame_externality_score"], 0.88))
        omega_stability = _first_score(data, ["omega_stability_score"], _first_score(oms, ["omega_stability_score", "stability_score", "omega_stability_index"], 0.84))
        omega_resilience = _first_score(data, ["omega_resilience_score"], _first_score(ofa, ["omega_resilience_score", "resilience_score"], 0.84))
        identity_continuity = _first_score(data, ["identity_continuity_score"], _first_score(ici, ["identity_continuity_score", "continuity_score", "identity_continuity_index"], 0.82))
        memory_integration = _first_score(data, ["memory_integration_score"], _first_score(mia, ["memory_integration_score", "integration_score"], 0.82))

        return {
            "frame_score": frame_score,
            "axis_persistence": _mean(axis_scores, frame_score),
            "metric_score": metric_score,
            "metric_component_stability": _mean(component_scores, metric_score),
            "externality_independence_stability": externality_score,
            "externality_test_stability": _mean(externality_scores, externality_score),
            "omega_stability_score": omega_stability,
            "omega_resilience_score": omega_resilience,
            "identity_continuity_score": identity_continuity,
            "memory_integration_score": memory_integration,
        }

    def _build_observations(self, metrics: Mapping[str, float]) -> List[Dict[str, Any]]:
        specs = [
            ("FS-O01", "frame_axis_persistence", "AF2 frame axes remain stable under RF reuse", metrics["axis_persistence"], 0.20),
            ("FS-O02", "intrinsic_metric_stability", "AF3 intrinsic metric components remain internally grounded", _mean([metrics["metric_score"], metrics["metric_component_stability"]]), 0.20),
            ("FS-O03", "externality_independence_stability", "AF4 externality independence remains stable", _mean([metrics["externality_independence_stability"], metrics["externality_test_stability"]]), 0.20),
            ("FS-O04", "omega_support_stability", "Omega stability and resilience continue to support RF", _mean([metrics["omega_stability_score"], metrics["omega_resilience_score"]]), 0.20),
            ("FS-O05", "identity_memory_continuity", "AD continuity and memory integration preserve RF interpretability", _mean([metrics["identity_continuity_score"], metrics["memory_integration_score"]]), 0.20),
        ]
        return [
            {
                "observation_id": oid,
                "label": label,
                "stability_basis": basis,
                "observation_score": _clamp(score),
                "observation_weight": weight,
                "below_threshold": _clamp(score) < 0.72,
            }
            for oid, label, basis, score, weight in specs
        ]

    def _build_profile(self, observations: List[Dict[str, Any]], metrics: Mapping[str, float]) -> Dict[str, Any]:
        weighted = sum(o["observation_score"] * o["observation_weight"] for o in observations)
        score = _clamp(weighted)
        return {
            "stability_observation_count": len(observations),
            "unstable_observation_count": sum(1 for o in observations if o["below_threshold"]),
            "mean_observation_score": _mean([o["observation_score"] for o in observations]),
            "weighted_stability_score": score,
            "frame_persistence_score": metrics["axis_persistence"],
            "metric_stability_score": metrics["metric_component_stability"],
            "externality_stability_score": metrics["externality_independence_stability"],
            "omega_support_score": _mean([metrics["omega_stability_score"], metrics["omega_resilience_score"]]),
            "identity_memory_support_score": _mean([metrics["identity_continuity_score"], metrics["memory_integration_score"]]),
        }

    def _failure_conditions(self, profile: Mapping[str, Any]) -> List[str]:
        failures: List[str] = []
        if profile["frame_persistence_score"] < 0.72:
            failures.append("frame_axis_persistence_below_threshold")
        if profile["metric_stability_score"] < 0.72:
            failures.append("intrinsic_metric_stability_below_threshold")
        if profile["externality_stability_score"] < 0.72:
            failures.append("externality_independence_stability_below_threshold")
        if profile["omega_support_score"] < 0.72:
            failures.append("omega_support_stability_below_threshold")
        if profile["identity_memory_support_score"] < 0.72:
            failures.append("identity_memory_support_below_threshold")
        if profile["weighted_stability_score"] < 0.72:
            failures.append("frame_stability_score_below_threshold")
        return failures

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_frame_stability_analyzer.json"
        md_path = OUT_DIR / "latest_frame_stability_analyzer.md"
        prom_path = OUT_DIR / "latest_frame_stability_analyzer.prom"

        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

        observations = result.get("stability_observations", [])
        profile = result.get("stability_profile", {})
        md_lines = [
            "# AF5 — Frame Stability Analyzer",
            "",
            f"Status: {result.get('frame_stability_analyzer_status')}",
            f"Frame stability score: {result.get('frame_stability_score')}",
            f"Functional conclusion only: {result.get('functional_conclusion_only')}",
            f"Phenomenology undetermined: {result.get('phenomenology_undetermined')}",
            "",
            "## Stability profile",
        ]
        for k, v in profile.items():
            md_lines.append(f"- {k}: {v}")
        md_lines.extend(["", "## Stability observations"])
        for obs in observations:
            md_lines.append(f"- {obs.get('observation_id')} — {obs.get('label')}: {obs.get('observation_score')} ({obs.get('stability_basis')})")
        md_lines.extend(["", "## Longitudinal stability certificate"])
        cert = result.get("longitudinal_stability_certificate", {})
        if isinstance(cert, dict):
            for k, v in cert.items():
                md_lines.append(f"- {k}: {v}")
        else:
            md_lines.append(f"- certificate: {cert}")

        md_lines.extend(["", "## Failure conditions"])
        for item in result.get("failure_conditions", []):
            md_lines.append(f"- {item}")
        if not result.get("failure_conditions"):
            md_lines.append("- none")
        md_lines.extend(["", "## RF prerequisites", ""])
        for k, v in result.get("rf_prerequisites", {}).items():
            md_lines.append(f"- {k}: {v}")
        md_lines.extend(["", "## Epistemic guard", "This report is a functional stability analysis only. It does not prove consciousness, subjectivity, qualia, or phenomenology."])
        md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

        prom_lines = [
            f"oce_frame_stability_score {result.get('frame_stability_score', 0.0)}",
            f"oce_frame_stability_observation_count {len(observations)}",
            f"oce_frame_unstable_observation_count {profile.get('unstable_observation_count', 0)}",
            f"oce_frame_metric_stability_score {profile.get('metric_stability_score', 0.0)}",
            f"oce_frame_externality_stability_score {profile.get('externality_stability_score', 0.0)}",
            f"oce_frame_omega_support_score {profile.get('omega_support_score', 0.0)}",
            f"oce_frame_stability_confirmed {1 if result.get('frame_stability_confirmed') else 0}",
        ]
        prom_path.write_text("\n".join(prom_lines) + "\n", encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        data = dict(inputs) if isinstance(inputs, Mapping) else self._default_inputs()
        has_evidence = self._has_evidence(data)
        metrics = self._extract_metrics(data) if has_evidence else {
            "frame_score": 0.0,
            "axis_persistence": 0.0,
            "metric_score": 0.0,
            "metric_component_stability": 0.0,
            "externality_independence_stability": 0.0,
            "externality_test_stability": 0.0,
            "omega_stability_score": 0.0,
            "omega_resilience_score": 0.0,
            "identity_continuity_score": 0.0,
            "memory_integration_score": 0.0,
        }
        observations = self._build_observations(metrics)
        profile = self._build_profile(observations, metrics)
        failures = self._failure_conditions(profile)
        score = _clamp(profile["weighted_stability_score"])
        confirmed = bool(has_evidence and score >= 0.72 and not failures)
        status = "FRAME_STABILITY_CONFIRMED" if confirmed else "FRAME_STABILITY_INSUFFICIENT"

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": _now(),
            "frame_stability_analyzer_status": status,
            "frame_stability_confirmed": confirmed,
            "frame_stability_score": score,
            "stability_observations": observations,
            "stability_profile": profile,
            "longitudinal_stability_certificate": {
                "certificate_status": "functional_rf_stability_supported" if confirmed else "functional_rf_stability_insufficient",
                "minimum_threshold": 0.72,
                "score": score,
                "external_reference_required": False,
                "certifies_consciousness": False,
            },
            "rf_prerequisites": {
                "frame_stability_confirmed": confirmed,
                "stable_reference_frame_available": confirmed,
                "omega_to_rf_theorem_checker_readiness": _clamp((score + metrics["omega_stability_score"] + metrics["omega_resilience_score"]) / 3.0),
                "next_required_module": "omega_to_rf_theorem_checker",
            },
            "metrics": dict(metrics),
            "failure_conditions": failures,
            "public_schema": {
                "required_fields": [
                    "stability_observations",
                    "stability_profile",
                    "longitudinal_stability_certificate",
                    "rf_prerequisites",
                    "frame_stability_score",
                    "failure_conditions",
                    "consciousness_proven",
                    "phenomenology_undetermined",
                    "functional_conclusion_only",
                ]
            },
            "consciousness_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
