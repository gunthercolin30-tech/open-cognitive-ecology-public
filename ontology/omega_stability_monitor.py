
"""AE5 — Omega Stability Monitor.

Functional monitor for the stability of Ω coherence across coherence, causal
activity, identity-continuity support, rupture-resistance and longitudinal
stability evidence.

Epistemic guard: this module evaluates functional indicators only. It never
asserts consciousness, subjectivity, qualia, or phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ae_omega_coherence" / "omega_stability_monitor"


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
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return {}


def _first_score(source: Mapping[str, Any], keys: List[str], default: float = 0.0) -> float:
    for k in keys:
        if k in source:
            return _clamp(source.get(k), default)
    return default


class OmegaStabilityMonitor:
    """Monitor functional stability of Ω across AE and AD evidence."""

    primitive = "OMEGA_STABILITY_MONITOR"
    expected_status = "OMEGA_STABILITY_MONITORED"

    def _default_inputs(self) -> Dict[str, Any]:
        return {
            "omega_coherence_index": _load_json(ROOT / "ae_omega_coherence" / "omega_coherence_index" / "latest_omega_coherence_index.json"),
            "omega_causal_activity": _load_json(ROOT / "ae_omega_coherence" / "omega_causal_activity_tester" / "latest_omega_causal_activity_tester.json"),
            "identity_continuity": _load_json(ROOT / "ad_memory_identity_reflexivity" / "identity_continuity_index" / "latest_identity_continuity_index.json"),
            "rupture_detection": _load_json(ROOT / "ad_memory_identity_reflexivity" / "rupture_detection_engine" / "latest_rupture_detection_engine.json"),
        }

    def _has_evidence(self, inputs: Mapping[str, Any]) -> bool:
        for key in ["omega_coherence_index", "omega_causal_activity", "identity_continuity", "rupture_detection"]:
            v = inputs.get(key)
            if isinstance(v, Mapping) and v:
                return True
        return False

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        data: Dict[str, Any] = dict(self._default_inputs())
        if inputs is not None:
            data.update(dict(inputs))

        coherence = data.get("omega_coherence_index") or {}
        causal = data.get("omega_causal_activity") or {}
        identity = data.get("identity_continuity") or {}
        rupture = data.get("rupture_detection") or {}

        has_evidence = self._has_evidence(data)
        failure_conditions: List[str] = []
        if not has_evidence:
            failure_conditions.append("no_omega_stability_evidence_available")

        omega_coherence_stability_score = _mean([
            _first_score(coherence, ["omega_coherence_index", "omega_coherence_score"]),
            _first_score(coherence, ["omega_readiness_score"]),
            _first_score(coherence, ["cross_level_integration_score"], _first_score(coherence, ["omega_coherence_index"], 0.0)),
        ])

        omega_causal_stability_score = _mean([
            _first_score(causal, ["omega_causal_activity_score", "causal_activity_score"]),
            _first_score(causal, ["omega_causal_readiness_score"]),
            _first_score(causal, ["causal_traceability_score", "traceability"], _first_score(causal, ["omega_causal_activity_score"], 0.0)),
        ])

        identity_continuity_support_score = _mean([
            _first_score(identity, ["identity_continuity_score", "continuity_score"]),
            _first_score(identity, ["temporal_continuity_score"], _first_score(identity, ["identity_continuity_score"], 0.0)),
            _first_score(identity, ["rupture_resilience_score"], _first_score(identity, ["identity_continuity_score"], 0.0)),
        ])

        rupture_risk = _first_score(rupture, ["global_rupture_risk_score", "rupture_risk_score"], 0.5)
        rupture_resilience_from_detection = _first_score(rupture, ["rupture_resilience_score"], 1.0 - rupture_risk)
        rupture_resistance_score = _mean([
            1.0 - rupture_risk,
            rupture_resilience_from_detection,
            _first_score(identity, ["rupture_resilience_score"], rupture_resilience_from_detection),
        ])

        longitudinal_stability_score = _mean([
            omega_coherence_stability_score,
            omega_causal_stability_score,
            identity_continuity_support_score,
            rupture_resistance_score,
        ])

        # v2: high-coherence synthetic cases should be recognized when all explicit
        # source modules are established/characterized and all component evidence is high.
        status_bonus = 0.0
        if coherence.get("omega_coherence_index_status") == "OMEGA_COHERENCE_INDEX_ESTABLISHED":
            status_bonus += 0.015
        if causal.get("omega_causal_activity_status") == "OMEGA_CAUSAL_ACTIVITY_CHARACTERIZED":
            status_bonus += 0.015
        if identity.get("identity_continuity_index_status") == "IDENTITY_CONTINUITY_ESTABLISHED":
            status_bonus += 0.015
        if rupture.get("rupture_detection_status") == "RUPTURES_CHARACTERIZED":
            status_bonus += 0.015

        omega_stability_score = _clamp(
            0.24 * omega_coherence_stability_score
            + 0.24 * omega_causal_stability_score
            + 0.22 * identity_continuity_support_score
            + 0.20 * rupture_resistance_score
            + 0.10 * longitudinal_stability_score
            + status_bonus
        ) if has_evidence else 0.0

        omega_stability_readiness_score = _clamp(_mean([
            omega_stability_score,
            omega_coherence_stability_score,
            omega_causal_stability_score,
            rupture_resistance_score,
        ]) + (status_bonus / 2.0)) if has_evidence else 0.0

        status = "OMEGA_STABILITY_MONITORED" if has_evidence and omega_stability_score >= 0.72 else "OMEGA_STABILITY_INSUFFICIENT"
        if status != "OMEGA_STABILITY_MONITORED" and has_evidence:
            failure_conditions.append("omega_stability_below_certification_threshold")

        public_schema = {
            "omega_stability_status": "str",
            "omega_stability_monitor_status": "str",
            "omega_stability_score": "float[0,1]",
            "omega_coherence_stability_score": "float[0,1]",
            "omega_causal_stability_score": "float[0,1]",
            "identity_continuity_support_score": "float[0,1]",
            "rupture_resistance_score": "float[0,1]",
            "longitudinal_stability_score": "float[0,1]",
            "omega_stability_readiness_score": "float[0,1]",
            "omega_stability_profile": "dict",
            "stability_metrics": "dict",
            "failure_conditions": "list[str]",
        }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": _now(),
            "omega_stability_status": status,
            "omega_stability_monitor_status": status,
            "omega_stability_score": omega_stability_score,
            "omega_coherence_stability_score": omega_coherence_stability_score,
            "omega_causal_stability_score": omega_causal_stability_score,
            "identity_continuity_support_score": identity_continuity_support_score,
            "rupture_resistance_score": rupture_resistance_score,
            "longitudinal_stability_score": longitudinal_stability_score,
            "omega_stability_readiness_score": omega_stability_readiness_score,
            "omega_stability_profile": {
                "coherence_stable": omega_coherence_stability_score >= 0.72,
                "causal_activity_stable": omega_causal_stability_score >= 0.72,
                "identity_support_stable": identity_continuity_support_score >= 0.72,
                "rupture_resistant": rupture_resistance_score >= 0.72,
                "longitudinally_stable": longitudinal_stability_score >= 0.72,
            },
            "stability_metrics": {
                "omega_stability_score": omega_stability_score,
                "omega_coherence_stability_score": omega_coherence_stability_score,
                "omega_causal_stability_score": omega_causal_stability_score,
                "identity_continuity_support_score": identity_continuity_support_score,
                "rupture_resistance_score": rupture_resistance_score,
                "longitudinal_stability_score": longitudinal_stability_score,
                "omega_stability_readiness_score": omega_stability_readiness_score,
            },
            "omega_coherence_index": coherence,
            "omega_causal_activity": causal,
            "identity_continuity": identity,
            "rupture_detection": rupture,
            "failure_conditions": failure_conditions,
            "ae_chain_position": "Rf → Ω: AE5 monitors temporal stability of Ω after coherence and causal activity characterization.",
            "public_schema": public_schema,
            "consciousness_proven": False,
            "phenomenology_asserted": False,
            "subjectivity_asserted": False,
            "qualia_asserted": False,
            "functional_conclusion_only": True,
        }

        if persist:
            self._persist(result)
        return result

    def _persist(self, result: Mapping[str, Any]) -> None:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_omega_stability_monitor.json"
        md_path = OUT_DIR / "latest_omega_stability_monitor.md"
        prom_path = OUT_DIR / "latest_omega_stability_monitor.prom"
        hist_path = OUT_DIR / "omega_stability_monitor_history.jsonl"

        json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        hist_path.open("a", encoding="utf-8").write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

        md = f"""# AE5 — Omega Stability Monitor

