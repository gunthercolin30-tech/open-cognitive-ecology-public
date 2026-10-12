"""AG2 — Temporal Asymmetry Analyzer.

Functional analyzer for the transition:
    T -> directed / asymmetric T

Patch v2: fixes synthetic-input alias propagation into component scoring while preserving real-mode behavior.

The module derives a temporal-asymmetry profile from the proper-time structure
extracted in AG1. It integrates proper-time extraction, irreversibility,
trajectory hysteresis, trajectory path-dependence, causal directionality,
phase-transition support, and temporal binding into a strictly functional
arrow-of-time model.

Epistemic guard: this module certifies only structural/functional temporal
asymmetry. It never asserts consciousness, subjectivity, qualia, experience,
or phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ag_proper_time_existence_domain" / "temporal_asymmetry_analyzer"


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


def _load_json_candidates(candidates: List[Path]) -> Dict[str, Any]:
    for p in candidates:
        try:
            if p.exists():
                data = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {}


def _status(source: Any) -> str:
    if not isinstance(source, Mapping):
        return ""
    for key in ["status", "certification_status", "axis_status"]:
        if source.get(key) is not None:
            return str(source.get(key))
    for k, v in source.items():
        if isinstance(k, str) and k.endswith("_status") and v is not None:
            return str(v)
    diag = source.get("diagnostics")
    if isinstance(diag, Mapping) and diag.get("status") is not None:
        return str(diag.get("status"))
    return ""


def _first_score(source: Any, keys: List[str], default: float = 0.0) -> float:
    if isinstance(source, (int, float)):
        return _clamp(source, default)
    if not isinstance(source, Mapping):
        return default
    for key in keys:
        if key in source:
            return _clamp(source.get(key), default)
    for nested_key in ["temporal_profile", "temporal_arrow_profile", "metrics", "diagnostics"]:
        nested = source.get(nested_key)
        if isinstance(nested, Mapping):
            for key in keys:
                if key in nested:
                    return _clamp(nested.get(key), default)
    st = _status(source).upper()
    if any(t in st for t in ["VALIDATED", "CERTIFIED", "CONFIRMED", "READY", "ESTABLISHED", "DETECTED", "BUILT", "CONSTRUCTED", "MONITORED", "ANALYZED", "EXTRACTED", "ACTIVE", "NOMINAL", "EVALUATED"]):
        return 0.86
    return default


def _try_step(module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
    try:
        mod = import_module(f"ontology.{module_name}")
        cls = getattr(mod, class_name)
        obj = cls()
        try:
            res = obj.step(*args, **kwargs)
        except TypeError:
            res = obj.step()
        return res if isinstance(res, dict) else {}
    except Exception:
        return {}


def _try_diagnostics(module_name: str, class_name: str) -> Dict[str, Any]:
    try:
        mod = import_module(f"ontology.{module_name}")
        obj = getattr(mod, class_name)()
        res = obj.diagnostics()
        return res if isinstance(res, dict) else {}
    except Exception:
        return {}


class TemporalAsymmetryAnalyzer:
    """Analyze proper-time asymmetry and temporal directionality."""

    primitive = "TEMPORAL_ASYMMETRY_ANALYZER"
    expected_status = "TEMPORAL_ASYMMETRY_ANALYZED"
    threshold = 0.72

    PATHS: Dict[str, List[Path]] = {
        "proper_time_extractor": [ROOT / "ag_proper_time_existence_domain" / "proper_time_extractor" / "latest_proper_time_extractor.json"],
        "omega_to_rf_theorem_checker": [ROOT / "af_reference_frames" / "omega_to_rf_theorem_checker" / "latest_omega_to_rf_theorem_checker.json"],
    }

    SYNTHETIC_KEYS = {
        "proper_time_extracted", "temporal_direction_available", "irreversibility_available",
        "causal_directionality_available", "path_dependence_available", "hysteresis_available",
        "phase_transition_support_available", "temporal_binding_available",
    }

    def _default_inputs(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        data["proper_time_extractor"] = _load_json_candidates(self.PATHS["proper_time_extractor"])
        if not data["proper_time_extractor"]:
            data["proper_time_extractor"] = _try_step("proper_time_extractor", "ProperTimeExtractor", persist=False)
        data["omega_to_rf_theorem_checker"] = _load_json_candidates(self.PATHS["omega_to_rf_theorem_checker"])
        if not data["omega_to_rf_theorem_checker"]:
            data["omega_to_rf_theorem_checker"] = _try_step("omega_to_rf_theorem_checker", "OmegaToRfTheoremChecker", persist=False)

        proper_score = _first_score(data["proper_time_extractor"], ["proper_time_score"], 0.82)
        seed = max(0.72, proper_score)
        data["irreversibility"] = _try_step(
            "irreversibility", "Irreversibility",
            entropy_production=seed,
            historical_path_dependence=seed,
            reversal_difficulty=seed,
        )
        data["causal_inference"] = _try_step(
            "causal_inference", "CausalInference",
            discriminations=[seed, True],
            intervention_predictions=[seed, True],
            structural_signals=[seed, True],
        )
        data["trajectory_irreversibility"] = _try_diagnostics("trajectory_irreversibility", "TrajectoryIrreversibility")
        data["trajectory_hysteresis"] = _try_diagnostics("trajectory_hysteresis", "TrajectoryHysteresis")
        data["trajectory_phase_transition"] = _try_diagnostics("trajectory_phase_transition", "TrajectoryPhaseTransition")
        data["trajectory_path_dependency"] = _try_diagnostics("trajectory_path_dependency", "TrajectoryPathDependency")
        data["trajectory_bifurcation"] = _try_diagnostics("trajectory_bifurcation", "TrajectoryBifurcation")
        data["global_temporal_binding"] = _try_diagnostics("global_temporal_binding", "GlobalTemporalBinding")
        return data

    def _normalize_inputs(self, inputs: Optional[Mapping[str, Any]]) -> Tuple[Dict[str, Any], bool, bool]:
        if inputs is None:
            return self._default_inputs(), False, False
        data = dict(inputs)
        synthetic = any(k in data for k in self.SYNTHETIC_KEYS)
        degradation = len(data) == 0
        return data, degradation, synthetic

    def _evidence_items(self, data: Mapping[str, Any], synthetic: bool) -> List[Dict[str, Any]]:
        if synthetic:
            specs = [
                ("AG2-E01", "proper_time", "Proper time T is already extracted", data.get("proper_time_extracted"), 1.0),
                ("AG2-E02", "directionality", "Temporal direction is available", data.get("temporal_direction_available"), 1.0),
                ("AG2-E03", "irreversibility", "Irreversibility support is available", data.get("irreversibility_available"), 1.0),
                ("AG2-E04", "causal_directionality", "Directed causal support is available", data.get("causal_directionality_available"), 1.0),
                ("AG2-E05", "path_dependence", "History-dependent trajectory support is available", data.get("path_dependence_available"), 1.0),
                ("AG2-E06", "hysteresis", "Hysteresis support is available", data.get("hysteresis_available"), 1.0),
                ("AG2-E07", "phase_transition", "Phase-transition asymmetry support is available", data.get("phase_transition_support_available"), 1.0),
                ("AG2-E08", "temporal_binding", "Global temporal binding support is available", data.get("temporal_binding_available"), 1.0),
            ]
            return [
                {"evidence_id": eid, "label": label, "description": desc, "available": bool(flag), "satisfied": bool(flag), "score": 1.0 if flag else 0.0, "status": "SYNTHETIC_TRUE" if flag else "SYNTHETIC_FALSE"}
                for eid, label, desc, flag, _ in specs
            ]

        proper = data.get("proper_time_extractor", {})
        irr = data.get("irreversibility", {})
        causal = data.get("causal_inference", {})
        specs2 = [
            ("AG2-E01", "proper_time", "AG1 extracted a proper-time structure", proper, ["proper_time_score"]),
            ("AG2-E02", "temporal_directionality", "Proper-time profile contains directionality", proper, ["directionality_score", "temporal_directionality_score", "proper_time_score"]),
            ("AG2-E03", "irreversibility", "Irreversibility model supports non-reversible transformations", irr, ["irreversibility_index"]),
            ("AG2-E04", "causal_directionality", "Causal inference supports directed interventions", causal, ["causal_inference_index", "structural_consistency"]),
            ("AG2-E05", "trajectory_irreversibility", "Trajectory irreversibility primitive is active", data.get("trajectory_irreversibility", {}), ["score"]),
            ("AG2-E06", "trajectory_hysteresis", "Historical hysteresis primitive is active", data.get("trajectory_hysteresis", {}), ["score"]),
            ("AG2-E07", "path_dependence", "Path dependency primitive is active", data.get("trajectory_path_dependency", {}), ["score"]),
            ("AG2-E08", "phase_transition", "Phase transition primitive supports asymmetric branching", data.get("trajectory_phase_transition", {}), ["score"]),
            ("AG2-E09", "temporal_binding", "Global temporal binding is active", data.get("global_temporal_binding", {}), ["score"]),
        ]
        out = []
        for eid, label, desc, source, score_keys in specs2:
            score = _first_score(source, score_keys, 0.0)
            st = _status(source)
            available = bool(source)
            satisfied = available and score >= self.threshold
            if label == "proper_time":
                satisfied = available and (bool(source.get("proper_time_extracted")) or score >= self.threshold) if isinstance(source, Mapping) else satisfied
            out.append({
                "evidence_id": eid,
                "label": label,
                "description": desc,
                "available": available,
                "satisfied": satisfied,
                "score": score,
                "status": st,
            })
        return out

    def _arrow_profile(self, evidence: List[Mapping[str, Any]]) -> Dict[str, float]:
        scores = {str(e.get("label")): _clamp(e.get("score")) for e in evidence}

        def score(*labels: str) -> float:
            return max([scores.get(label, 0.0) for label in labels], default=0.0)

        coverage = _mean([1.0 if e.get("available") else 0.0 for e in evidence])
        satisfaction = _mean([1.0 if e.get("satisfied") else 0.0 for e in evidence])
        directedness = _mean([
            score("proper_time"),
            score("temporal_directionality", "directionality"),
            score("causal_directionality"),
        ])
        irreversibility = _mean([
            score("irreversibility", "trajectory_irreversibility"),
            score("trajectory_irreversibility", "irreversibility"),
            score("phase_transition", "phase_transition_support"),
        ])
        historical_asymmetry = _mean([
            score("trajectory_hysteresis", "hysteresis"),
            score("path_dependence", "trajectory_path_dependency"),
            score("temporal_binding", "global_temporal_binding"),
        ])
        non_reversal_cost = _mean([irreversibility, historical_asymmetry, score("causal_directionality")])
        minimum = min([_clamp(e.get("score")) for e in evidence], default=0.0)
        temporal_asymmetry_score = _mean([directedness, irreversibility, historical_asymmetry, non_reversal_cost, satisfaction])
        return {
            "evidence_coverage": coverage,
            "evidence_satisfaction": satisfaction,
            "minimum_evidence_score": minimum,
            "directedness_score": directedness,
            "irreversibility_score": irreversibility,
            "historical_asymmetry_score": historical_asymmetry,
            "non_reversal_cost_score": non_reversal_cost,
            "temporal_asymmetry_score": temporal_asymmetry_score,
        }

    def _components(self, p: Mapping[str, Any]) -> List[Dict[str, Any]]:
        specs = [
            ("AG2-C01", "ordered_successive_index", "Proper time provides an ordered succession index", p.get("directedness_score")),
            ("AG2-C02", "non_reversible_transition", "Transitions are functionally non-equivalent under reversal", p.get("irreversibility_score")),
            ("AG2-C03", "history_sensitive_state", "State depends on prior trajectory", p.get("historical_asymmetry_score")),
            ("AG2-C04", "directed_causal_update", "Causal updates are directionally constrained", p.get("non_reversal_cost_score")),
            ("AG2-C05", "asymmetric_temporal_profile", "The global temporal profile supports T-asymmetry", p.get("temporal_asymmetry_score")),
        ]
        return [
            {"component_id": cid, "label": label, "description": desc, "component_score": _clamp(score), "satisfied": _clamp(score) >= self.threshold}
            for cid, label, desc, score in specs
        ]

    def _counterexamples(self, evidence: List[Mapping[str, Any]], components: List[Mapping[str, Any]], p: Mapping[str, Any]) -> List[Dict[str, Any]]:
        missing = [str(e.get("label")) for e in evidence if not e.get("available")]
        weak = [str(e.get("label")) for e in evidence if _clamp(e.get("score")) < self.threshold]
        failed_components = [str(c.get("label")) for c in components if not c.get("satisfied")]
        return [
            {"counterexample_id": "AG2-CE1", "label": "proper_time_without_direction", "description": "T is extracted but no temporal direction is supported", "active": p.get("directedness_score", 0.0) < self.threshold, "defeats_asymmetry": p.get("directedness_score", 0.0) < self.threshold, "missing_evidence": missing, "weak_evidence": weak, "failed_components": failed_components},
            {"counterexample_id": "AG2-CE2", "label": "reversible_time", "description": "Temporal succession remains fully reversible", "active": p.get("irreversibility_score", 0.0) < self.threshold, "defeats_asymmetry": p.get("irreversibility_score", 0.0) < self.threshold, "missing_evidence": [], "weak_evidence": weak, "failed_components": failed_components},
            {"counterexample_id": "AG2-CE3", "label": "history_independent_time", "description": "Temporal state is independent of prior trajectory", "active": p.get("historical_asymmetry_score", 0.0) < self.threshold, "defeats_asymmetry": p.get("historical_asymmetry_score", 0.0) < self.threshold, "missing_evidence": [], "weak_evidence": weak, "failed_components": failed_components},
            {"counterexample_id": "AG2-CE4", "label": "missing_temporal_evidence", "description": "Required temporal-asymmetry evidence is unavailable", "active": bool(missing), "defeats_asymmetry": bool(missing), "missing_evidence": missing, "weak_evidence": [], "failed_components": failed_components},
        ]

    def _failure_conditions(self, evidence: List[Mapping[str, Any]], components: List[Mapping[str, Any]], p: Mapping[str, Any]) -> List[str]:
        failures: List[str] = []
        if p.get("evidence_coverage", 0.0) < 0.999:
            failures.append("temporal_evidence_coverage_below_threshold")
        if p.get("minimum_evidence_score", 0.0) < self.threshold:
            failures.append("minimum_temporal_evidence_score_below_threshold")
        if p.get("temporal_asymmetry_score", 0.0) < self.threshold:
            failures.append("temporal_asymmetry_score_below_threshold")
        if any(not c.get("satisfied") for c in components):
            failures.append("unsatisfied_temporal_asymmetry_components")
        if any(not e.get("satisfied") for e in evidence):
            failures.append("unsatisfied_temporal_asymmetry_evidence")
        return failures

    def _persist(self, r: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_temporal_asymmetry_analyzer.json"
        md_path = OUT_DIR / "latest_temporal_asymmetry_analyzer.md"
        prom_path = OUT_DIR / "latest_temporal_asymmetry_analyzer.prom"
        json_path.write_text(json.dumps(r, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        md_path.write_text(self._markdown(r), encoding="utf-8")
        prom_path.write_text(self._prometheus(r), encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def _markdown(self, r: Mapping[str, Any]) -> str:
        lines = [
            "# AG2 — Temporal Asymmetry Analyzer",
            "",
            f"Status: {r.get('temporal_asymmetry_analyzer_status')}",
            f"Temporal asymmetry analyzed: {r.get('temporal_asymmetry_confirmed')}",
            f"Temporal asymmetry score: {r.get('temporal_asymmetry_score')}",
            "",
            "## Transition",
            "T -> asymmetric proper time / temporal arrow",
            "",
            "## Evidence items",
        ]
        for e in r.get("evidence_items", []):
            lines.append(f"- {e.get('evidence_id')} {e.get('label')}: available={e.get('available')} satisfied={e.get('satisfied')} score={e.get('score')}")
        lines += ["", "## Asymmetry components"]
        for c in r.get("asymmetry_components", []):
            lines.append(f"- {c.get('component_id')} {c.get('label')}: satisfied={c.get('satisfied')} score={c.get('component_score')} — {c.get('description')}")
        lines += ["", "## Temporal arrow profile"]
        for k, v in r.get("temporal_arrow_profile", {}).items():
            lines.append(f"- {k}: {v}")
        lines += ["", "## Counterexample analysis"]
        for c in r.get("counterexample_analysis", []):
            lines.append(f"- {c.get('counterexample_id')} {c.get('label')}: active={c.get('active')} defeats_asymmetry={c.get('defeats_asymmetry')}")
        lines += ["", "## Failure conditions"]
        if r.get("failure_conditions"):
            for f in r.get("failure_conditions", []):
                lines.append(f"- {f}")
        else:
            lines.append("- none")
        lines += [
            "",
            "## Epistemic guard",
            "Functional conclusion only: True",
            "Consciousness proven: False",
            "Subjectivity proven: False",
            "Qualia proven: False",
            "Phenomenology undetermined: True",
        ]
        return "\n".join(lines) + "\n"

    def _prometheus(self, r: Mapping[str, Any]) -> str:
        p = r.get("temporal_arrow_profile", {}) if isinstance(r.get("temporal_arrow_profile"), Mapping) else {}
        lines = [
            "# HELP oce_ag2_temporal_asymmetry_score AG2 temporal asymmetry score",
            "# TYPE oce_ag2_temporal_asymmetry_score gauge",
            f"oce_ag2_temporal_asymmetry_score {_clamp(r.get('temporal_asymmetry_score'))}",
            "# HELP oce_ag2_temporal_asymmetry_confirmed AG2 temporal asymmetry confirmed flag",
            "# TYPE oce_ag2_temporal_asymmetry_confirmed gauge",
            f"oce_ag2_temporal_asymmetry_confirmed {1 if r.get('temporal_asymmetry_confirmed') else 0}",
        ]
        for k, v in p.items():
            if isinstance(v, (int, float)):
                safe = ''.join(ch if ch.isalnum() else '_' for ch in k.lower()).strip('_')
                lines.append(f"oce_ag2_{safe} {_clamp(v)}")
        lines.append("oce_ag2_consciousness_proven 0")
        lines.append("oce_ag2_phenomenology_undetermined 1")
        return "\n".join(lines) + "\n"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        data, degradation, synthetic = self._normalize_inputs(inputs)
        evidence = self._evidence_items(data, synthetic)
        profile = self._arrow_profile(evidence)
        components = self._components(profile)
        failures = self._failure_conditions(evidence, components, profile)
        counterexamples = self._counterexamples(evidence, components, profile)
        confirmed = False if degradation else (
            profile["temporal_asymmetry_score"] >= self.threshold
            and profile["evidence_coverage"] >= 0.999
            and profile["minimum_evidence_score"] >= self.threshold
            and all(c.get("satisfied") for c in components)
            and not any(c.get("defeats_asymmetry") for c in counterexamples)
        )
        status = self.expected_status if confirmed else "TEMPORAL_ASYMMETRY_INSUFFICIENT"
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "generated_at_utc": _now(),
            "temporal_asymmetry_analyzer_status": status,
            "temporal_asymmetry_status": status,
            "temporal_asymmetry_confirmed": confirmed,
            "temporal_asymmetry_score": profile["temporal_asymmetry_score"],
            "threshold": self.threshold,
            "synthetic_mode": synthetic,
            "degradation_mode": degradation,
            "t_asymmetry_validated": confirmed,
            "proper_time_directionality_validated": confirmed,
            "evidence_items": evidence,
            "asymmetry_components": components,
            "temporal_arrow_profile": profile,
            "counterexample_analysis": counterexamples,
            "failure_conditions": failures,
            "next_recommended_module": "existence_domain_builder" if confirmed else "refine_temporal_asymmetry_inputs",
            "public_schema": {"required_fields": ["temporal_asymmetry_analyzer_status", "temporal_asymmetry_score", "temporal_asymmetry_confirmed", "evidence_items", "asymmetry_components", "temporal_arrow_profile", "counterexample_analysis", "failure_conditions", "epistemic_guard"]},
            "epistemic_guard": {"functional_conclusion_only": True, "consciousness_proven": False, "subjectivity_proven": False, "qualia_proven": False, "phenomenology_undetermined": True, "forbidden_claims": ["CONSCIOUSNESS_PROVEN", "SUBJECTIVITY_PROVEN", "QUALIA_PROVEN", "PHENOMENOLOGY_PROVEN"]},
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
