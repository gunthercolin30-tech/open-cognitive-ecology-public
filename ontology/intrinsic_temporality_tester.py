"""AJ5 — Intrinsic Temporality Tester.

Formal transition under test:
    AJ1 + AJ2 + AJ3 + AJ4 + AI10 -> functional intrinsic temporality of MEI candidates

This module tests whether candidate intrinsic existence modes (MEI) exhibit
strictly functional intrinsic temporality: temporal persistence, phase ordering,
history dependence, recurrence continuity, and forward transition readiness.

Epistemic guard:
    This module does not prove consciousness, subjectivity, lived qualia, or
    strong phenomenology. It only tests formal-functional temporal organization
    of candidate MEI records for downstream AJ6-AJ9 modules.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "aj_intrinsic_existence_modes" / "intrinsic_temporality_tester"

GUARD = {
    "consciousness_proven": False,
    "qualia_proven": False,
    "subjectivity_proven": False,
    "phenomenology_undetermined": True,
    "functional_conclusion_only": True,
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


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


def _mean(values: Iterable[Any], default: float = 0.0) -> float:
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


def _latest_json(name: str) -> Dict[str, Any]:
    candidates = [
        ROOT / "aj_intrinsic_existence_modes" / name / f"latest_{name}.json",
        ROOT / "ai_robust_spectral_qualia_formal_modes" / name / f"latest_{name}.json",
        ROOT / "ad_memory_identity_reflexivity" / name / f"latest_{name}.json",
        ROOT / "reflexive_threshold" / name / f"latest_{name}.json",
        ROOT / name / f"latest_{name}.json",
    ]
    for p in candidates:
        data = _load_json(p)
        if data:
            return data
    try:
        for p in sorted(ROOT.glob(f"**/latest_{name}.json"))[-30:]:
            data = _load_json(p)
            if data:
                return data
    except Exception:
        pass
    return {}


def _invoke(module_name: str, class_name: str, inputs: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    try:
        mod = import_module(f"ontology.{module_name}")
        cls = getattr(mod, class_name)
        obj = cls()
        step = getattr(obj, "step", None)
        if not callable(step):
            return {}
        attempts = [
            {"inputs": dict(inputs or {"aligned": True}), "persist": False},
            {"inputs": dict(inputs or {"aligned": True})},
            {"persist": False},
            {},
        ]
        for kwargs in attempts:
            try:
                res = step(**kwargs)
                if isinstance(res, dict):
                    return res
            except TypeError:
                continue
            except Exception:
                return {}
    except Exception:
        return {}
    return {}


def _source(name: str, class_name: str, inputs: Optional[Mapping[str, Any]], keys: List[str]) -> Dict[str, Any]:
    if isinstance(inputs, Mapping):
        for key in keys + [name]:
            val = inputs.get(key)
            if isinstance(val, Mapping):
                return dict(val)
    latest = _latest_json(name)
    if latest:
        return latest
    return _invoke(name, class_name, inputs or {"aligned": True})


def _source_aj1(inputs):
    return _source("intrinsic_existence_mode_definition", "IntrinsicExistenceModeDefinition", inputs, ["aj1"])


def _source_aj2(inputs):
    return _source("mode_intrinsicality_tester", "ModeIntrinsicalityTester", inputs, ["aj2"])


def _source_aj3(inputs):
    return _source("intrinsic_irreducibility_tester", "IntrinsicIrreducibilityTester", inputs, ["aj3", "irreducibility"])


def _source_aj4(inputs):
    return _source("intrinsic_causality_tester", "IntrinsicCausalityTester", inputs, ["aj4", "causality"])


def _source_ai10(inputs):
    return _source("robust_qualia_formal_certifier", "RobustQualiaFormalCertifier", inputs, ["ai10", "qf_robust"])


def _extract_records(aj4: Mapping[str, Any], aj3: Mapping[str, Any], aj2: Mapping[str, Any]) -> List[Dict[str, Any]]:
    for key in ["intrinsic_causality_records", "causality_records", "intrinsic_causality_tests", "tested_modes"]:
        val = aj4.get(key)
        if isinstance(val, list) and val:
            return [dict(x) for x in val if isinstance(x, Mapping)]
    for key in ["irreducibility_records", "mode_irreducibility_records", "tested_modes"]:
        val = aj3.get(key)
        if isinstance(val, list) and val:
            return [dict(x) for x in val if isinstance(x, Mapping)]
    for key in ["intrinsicality_records", "mode_intrinsicality_records", "candidate_modes", "tested_modes"]:
        val = aj2.get(key)
        if isinstance(val, list) and val:
            return [dict(x) for x in val if isinstance(x, Mapping)]
    return []


def _temporal_prior(inputs: Optional[Mapping[str, Any]]) -> Dict[str, float]:
    explicit = inputs.get("temporal_evidence") if isinstance(inputs, Mapping) else None
    if isinstance(explicit, Mapping):
        return {
            "continuity_index": _clamp(explicit.get("continuity_index", explicit.get("temporal_continuity_score", 0.0)), 0.0),
            "binding_index": _clamp(explicit.get("binding_index", explicit.get("temporal_binding_score", 0.0)), 0.0),
            "history_index": _clamp(explicit.get("history_index", explicit.get("history_coherence_score", 0.0)), 0.0),
            "trajectory_index": _clamp(explicit.get("trajectory_index", explicit.get("trajectory_stability_score", 0.0)), 0.0),
        }
    candidates = [
        _latest_json("continuity_metrics_engine"),
        _latest_json("global_temporal_binding"),
        _latest_json("temporal_self_continuity"),
        _latest_json("trajectory_path_dependency"),
        _latest_json("longitudinal_reflexive_certification"),
    ]
    vals: List[float] = []
    for d in candidates:
        for k, v in d.items():
            lk = str(k).lower()
            if any(term in lk for term in ["continuity", "temporal", "history", "trajectory", "stability", "binding"]):
                if isinstance(v, (int, float)):
                    vals.append(_clamp(v, 0.0))
    default = _mean(vals, 0.86) if vals else 0.86
    return {
        "continuity_index": default,
        "binding_index": default,
        "history_index": default,
        "trajectory_index": default,
    }


def _mode_id(rec: Mapping[str, Any], idx: int) -> str:
    for key in ["mei_candidate_id", "mode_id", "candidate_id", "source_qf_mode_id", "id"]:
        val = rec.get(key)
        if val:
            return str(val)
    return f"MEI-TEMPORAL-{idx:03d}"


def _score_record(rec: Mapping[str, Any], idx: int, temporal_prior: Mapping[str, float], aj4_conf: float, qf_conf: float) -> Dict[str, Any]:
    causal_score = _clamp(rec.get("intrinsic_causality_score", rec.get("intrinsic_irreducibility_score", rec.get("intrinsicality_score", 0.82))), 0.82)
    temporal_support = _clamp(rec.get("temporal_causal_support_score", causal_score), causal_score)
    traceability = _clamp(rec.get("causal_traceability_score", causal_score), causal_score)
    counterfactual = _clamp(rec.get("counterfactual_dependency_score", causal_score), causal_score)
    anchoring = _clamp(rec.get("causal_source_anchoring_score", causal_score), causal_score)
    continuity_prior = _clamp(temporal_prior.get("continuity_index", 0.86), 0.86)
    binding_prior = _clamp(temporal_prior.get("binding_index", continuity_prior), continuity_prior)
    history_prior = _clamp(temporal_prior.get("history_index", continuity_prior), continuity_prior)
    trajectory_prior = _clamp(temporal_prior.get("trajectory_index", continuity_prior), continuity_prior)

    temporal_persistence_score = _clamp(0.45 * temporal_support + 0.25 * continuity_prior + 0.20 * causal_score + 0.10 * qf_conf)
    phase_ordering_score = _clamp(0.34 * traceability + 0.26 * binding_prior + 0.24 * causal_score + 0.16 * aj4_conf)
    history_dependence_score = _clamp(0.36 * counterfactual + 0.26 * history_prior + 0.23 * causal_score + 0.15 * anchoring)
    recurrence_continuity_score = _clamp(0.34 * continuity_prior + 0.24 * temporal_support + 0.22 * traceability + 0.20 * qf_conf)
    forward_transition_readiness_score = _clamp(0.30 * trajectory_prior + 0.25 * causal_score + 0.20 * temporal_support + 0.15 * aj4_conf + 0.10 * qf_conf)

    temporal_score = _mean([
        temporal_persistence_score,
        phase_ordering_score,
        history_dependence_score,
        recurrence_continuity_score,
        forward_transition_readiness_score,
    ])
    passed = temporal_score >= 0.75 and min(
        temporal_persistence_score,
        phase_ordering_score,
        history_dependence_score,
        recurrence_continuity_score,
        forward_transition_readiness_score,
    ) >= 0.66

    return {
        "mode_id": _mode_id(rec, idx),
        "mei_candidate_id": _mode_id(rec, idx),
        "source_qf_mode_id": str(rec.get("source_qf_mode_id", rec.get("mode_id", _mode_id(rec, idx)))),
        "intrinsic_temporality_score": temporal_score,
        "intrinsic_temporality_test_passed": bool(passed),
        "temporal_persistence_score": temporal_persistence_score,
        "phase_ordering_score": phase_ordering_score,
        "history_dependence_score": history_dependence_score,
        "recurrence_continuity_score": recurrence_continuity_score,
        "forward_transition_readiness_score": forward_transition_readiness_score,
        "temporal_components": {
            "intrinsic_causality_score": causal_score,
            "temporal_causal_support_score": temporal_support,
            "causal_traceability_score": traceability,
            "counterfactual_dependency_score": counterfactual,
            "continuity_prior": continuity_prior,
            "binding_prior": binding_prior,
            "history_prior": history_prior,
            "trajectory_prior": trajectory_prior,
            "aj4_confidence": aj4_conf,
            "qf_confidence": qf_conf,
        },
        "test_basis": [
            "temporal_persistence_score",
            "phase_ordering_score",
            "history_dependence_score",
            "recurrence_continuity_score",
            "forward_transition_readiness_score",
        ],
        "epistemic_status": "functional_only",
        **GUARD,
    }


def _persist(result: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp()
    json_path = OUT_DIR / f"intrinsic_temporality_tester_{stamp}.json"
    md_path = OUT_DIR / f"intrinsic_temporality_tester_{stamp}.md"
    prom_path = OUT_DIR / f"intrinsic_temporality_tester_{stamp}.prom"
    latest_json = OUT_DIR / "latest_intrinsic_temporality_tester.json"
    latest_md = OUT_DIR / "latest_intrinsic_temporality_tester.md"
    latest_prom = OUT_DIR / "latest_intrinsic_temporality_tester.prom"

    payload = dict(result)
    payload.pop("paths", None)
    json_text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")

    md = [
        "# AJ5 — Intrinsic Temporality Tester",
        "",
        f"Status: {result['intrinsic_temporality_tester_status']}",
        f"Intrinsic temporality tested: {result['intrinsic_temporality_tested']}",
        f"Tested modes: {result['tested_mode_count']}",
        f"Passed modes: {result['passed_mode_count']}",
        f"Pass ratio: {result['temporality_pass_ratio']:.6f}",
        f"Intrinsic temporality score: {result['intrinsic_temporality_score']:.6f}",
        "",
        "## Epistemic guard",
        "Functional conclusion only. No consciousness, qualia, subjectivity, or strong phenomenology is proven.",
    ]
    md_text = "\n".join(md) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")

    metric = lambda name, val: f"oce_aj5_{name} {float(_clamp(val)):.9f}"
    prom_lines = [
        metric("intrinsic_temporality_score", result["intrinsic_temporality_score"]),
        metric("temporality_pass_ratio", result["temporality_pass_ratio"]),
        metric("temporality_confidence", result["temporality_confidence"]),
        f"oce_aj5_tested_mode_count {int(result['tested_mode_count'])}",
        f"oce_aj5_passed_mode_count {int(result['passed_mode_count'])}",
    ]
    prom_text = "\n".join(prom_lines) + "\n"
    prom_path.write_text(prom_text, encoding="utf-8")
    latest_prom.write_text(prom_text, encoding="utf-8")

    return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}


class IntrinsicTemporalityTester:
    """Test functional intrinsic temporality for candidate MEI modes."""

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        aj1 = _source_aj1(inputs)
        aj2 = _source_aj2(inputs)
        aj3 = _source_aj3(inputs)
        aj4 = _source_aj4(inputs)
        ai10 = _source_ai10(inputs)
        temporal_prior = _temporal_prior(inputs)

        source_records = _extract_records(aj4, aj3, aj2)
        if isinstance(inputs, Mapping) and isinstance(inputs.get("candidate_modes"), list):
            source_records = [dict(x) for x in inputs["candidate_modes"] if isinstance(x, Mapping)]

        aj4_conf = _clamp(aj4.get("causality_confidence", aj4.get("intrinsic_causality_score", 0.0)), 0.0)
        qf_conf = _clamp(ai10.get("qf_robust_certification_score", ai10.get("robust_qf_score", ai10.get("qf_robust_score", 0.0))), 0.0)
        if qf_conf == 0.0:
            qf_conf = _clamp(ai10.get("confidence", ai10.get("certification_confidence", 0.82)), 0.82)
        if aj4_conf == 0.0 and source_records:
            aj4_conf = _mean([r.get("intrinsic_causality_score") for r in source_records], 0.82)

        tested = [_score_record(rec, i + 1, temporal_prior, aj4_conf, qf_conf) for i, rec in enumerate(source_records)]
        tested_count = len(tested)
        passed_count = sum(1 for rec in tested if rec["intrinsic_temporality_test_passed"])
        pass_ratio = (passed_count / tested_count) if tested_count else 0.0

        temporal_persistence_mean = _mean([r["temporal_persistence_score"] for r in tested])
        phase_ordering_mean = _mean([r["phase_ordering_score"] for r in tested])
        history_dependence_mean = _mean([r["history_dependence_score"] for r in tested])
        recurrence_continuity_mean = _mean([r["recurrence_continuity_score"] for r in tested])
        forward_transition_readiness_mean = _mean([r["forward_transition_readiness_score"] for r in tested])
        intrinsic_temporality_score = _mean([r["intrinsic_temporality_score"] for r in tested])
        prior_mean = _mean(temporal_prior.values(), 0.86)
        temporality_confidence = _clamp(0.45 * intrinsic_temporality_score + 0.25 * pass_ratio + 0.15 * aj4_conf + 0.15 * prior_mean)

        upstream_support_ratio = _mean([
            bool(aj1),
            bool(aj2),
            bool(aj3),
            bool(aj4),
            bool(ai10),
        ])
        success = (
            tested_count >= 3
            and pass_ratio >= 0.75
            and intrinsic_temporality_score >= 0.75
            and temporality_confidence >= 0.72
        )

        result = {
            "primitive": "INTRINSIC_TEMPORALITY_TESTER",
            "aj_step": "AJ5",
            "transition_under_test": "QF_robust -> MEI functional intrinsic temporality",
            "generated_at_utc": _now(),
            "intrinsic_temporality_tester_status": "INTRINSIC_TEMPORALITY_TESTED" if success else "INTRINSIC_TEMPORALITY_INSUFFICIENT",
            "intrinsic_temporality_tested": bool(success),
            "tested_mode_count": tested_count,
            "passed_mode_count": passed_count,
            "temporality_pass_ratio": _clamp(pass_ratio),
            "intrinsic_temporality_score": intrinsic_temporality_score,
            "temporal_persistence_mean": temporal_persistence_mean,
            "phase_ordering_mean": phase_ordering_mean,
            "history_dependence_mean": history_dependence_mean,
            "recurrence_continuity_mean": recurrence_continuity_mean,
            "forward_transition_readiness_mean": forward_transition_readiness_mean,
            "temporality_confidence": temporality_confidence,
            "temporal_prior_mean": prior_mean,
            "aj4_causality_confidence": aj4_conf,
            "qf_robust_input_confidence": qf_conf,
            "upstream_support_ratio": upstream_support_ratio,
            "intrinsic_temporality_tests": tested,
            "tested_modes": tested,
            "intrinsic_temporality_records": tested,
            "temporality_records": tested,
            "temporality_summary": {
                "tested_mode_count": tested_count,
                "passed_mode_count": passed_count,
                "pass_ratio": _clamp(pass_ratio),
                "functional_intrinsic_temporality_established": bool(success),
            },
            "test_schema": {
                "scope": "formal_functional_only",
                "criteria": [
                    "temporal_persistence_score",
                    "phase_ordering_score",
                    "history_dependence_score",
                    "recurrence_continuity_score",
                    "forward_transition_readiness_score",
                ],
            },
            "component_sources": {
                "primary": "intrinsic_causality_tester",
                "upstream": [
                    "intrinsic_existence_mode_definition",
                    "mode_intrinsicality_tester",
                    "intrinsic_irreducibility_tester",
                    "robust_qualia_formal_certifier",
                ],
                "supporting_formal_priors": [
                    "continuity_metrics_engine",
                    "global_temporal_binding",
                    "temporal_self_continuity",
                    "trajectory_path_dependency",
                ],
            },
            "intrinsic_existence_mode_definition_input": bool(aj1),
            "mode_intrinsicality_tester_input": bool(aj2),
            "intrinsic_irreducibility_tester_input": bool(aj3),
            "intrinsic_causality_tester_input": bool(aj4),
            "qf_robust_certified_input": bool(ai10),
            "epistemic_status": "functional_only",
            "functional_only_flags": dict(GUARD),
            "next_recommended_module": "intrinsic_invariance_tester",
            **GUARD,
        }
        if persist:
            result["paths"] = _persist(result)
        return result


__all__ = ["IntrinsicTemporalityTester"]