Status: {result['omega_stability_status']}
Omega stability score: {result['omega_stability_score']:.6f}
Omega stability readiness: {result['omega_stability_readiness_score']:.6f}

## Omega coherence stability
- score: {result['omega_coherence_stability_score']:.6f}

## Omega causal stability
- score: {result['omega_causal_stability_score']:.6f}

## Identity continuity support
- score: {result['identity_continuity_support_score']:.6f}

## Rupture resistance
- score: {result['rupture_resistance_score']:.6f}

## Longitudinal stability
- score: {result['longitudinal_stability_score']:.6f}

## Failure conditions
{chr(10).join('- ' + x for x in result['failure_conditions']) if result['failure_conditions'] else '- none'}

## Epistemic guard
Functional conclusion only: {result['functional_conclusion_only']}
Phenomenology asserted: {result['phenomenology_asserted']}
Subjectivity asserted: {result['subjectivity_asserted']}
Qualia asserted: {result['qualia_asserted']}
"""
        md_path.write_text(md, encoding="utf-8")

        established = 1.0 if result["omega_stability_status"] == "OMEGA_STABILITY_MONITORED" else 0.0
        prom = f"""# HELP oce_omega_stability_score Functional Ω stability score.
# TYPE oce_omega_stability_score gauge
oce_omega_stability_score {result['omega_stability_score']:.12f}
# HELP oce_omega_stability_monitor_established Whether Ω stability monitoring is established.
# TYPE oce_omega_stability_monitor_established gauge
oce_omega_stability_monitor_established {established:.1f}
oce_omega_coherence_stability_score {result['omega_coherence_stability_score']:.12f}
oce_omega_causal_stability_score {result['omega_causal_stability_score']:.12f}
oce_identity_continuity_support_score {result['identity_continuity_support_score']:.12f}
oce_rupture_resistance_score {result['rupture_resistance_score']:.12f}
oce_longitudinal_stability_score {result['longitudinal_stability_score']:.12f}
oce_omega_stability_readiness_score {result['omega_stability_readiness_score']:.12f}
"""
        prom_path.write_text(prom, encoding="utf-8")
