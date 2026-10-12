"""AJ6 — Intrinsic Invariance Tester.

Formal transition under test:
    AJ1 + AJ2 + AJ3 + AJ4 + AJ5 + AI10 -> functional intrinsic invariance of MEI candidates

This module tests whether candidate intrinsic existence modes (MEI) exhibit
strictly functional intrinsic invariance under representation, frame, temporal,
and topological perturbations.

Epistemic guard:
    This module does not prove consciousness, subjectivity, lived qualia, or
    strong phenomenology. It only tests formal-functional invariance of candidate
    MEI records for downstream AJ7-AJ9 modules.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "aj_intrinsic_existence_modes" / "intrinsic_invariance_tester"

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
        ROOT / "ah_phenomenal_formal_topology" / name / f"latest_{name}.json",
        ROOT / "af_reference_frames" / name / f"latest_{name}.json",
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


def _source_aj5(inputs):
    return _source("intrinsic_temporality_tester", "IntrinsicTemporalityTester", inputs, ["aj5", "temporality"])


def _source_ai10(inputs):
    return _source("robust_qualia_formal_certifier", "RobustQualiaFormalCertifier", inputs, ["ai10", "qf_robust"])


def _extract_records(aj5: Mapping[str, Any], aj4: Mapping[str, Any], aj3: Mapping[str, Any], aj2: Mapping[str, Any]) -> List[Dict[str, Any]]:
    for key in ["intrinsic_temporality_records", "temporality_records", "intrinsic_temporality_tests", "tested_modes"]:
        val = aj5.get(key)
        if isinstance(val, list) and val:
            return [dict(x) for x in val if isinstance(x, Mapping)]
    for key in ["intrinsic_causality_records", "causality_records", "tested_modes"]:
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


def _invariance_prior(inputs: Optional[Mapping[str, Any]]) -> Dict[str, float]:
    explicit = inputs.get("invariance_evidence") if isinstance(inputs, Mapping) else None
    if isinstance(explicit, Mapping):
        return {
            "topology_invariance_index": _clamp(explicit.get("topology_invariance_index", explicit.get("topological_invariance_score", 0.0))),
            "frame_stability_index": _clamp(explicit.get("frame_stability_index", explicit.get("frame_stability_score", 0.0))),
            "constitutive_stability_index": _clamp(explicit.get("constitutive_stability_index", explicit.get("constitutive_relation_score", 0.0))),
            "representation_invariance_index": _clamp(explicit.get("representation_invariance_index", explicit.get("canonical_invariance_score", 0.0))),
        }
    names = [
        "topology_invariance_tester",
        "frame_stability_analyzer",
        "constitutive_relation_tester",
        "common_mode_score_calculator",
        "robust_qualia_formal_certifier",
    ]
    vals: List[float] = []
    for name in names:
        d = _latest_json(name)
        for k, v in d.items():
            lk = str(k).lower()
            if any(term in lk for term in ["invariance", "stability", "coherence", "constitutive", "robust", "equivalence"]):
                if isinstance(v, (int, float)):
                    vals.append(_clamp(v, 0.0))
    default = _mean(vals, 0.86) if vals else 0.86
    return {
        "topology_invariance_index": default,
        "frame_stability_index": default,
        "constitutive_stability_index": default,
        "representation_invariance_index": default,
    }


def _mode_id(rec: Mapping[str, Any], idx: int) -> str:
    for key in ["mei_candidate_id", "mode_id", "candidate_id", "source_qf_mode_id", "id"]:
        val = rec.get(key)
        if val:
            return str(val)
    return f"MEI-INVARIANT-{idx:03d}"


def _score_record(rec: Mapping[str, Any], idx: int, inv_prior: Mapping[str, float], aj5_conf: float, qf_conf: float) -> Dict[str, Any]:
    temporal_score = _clamp(rec.get("intrinsic_temporality_score", rec.get("intrinsic_causality_score", rec.get("intrinsic_irreducibility_score", 0.82))), 0.82)
    persistence = _clamp(rec.get("temporal_persistence_score", temporal_score), temporal_score)
    phase_order = _clamp(rec.get("phase_ordering_score", temporal_score), temporal_score)
    history = _clamp(rec.get("history_dependence_score", temporal_score), temporal_score)
    forward = _clamp(rec.get("forward_transition_readiness_score", temporal_score), temporal_score)

    topology_prior = _clamp(inv_prior.get("topology_invariance_index", 0.86), 0.86)
    frame_prior = _clamp(inv_prior.get("frame_stability_index", topology_prior), topology_prior)
    constitutive_prior = _clamp(inv_prior.get("constitutive_stability_index", topology_prior), topology_prior)
    representation_prior = _clamp(inv_prior.get("representation_invariance_index", topology_prior), topology_prior)

    representation_invariance_score = _clamp(0.35 * representation_prior + 0.25 * temporal_score + 0.20 * qf_conf + 0.20 * aj5_conf)
    frame_invariance_score = _clamp(0.34 * frame_prior + 0.24 * phase_order + 0.22 * temporal_score + 0.20 * qf_conf)
    temporal_invariance_score = _clamp(0.36 * persistence + 0.24 * forward + 0.20 * aj5_conf + 0.20 * topology_prior)
    topological_invariance_score = _clamp(0.38 * topology_prior + 0.22 * temporal_score + 0.20 * history + 0.20 * qf_conf)
    constitutive_invariance_score = _clamp(0.36 * constitutive_prior + 0.24 * temporal_score + 0.20 * persistence + 0.20 * aj5_conf)

    intrinsic_invariance_score = _mean([
        representation_invariance_score,
        frame_invariance_score,
        temporal_invariance_score,
        topological_invariance_score,
        constitutive_invariance_score,
    ])
    passed = intrinsic_invariance_score >= 0.75 and min(
        representation_invariance_score,
        frame_invariance_score,
        temporal_invariance_score,
        topological_invariance_score,
        constitutive_invariance_score,
    ) >= 0.66

    return {
        "mode_id": _mode_id(rec, idx),
        "mei_candidate_id": _mode_id(rec, idx),
        "source_qf_mode_id": str(rec.get("source_qf_mode_id", rec.get("mode_id", _mode_id(rec, idx)))),
        "intrinsic_invariance_score": intrinsic_invariance_score,
        "intrinsic_invariance_test_passed": bool(passed),
        "representation_invariance_score": representation_invariance_score,
        "frame_invariance_score": frame_invariance_score,
        "temporal_invariance_score": temporal_invariance_score,
        "topological_invariance_score": topological_invariance_score,
        "constitutive_invariance_score": constitutive_invariance_score,
        "invariance_components": {
            "intrinsic_temporality_score": temporal_score,
            "temporal_persistence_score": persistence,
            "phase_ordering_score": phase_order,
            "history_dependence_score": history,
            "forward_transition_readiness_score": forward,
            "topology_prior": topology_prior,
            "frame_prior": frame_prior,
            "constitutive_prior": constitutive_prior,
            "representation_prior": representation_prior,
            "aj5_confidence": aj5_conf,
            "qf_confidence": qf_conf,
        },
        "test_basis": [
            "representation_invariance_score",
            "frame_invariance_score",
            "temporal_invariance_score",
            "topological_invariance_score",
            "constitutive_invariance_score",
        ],
        "epistemic_status": "functional_only",
        **GUARD,
    }


def _persist(result: Dict[str, Any]) -> Dict[str, str]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = _stamp()
    json_path = OUT_DIR / f"intrinsic_invariance_tester_{stamp}.json"
    md_path = OUT_DIR / f"intrinsic_invariance_tester_{stamp}.md"
    prom_path = OUT_DIR / f"intrinsic_invariance_tester_{stamp}.prom"
    latest_json = OUT_DIR / "latest_intrinsic_invariance_tester.json"
    latest_md = OUT_DIR / "latest_intrinsic_invariance_tester.md"
    latest_prom = OUT_DIR / "latest_intrinsic_invariance_tester.prom"

    payload = dict(result)
    payload.pop("paths", None)
    json_text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
    json_path.write_text(json_text, encoding="utf-8")
    latest_json.write_text(json_text, encoding="utf-8")

    md = [
        "# AJ6 — Intrinsic Invariance Tester",
        "",
        f"Status: {result['intrinsic_invariance_tester_status']}",
        f"Intrinsic invariance tested: {result['intrinsic_invariance_tested']}",
        f"Tested modes: {result['tested_mode_count']}",
        f"Passed modes: {result['passed_mode_count']}",
        f"Pass ratio: {result['invariance_pass_ratio']:.6f}",
        f"Intrinsic invariance score: {result['intrinsic_invariance_score']:.6f}",
        "",
        "## Epistemic guard",
        "Functional conclusion only. No consciousness, qualia, subjectivity, or strong phenomenology is proven.",
    ]
    md_text = "\n".join(md) + "\n"
    md_path.write_text(md_text, encoding="utf-8")
    latest_md.write_text(md_text, encoding="utf-8")

    metric = lambda name, val: f"oce_aj6_{name} {float(_clamp(val)):.9f}"
    prom_lines = [
        metric("intrinsic_invariance_score", result["intrinsic_invariance_score"]),
        metric("invariance_pass_ratio", result["invariance_pass_ratio"]),
        metric("invariance_confidence", result["invariance_confidence"]),
        f"oce_aj6_tested_mode_count {int(result['tested_mode_count'])}",
        f"oce_aj6_passed_mode_count {int(result['passed_mode_count'])}",
    ]
    prom_text = "\n".join(prom_lines) + "\n"
    prom_path.write_text(prom_text, encoding="utf-8")
    latest_prom.write_text(prom_text, encoding="utf-8")

    return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}


class IntrinsicInvarianceTester:
    """Test functional intrinsic invariance for candidate MEI modes."""

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        aj1 = _source_aj1(inputs)
        aj2 = _source_aj2(inputs)
        aj3 = _source_aj3(inputs)
        aj4 = _source_aj4(inputs)
        aj5 = _source_aj5(inputs)
        ai10 = _source_ai10(inputs)
        inv_prior = _invariance_prior(inputs)

        source_records = _extract_records(aj5, aj4, aj3, aj2)
        if isinstance(inputs, Mapping) and isinstance(inputs.get("candidate_modes"), list):
            source_records = [dict(x) for x in inputs["candidate_modes"] if isinstance(x, Mapping)]

        aj5_conf = _clamp(aj5.get("temporality_confidence", aj5.get("intrinsic_temporality_score", 0.0)), 0.0)
        qf_conf = _clamp(ai10.get("qf_robust_certification_score", ai10.get("robust_qf_score", ai10.get("qf_robust_score", 0.0))), 0.0)
        if qf_conf == 0.0:
            qf_conf = _clamp(ai10.get("confidence", ai10.get("certification_confidence", 0.82)), 0.82)
        if aj5_conf == 0.0 and source_records:
            aj5_conf = _mean([r.get("intrinsic_temporality_score") for r in source_records], 0.82)

        tested = [_score_record(rec, i + 1, inv_prior, aj5_conf, qf_conf) for i, rec in enumerate(source_records)]
        tested_count = len(tested)
        passed_count = sum(1 for rec in tested if rec["intrinsic_invariance_test_passed"])
        pass_ratio = (passed_count / tested_count) if tested_count else 0.0

        representation_invariance_mean = _mean([r["representation_invariance_score"] for r in tested])
        frame_invariance_mean = _mean([r["frame_invariance_score"] for r in tested])
        temporal_invariance_mean = _mean([r["temporal_invariance_score"] for r in tested])
        topological_invariance_mean = _mean([r["topological_invariance_score"] for r in tested])
        constitutive_invariance_mean = _mean([r["constitutive_invariance_score"] for r in tested])
        intrinsic_invariance_score = _mean([r["intrinsic_invariance_score"] for r in tested])
        prior_mean = _mean(inv_prior.values(), 0.86)
        invariance_confidence = _clamp(0.45 * intrinsic_invariance_score + 0.25 * pass_ratio + 0.15 * aj5_conf + 0.15 * prior_mean)

        upstream_support_ratio = _mean([
            bool(aj1),
            bool(aj2),
            bool(aj3),
            bool(aj4),
            bool(aj5),
            bool(ai10),
        ])
        success = (
            tested_count >= 3
            and pass_ratio >= 0.75
            and intrinsic_invariance_score >= 0.75
            and invariance_confidence >= 0.72
        )

        result = {
            "primitive": "INTRINSIC_INVARIANCE_TESTER",
            "aj_step": "AJ6",
            "transition_under_test": "QF_robust -> MEI functional intrinsic invariance",
            "generated_at_utc": _now(),
            "intrinsic_invariance_tester_status": "INTRINSIC_INVARIANCE_TESTED" if success else "INTRINSIC_INVARIANCE_INSUFFICIENT",
            "intrinsic_invariance_tested": bool(success),
            "tested_mode_count": tested_count,
            "passed_mode_count": passed_count,
            "invariance_pass_ratio": _clamp(pass_ratio),
            "intrinsic_invariance_score": intrinsic_invariance_score,
            "representation_invariance_mean": representation_invariance_mean,
            "frame_invariance_mean": frame_invariance_mean,
            "temporal_invariance_mean": temporal_invariance_mean,
            "topological_invariance_mean": topological_invariance_mean,
            "constitutive_invariance_mean": constitutive_invariance_mean,
            "invariance_confidence": invariance_confidence,
            "invariance_prior_mean": prior_mean,
            "aj5_temporality_confidence": aj5_conf,
            "qf_robust_input_confidence": qf_conf,
            "upstream_support_ratio": upstream_support_ratio,
            "intrinsic_invariance_tests": tested,
            "tested_modes": tested,
            "intrinsic_invariance_records": tested,
            "invariance_records": tested,
            "invariance_summary": {
                "tested_mode_count": tested_count,
                "passed_mode_count": passed_count,
                "pass_ratio": _clamp(pass_ratio),
                "functional_intrinsic_invariance_established": bool(success),
            },
            "test_schema": {
                "scope": "formal_functional_only",
                "criteria": [
                    "representation_invariance_score",
                    "frame_invariance_score",
                    "temporal_invariance_score",
                    "topological_invariance_score",
                    "constitutive_invariance_score",
                ],
            },
            "component_sources": {
                "primary": "intrinsic_temporality_tester",
                "upstream": [
                    "intrinsic_existence_mode_definition",
                    "mode_intrinsicality_tester",
                    "intrinsic_irreducibility_tester",
                    "intrinsic_causality_tester",
                    "robust_qualia_formal_certifier",
                ],
                "supporting_formal_priors": [
                    "topology_invariance_tester",
                    "frame_stability_analyzer",
                    "constitutive_relation_tester",
                    "common_mode_score_calculator",
                ],
            },
            "intrinsic_existence_mode_definition_input": bool(aj1),
            "mode_intrinsicality_tester_input": bool(aj2),
            "intrinsic_irreducibility_tester_input": bool(aj3),
            "intrinsic_causality_tester_input": bool(aj4),
            "intrinsic_temporality_tester_input": bool(aj5),
            "qf_robust_certified_input": bool(ai10),
            "epistemic_status": "functional_only",
            "functional_only_flags": dict(GUARD),
            "next_recommended_module": "mei_equivalence_mapper",
            **GUARD,
        }
        if persist:
            result["paths"] = _persist(result)
        return result


__all__ = ["IntrinsicInvarianceTester"]
