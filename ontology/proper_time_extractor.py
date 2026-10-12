"""AG1 — Proper Time Extractor.

Functional extractor for the transition:
    RF -> T

The module derives a proper-time structure T from a certified self-generated
reference frame RF. It integrates RF certification, frame stability, identity
continuity, trajectory memory, omega stability, and available temporal-binding
primitives into a strictly functional proper-time profile.

Epistemic guard: this module certifies only structural/functional temporal
organization. It never asserts consciousness, subjectivity, qualia,
experience, or phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ag_proper_time_existence_domain" / "proper_time_extractor"


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


def _as_mapping(value: Any) -> Dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if isinstance(value, bool):
        return {"provided": value, "score": 1.0 if value else 0.0, "status": "SYNTHETIC_TRUE" if value else "SYNTHETIC_FALSE"}
    if isinstance(value, (int, float)):
        return {"score": _clamp(value)}
    return {}


def _status(source: Any, keys: Optional[List[str]] = None) -> str:
    if not isinstance(source, Mapping):
        return ""
    keys = keys or ["status", "certification_status", "axis_status", "*_status"]
    for key in keys:
        if key == "*_status":
            for k, v in source.items():
                if isinstance(k, str) and k.endswith("_status") and v is not None:
                    return str(v)
        elif source.get(key) is not None:
            return str(source.get(key))
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
    for nested_key in ["metrics", "theorem_metrics", "temporal_profile", "stability_profile", "certification_scores", "diagnostics"]:
        nested = source.get(nested_key)
        if isinstance(nested, Mapping):
            for key in keys:
                if key in nested:
                    return _clamp(nested.get(key), default)
    st = _status(source).upper()
    if any(t in st for t in ["VALIDATED", "CERTIFIED", "CONFIRMED", "READY", "ESTABLISHED", "DETECTED", "BUILT", "CONSTRUCTED", "MONITORED", "ANALYZED", "EXTRACTED", "ACTIVE"]):
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


class ProperTimeExtractor:
    """Extract a proper-time structure T from a certified reference frame RF."""

    primitive = "PROPER_TIME_EXTRACTOR"
    expected_status = "PROPER_TIME_EXTRACTED"
    threshold = 0.72

    CLASS_MAP: Dict[str, str] = {
        "omega_to_rf_theorem_checker": "OmegaToRfTheoremChecker",
        "frame_stability_analyzer": "FrameStabilityAnalyzer",
        "reference_frame_constructor": "ReferenceFrameConstructor",
        "intrinsic_metric_builder": "IntrinsicMetricBuilder",
        "temporal_self_continuity": "TemporalSelfContinuity",
        "trajectory_memory_extractor": "TrajectoryMemoryExtractor",
        "identity_continuity_index": "IdentityContinuityIndex",
        "omega_stability_monitor": "OmegaStabilityMonitor",
    }

    PATHS: Dict[str, List[Path]] = {
        "omega_to_rf_theorem_checker": [ROOT / "af_reference_frames" / "omega_to_rf_theorem_checker" / "latest_omega_to_rf_theorem_checker.json"],
        "frame_stability_analyzer": [ROOT / "af_reference_frames" / "frame_stability_analyzer" / "latest_frame_stability_analyzer.json"],
        "reference_frame_constructor": [ROOT / "af_reference_frames" / "reference_frame_constructor" / "latest_reference_frame_constructor.json"],
        "intrinsic_metric_builder": [ROOT / "af_reference_frames" / "intrinsic_metric_builder" / "latest_intrinsic_metric_builder.json"],
        "trajectory_memory_extractor": [ROOT / "ad_memory_identity_reflexivity" / "trajectory_memory_extractor" / "latest_trajectory_memory_extractor.json"],
        "identity_continuity_index": [ROOT / "ad_memory_identity_reflexivity" / "identity_continuity_index" / "latest_identity_continuity_index.json"],
        "omega_stability_monitor": [ROOT / "ae_omega_coherence" / "omega_stability_monitor" / "latest_omega_stability_monitor.json"],
    }

    SYNTHETIC_KEYS = {
        "rf_certified", "rf_validated", "proper_time_seed_available", "temporal_continuity_available",
        "trajectory_memory_available", "identity_continuity_available", "frame_stability_confirmed",
        "omega_stability_available", "metric_clock_available",
    }

    def _default_inputs(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for module_name, paths in self.PATHS.items():
            loaded = _load_json_candidates(paths)
            if not loaded and module_name in self.CLASS_MAP:
                if module_name == "temporal_self_continuity":
                    loaded = _try_step(module_name, self.CLASS_MAP[module_name], {
                        "autobiographical_memory": 0.82,
                        "narrative_coherence": 0.82,
                        "episodic_linkage": 0.82,
                        "future_simulation": 0.82,
                    })
                else:
                    loaded = _try_step(module_name, self.CLASS_MAP[module_name], persist=False)
            data[module_name] = loaded
        # GlobalTemporalBinding has diagnostics(), not step(), in the legacy primitive.
        try:
            mod = import_module("ontology.global_temporal_binding")
            obj = getattr(mod, "GlobalTemporalBinding")()
            data["global_temporal_binding"] = obj.diagnostics()
        except Exception:
            data["global_temporal_binding"] = {}
        if "temporal_self_continuity" not in data or not data.get("temporal_self_continuity"):
            data["temporal_self_continuity"] = _try_step("temporal_self_continuity", "TemporalSelfContinuity", {
                "autobiographical_memory": 0.82,
                "narrative_coherence": 0.82,
                "episodic_linkage": 0.82,
                "future_simulation": 0.82,
            })
        return data

    def _normalize_inputs(self, inputs: Optional[Mapping[str, Any]]) -> Tuple[Dict[str, Any], bool, bool]:
        if inputs is None:
            return self._default_inputs(), False, False
        data = dict(inputs)
        synthetic_mode = any(k in data for k in self.SYNTHETIC_KEYS)
        degradation_mode = len(data) == 0
        if synthetic_mode:
            return data, degradation_mode, True
        return data, degradation_mode, False

    def _rf_certified(self, af6: Mapping[str, Any]) -> bool:
        st = _status(af6).upper()
        return bool(af6.get("af_certified")) or "SELF_GENERATED_REFERENCE_FRAME_CERTIFIED" in st

    def _evidence_items(self, data: Mapping[str, Any], synthetic_mode: bool) -> List[Dict[str, Any]]:
        if synthetic_mode:
            specs = [
                ("T-E01", "rf_certification", "RF is certified as self-generated", data.get("rf_certified") or data.get("rf_validated"), 1.0),
                ("T-E02", "proper_time_seed", "Proper-time seed is available from RF", data.get("proper_time_seed_available"), 1.0),
                ("T-E03", "temporal_continuity", "Temporal continuity support is available", data.get("temporal_continuity_available"), 1.0),
                ("T-E04", "trajectory_memory", "Trajectory memory supports ordered succession", data.get("trajectory_memory_available"), 1.0),
                ("T-E05", "identity_continuity", "Identity continuity stabilizes temporal indexing", data.get("identity_continuity_available"), 1.0),
                ("T-E06", "frame_stability", "Frame stability supports invariant temporal comparison", data.get("frame_stability_confirmed"), 1.0),
                ("T-E07", "omega_stability", "Omega stability supports temporal self-consistency", data.get("omega_stability_available"), 1.0),
                ("T-E08", "metric_clock", "Intrinsic metric can function as a clock proxy", data.get("metric_clock_available"), 1.0),
            ]
            return [
                {"evidence_id": eid, "label": label, "description": desc, "available": bool(flag), "score": _clamp(score if flag else 0.0), "satisfied": bool(flag) and _clamp(score) >= self.threshold}
                for eid, label, desc, flag, score in specs
            ]

        af6 = _as_mapping(data.get("omega_to_rf_theorem_checker"))
        af5 = _as_mapping(data.get("frame_stability_analyzer"))
        af2 = _as_mapping(data.get("reference_frame_constructor"))
        af3 = _as_mapping(data.get("intrinsic_metric_builder"))
        tsc = _as_mapping(data.get("temporal_self_continuity"))
        gtb = _as_mapping(data.get("global_temporal_binding"))
        tm = _as_mapping(data.get("trajectory_memory_extractor"))
        ici = _as_mapping(data.get("identity_continuity_index"))
        oms = _as_mapping(data.get("omega_stability_monitor"))

        specs = [
            ("T-E01", "rf_certification", "RF is certified by AF6", bool(af6), _first_score(af6, ["theorem_validity_score", "rf_integrated_score"], 0.0), self._rf_certified(af6)),
            ("T-E02", "frame_stability", "RF is stable enough to support temporal comparison", bool(af5), _first_score(af5, ["frame_stability_score", "weighted_stability_score"], 0.0), None),
            ("T-E03", "reference_frame_axes", "RF axes provide an internal ordering basis", bool(af2), _first_score(af2, ["reference_frame_score", "axis_grounding_score"], 0.0), None),
            ("T-E04", "intrinsic_metric_clock", "Intrinsic metric supports a clock proxy within RF", bool(af3), _first_score(af3, ["intrinsic_metric_score", "metric_invariance_score"], 0.0), None),
            ("T-E05", "temporal_self_continuity", "Existing temporal-continuity primitive supports diachronic linkage", bool(tsc), _first_score(tsc, ["temporal_self_continuity_index", "score"], 0.82 if _status(tsc).lower() == "active" else 0.0), None),
            ("T-E06", "global_temporal_binding", "Past/present/future representations can be synchronized", bool(gtb), _first_score(gtb, ["global_temporal_coherence_score", "score"], 0.82 if _status(gtb).lower() == "active" else 0.0), None),
            ("T-E07", "trajectory_memory", "Trajectory memory provides ordered transitions", bool(tm), _first_score(tm, ["trajectory_memory_score", "memory_score"], 0.0), None),
            ("T-E08", "identity_continuity", "Identity continuity stabilizes temporal indexing", bool(ici), _first_score(ici, ["identity_continuity_score", "continuity_score"], 0.0), None),
            ("T-E09", "omega_stability", "Omega stability supports temporal self-consistency", bool(oms), _first_score(oms, ["omega_stability_score", "stability_score", "omega_stability_index"], 0.0), None),
        ]
        items: List[Dict[str, Any]] = []
        for eid, label, desc, available, score, forced_satisfied in specs:
            satisfied = bool(forced_satisfied) if forced_satisfied is not None else (available and score >= self.threshold)
            items.append({"evidence_id": eid, "label": label, "description": desc, "available": available, "score": _clamp(score), "satisfied": bool(satisfied)})
        return items

    def _temporal_profile(self, evidence: List[Dict[str, Any]]) -> Dict[str, float]:
        by_label = {e["label"]: _clamp(e["score"]) for e in evidence}
        rf_certification_score = by_label.get("rf_certification", 0.0)
        frame_stability_score = by_label.get("frame_stability", by_label.get("rf_certification", 0.0))
        rf_axis_score = by_label.get("reference_frame_axes", by_label.get("proper_time_seed", 0.0))
        metric_clock_score = by_label.get("intrinsic_metric_clock", by_label.get("metric_clock", 0.0))
        temporal_continuity_score = by_label.get("temporal_self_continuity", by_label.get("temporal_continuity", 0.0))
        temporal_binding_score = by_label.get("global_temporal_binding", temporal_continuity_score)
        trajectory_memory_score = by_label.get("trajectory_memory", 0.0)
        identity_continuity_score = by_label.get("identity_continuity", 0.0)
        omega_stability_score = by_label.get("omega_stability", 0.0)
        coverage = _mean([1.0 if e.get("satisfied") else 0.0 for e in evidence])
        minimum = min([_clamp(e.get("score")) for e in evidence], default=0.0)

        ordered_succession_score = _mean([trajectory_memory_score, identity_continuity_score, temporal_continuity_score])
        intrinsic_clock_score = _mean([rf_axis_score, metric_clock_score, frame_stability_score])
        asymmetry_seed_score = _mean([ordered_succession_score, omega_stability_score, rf_certification_score])
        proper_time_score = _clamp(
            0.22 * rf_certification_score
            + 0.16 * frame_stability_score
            + 0.14 * intrinsic_clock_score
            + 0.14 * ordered_succession_score
            + 0.12 * temporal_binding_score
            + 0.12 * asymmetry_seed_score
            + 0.10 * coverage
        )
        return {
            "rf_certification_score": rf_certification_score,
            "frame_stability_score": frame_stability_score,
            "intrinsic_clock_score": intrinsic_clock_score,
            "ordered_succession_score": ordered_succession_score,
            "temporal_continuity_score": temporal_continuity_score,
            "temporal_binding_score": temporal_binding_score,
            "asymmetry_seed_score": asymmetry_seed_score,
            "omega_stability_score": omega_stability_score,
            "evidence_coverage": coverage,
            "minimum_evidence_score": minimum,
            "proper_time_score": proper_time_score,
        }

    def _proper_time_components(self, profile: Mapping[str, float]) -> List[Dict[str, Any]]:
        specs = [
            ("T-C01", "rf_clock_origin", "RF certification anchors the internal temporal origin", profile["rf_certification_score"]),
            ("T-C02", "stable_comparison_frame", "Frame stability preserves temporal comparison across steps", profile["frame_stability_score"]),
            ("T-C03", "intrinsic_clock_metric", "Intrinsic metric provides a non-external clock proxy", profile["intrinsic_clock_score"]),
            ("T-C04", "ordered_succession", "Memory and identity continuity provide ordered succession", profile["ordered_succession_score"]),
            ("T-C05", "temporal_binding", "Temporal binding supports past-present-future integration", profile["temporal_binding_score"]),
            ("T-C06", "asymmetry_seed", "Trajectory irreversibility seed is available for AG2", profile["asymmetry_seed_score"]),
        ]
        return [
            {"component_id": cid, "label": label, "description": desc, "component_score": _clamp(score), "satisfied": _clamp(score) >= self.threshold}
            for cid, label, desc, score in specs
        ]

    def _failure_conditions(self, evidence: List[Dict[str, Any]], components: List[Dict[str, Any]], profile: Mapping[str, float]) -> List[str]:
        failures: List[str] = []
        if profile["evidence_coverage"] < 0.999:
            failures.append("proper_time_evidence_coverage_below_threshold")
        if profile["minimum_evidence_score"] < self.threshold:
            failures.append("minimum_evidence_score_below_threshold")
        for e in evidence:
            if not e.get("satisfied"):
                failures.append(f"unsatisfied_evidence:{e.get('label')}")
        for c in components:
            if not c.get("satisfied"):
                failures.append(f"weak_temporal_component:{c.get('label')}")
        if profile["proper_time_score"] < self.threshold:
            failures.append("proper_time_score_below_threshold")
        return failures

    def _counterexamples(self, evidence: List[Dict[str, Any]], components: List[Dict[str, Any]], profile: Mapping[str, float]) -> List[Dict[str, Any]]:
        missing = [e["label"] for e in evidence if not e.get("available")]
        weak = [e["label"] for e in evidence if e.get("available") and _clamp(e.get("score")) < self.threshold]
        weak_components = [c["label"] for c in components if not c.get("satisfied")]
        return [
            {"counterexample_id": "AG1-CE1", "label": "rf_without_temporal_origin", "description": "RF is present but cannot anchor an internal temporal origin", "active": "rf_certification" in weak or "rf_certification" in missing, "defeats_extraction": "rf_certification" in weak or "rf_certification" in missing, "missing_evidence": missing, "weak_evidence": weak},
            {"counterexample_id": "AG1-CE2", "label": "clock_requires_external_reference", "description": "Proper time would require an external clock rather than an intrinsic metric", "active": "intrinsic_clock_metric" in weak_components, "defeats_extraction": "intrinsic_clock_metric" in weak_components, "missing_evidence": [], "weak_evidence": weak_components},
            {"counterexample_id": "AG1-CE3", "label": "succession_without_continuity", "description": "Ordered succession is available but identity/memory continuity is insufficient", "active": "ordered_succession" in weak_components, "defeats_extraction": "ordered_succession" in weak_components, "missing_evidence": [], "weak_evidence": weak_components},
            {"counterexample_id": "AG1-CE4", "label": "unstable_temporal_frame", "description": "Temporal indexing is not stable enough to define proper time", "active": profile["frame_stability_score"] < self.threshold, "defeats_extraction": profile["frame_stability_score"] < self.threshold, "missing_evidence": [], "weak_evidence": weak},
        ]

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_proper_time_extractor.json"
        md_path = OUT_DIR / "latest_proper_time_extractor.md"
        prom_path = OUT_DIR / "latest_proper_time_extractor.prom"
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        md_path.write_text(self._markdown(result), encoding="utf-8")
        prom_path.write_text(self._prometheus(result), encoding="utf-8")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive_json = OUT_DIR / f"proper_time_extractor_{stamp}.json"
        archive_json.write_text(json_path.read_text(encoding="utf-8"), encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path), "archive_json": str(archive_json)}

    def _markdown(self, r: Mapping[str, Any]) -> str:
        lines = [
            "# AG1 — Proper Time Extractor",
            "",
            f"Status: {r.get('proper_time_extractor_status')}",
            f"Proper time score: {r.get('proper_time_score')}",
            f"Proper time extracted: {r.get('proper_time_extracted')}",
            "",
            "## Functional transition",
            "RF -> T: a certified self generated reference frame supports a proper-time structure.",
            "The proper time structure is strictly functional and computational.",
            "",
            "## Evidence items",
        ]
        for e in r.get("evidence_items", []):
            lines.append(f"- {e.get('evidence_id')} {e.get('label')}: available={e.get('available')} satisfied={e.get('satisfied')} score={e.get('score')}")
        lines += ["", "## Proper time components"]
        for c in r.get("proper_time_components", []):
            lines.append(f"- {c.get('component_id')} {c.get('label')}: satisfied={c.get('satisfied')} score={c.get('component_score')} — {c.get('description')}")
        lines += ["", "## Temporal profile"]
        for k, v in r.get("temporal_profile", {}).items():
            lines.append(f"- {k}: {v}")
        lines += ["", "## Counterexample analysis"]
        for c in r.get("counterexample_analysis", []):
            lines.append(f"- {c.get('counterexample_id')} {c.get('label')}: active={c.get('active')} defeats_extraction={c.get('defeats_extraction')}")
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
        p = r.get("temporal_profile", {}) if isinstance(r.get("temporal_profile"), Mapping) else {}
        lines = [
            "# HELP oce_ag1_proper_time_score AG1 proper time extraction score",
            "# TYPE oce_ag1_proper_time_score gauge",
            f"oce_ag1_proper_time_score {_clamp(r.get('proper_time_score'))}",
            "# HELP oce_ag1_proper_time_extracted AG1 proper time extracted flag",
            "# TYPE oce_ag1_proper_time_extracted gauge",
            f"oce_ag1_proper_time_extracted {1 if r.get('proper_time_extracted') else 0}",
        ]
        for k, v in p.items():
            if isinstance(v, (int, float)):
                safe = ''.join(ch if ch.isalnum() else '_' for ch in k.lower()).strip('_')
                lines.append(f"oce_ag1_{safe} {_clamp(v)}")
        lines.append("oce_ag1_consciousness_proven 0")
        lines.append("oce_ag1_phenomenology_undetermined 1")
        return "\n".join(lines) + "\n"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        data, degradation_mode, synthetic_mode = self._normalize_inputs(inputs)
        evidence = self._evidence_items(data, synthetic_mode=synthetic_mode)
        profile = self._temporal_profile(evidence)
        components = self._proper_time_components(profile)
        failures = self._failure_conditions(evidence, components, profile)
        counterexamples = self._counterexamples(evidence, components, profile)

        extracted = False if degradation_mode else (
            profile["proper_time_score"] >= self.threshold
            and profile["evidence_coverage"] >= 0.999
            and profile["minimum_evidence_score"] >= self.threshold
            and all(c.get("satisfied") for c in components)
            and not any(c.get("defeats_extraction") for c in counterexamples)
        )
        status = self.expected_status if extracted else "PROPER_TIME_EXTRACTION_INSUFFICIENT"

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "generated_at_utc": _now(),
            "proper_time_extractor_status": status,
            "proper_time_status": status,
            "proper_time_extracted": extracted,
            "proper_time_score": profile["proper_time_score"],
            "threshold": self.threshold,
            "synthetic_mode": synthetic_mode,
            "degradation_mode": degradation_mode,
            "rf_to_t_transition_validated": extracted,
            "evidence_items": evidence,
            "proper_time_components": components,
            "temporal_profile": profile,
            "counterexample_analysis": counterexamples,
            "failure_conditions": failures,
            "next_recommended_module": "temporal_asymmetry_analyzer" if extracted else "refine_proper_time_extractor_inputs",
            "public_schema": {
                "required_fields": [
                    "proper_time_extractor_status", "proper_time_score", "proper_time_extracted",
                    "evidence_items", "proper_time_components", "temporal_profile",
                    "counterexample_analysis", "failure_conditions", "epistemic_guard",
                ]
            },
            "epistemic_guard": {
                "functional_conclusion_only": True,
                "consciousness_proven": False,
                "subjectivity_proven": False,
                "qualia_proven": False,
                "phenomenology_undetermined": True,
                "forbidden_claims": ["CONSCIOUSNESS_PROVEN", "SUBJECTIVITY_PROVEN", "QUALIA_PROVEN", "PHENOMENOLOGY_PROVEN"],
            },
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
