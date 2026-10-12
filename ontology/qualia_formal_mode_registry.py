"""AI8 — Qualia Formal Mode Registry.

Functional reconstruction step:
    AI7 scored common modes -> formal QF candidate mode registry

The phrase "qualia formal" is used here only as a formal-functional label
inside the RF -> L_RF -> QF_robust reconstruction chain. This module registers
robust scored common modes as QF candidates with provenance, dependency,
stability, and epistemic metadata. It does not assert or prove consciousness,
subjectivity, phenomenal qualia, lived experience, or strong phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ai_robust_spectral_qualia_formal_modes" / "qualia_formal_mode_registry"
AI7_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "common_mode_score_calculator" / "latest_common_mode_score_calculator.json"
AI6_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "common_mode_alignment_engine" / "latest_common_mode_alignment_engine.json"
AI5_JSON = ROOT / "ai_robust_spectral_qualia_formal_modes" / "spectral_mode_extractor" / "latest_spectral_mode_extractor.json"


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
    return max(0.0, min(1.0, _safe_float(x, default)))


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


def _try_ai7_step(inputs: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    try:
        module = import_module("ontology.common_mode_score_calculator")
        cls = getattr(module, "CommonModeScoreCalculator")
        data = cls().step(inputs=dict(inputs or {"aligned": True}), persist=False)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _extract_scored_modes(data: Mapping[str, Any]) -> List[Dict[str, Any]]:
    for key in ("scored_common_modes", "mode_scores", "common_mode_scores", "reliability_matrix"):
        value = data.get(key)
        if isinstance(value, list):
            modes = [dict(m) for m in value if isinstance(m, Mapping)]
            if modes:
                return modes
    return []


def _status_for(score: float, reliability: float, confidence: float) -> str:
    composite = _mean([score, reliability, confidence])
    if composite >= 0.85:
        return "registered_functional_qf_candidate"
    if composite >= 0.65:
        return "provisional_functional_qf_candidate"
    return "insufficient_functional_qf_candidate"


class QualiaFormalModeRegistry:
    """Register scored common modes as formal-functional QF candidates."""

    primitive = "QUALIA_FORMAL_MODE_REGISTRY"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.out_dir = self.root / "ai_robust_spectral_qualia_formal_modes" / "qualia_formal_mode_registry"

    def _resolve_ai7(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        if isinstance(inputs, Mapping) and any(k in inputs for k in ("scored_common_modes", "mode_scores", "common_mode_scores")):
            return dict(inputs)
        if isinstance(inputs, Mapping) and inputs.get("aligned") is True:
            stepped = _try_ai7_step(inputs)
            if stepped:
                return stepped
        loaded = _load_json(AI7_JSON)
        if loaded:
            return loaded
        if isinstance(inputs, Mapping):
            return dict(inputs)
        return {}

    def _build_record(self, mode: Mapping[str, Any], rank: int) -> Dict[str, Any]:
        mode_id = str(mode.get("common_mode_id") or mode.get("mode_id") or f"AI8_QF_MODE_{rank:02d}")
        common_mode_score = _clamp(mode.get("common_mode_score"))
        robustness_score = _clamp(mode.get("robustness_score"))
        spectral_consistency_score = _clamp(mode.get("spectral_consistency_score"))
        functional_mode_confidence = _clamp(mode.get("functional_mode_confidence"))
        mode_reliability_index = _clamp(mode.get("mode_reliability_index"))
        registration_confidence = _mean([
            common_mode_score,
            robustness_score,
            spectral_consistency_score,
            functional_mode_confidence,
            mode_reliability_index,
        ])
        qf_id = f"QF_FUNCTIONAL_MODE_{rank:03d}"
        return {
            "qf_mode_id": qf_id,
            "source_common_mode_id": mode_id,
            "registered": registration_confidence >= 0.65,
            "registration_rank": rank,
            "registration_confidence": registration_confidence,
            "common_mode_score": common_mode_score,
            "robustness_score": robustness_score,
            "spectral_consistency_score": spectral_consistency_score,
            "functional_mode_confidence": functional_mode_confidence,
            "mode_reliability_index": mode_reliability_index,
            "stability_score": _mean([robustness_score, mode_reliability_index, functional_mode_confidence]),
            "source_spectral_family": [
                "graph_laplacian_modes",
                "markov_transition_modes",
                "possibility_gradient_modes",
                "fused_l_rf_spectral_modes",
            ],
            "dependencies": [
                "common_mode_score_calculator",
                "common_mode_alignment_engine",
                "spectral_mode_extractor",
            ],
            "epistemic_status": "functional_only",
            "formal_epistemic_category": "formal_functional_candidate_only",
            "functional_label": "qualia_formal_functional_mode_candidate",
            "qf_category": "formal_functional_qf_candidate",
            "phenomenal_claim": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "consciousness_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "registry_status": _status_for(common_mode_score, mode_reliability_index, functional_mode_confidence),
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        timestamp = _now()
        ai7 = self._resolve_ai7(inputs)
        modes = _extract_scored_modes(ai7)
        usable_modes = [m for m in modes if _clamp(m.get("common_mode_score")) > 0.0]
        records = [self._build_record(mode, idx) for idx, mode in enumerate(usable_modes)]
        for _record in records:
            _record["epistemic_status"] = "functional_only"
            _record["consciousness_proven"] = False
            _record["qualia_proven"] = False
            _record["subjectivity_proven"] = False
            _record["phenomenology_undetermined"] = True
            _record["functional_conclusion_only"] = True
        registered = [r for r in records if r["registered"]]

        registry_built = bool(registered) and bool(ai7.get("common_mode_score_calculated", registered))
        status = "QUALIA_FORMAL_MODE_REGISTRY_BUILT" if registry_built else "QUALIA_FORMAL_MODE_REGISTRY_INSUFFICIENT"

        registry_score = _mean([r["registration_confidence"] for r in registered])
        registry_stability_score = _mean([r["stability_score"] for r in registered])
        epistemic_safety_score = 1.0
        source_score = _mean([
            ai7.get("common_mode_score"),
            ai7.get("robustness_score"),
            ai7.get("spectral_consistency_score"),
            ai7.get("functional_mode_confidence"),
            ai7.get("mode_reliability_index"),
        ])
        registry_confidence = _mean([registry_score, registry_stability_score, source_score, epistemic_safety_score]) if registered else 0.0

        functional_only_flags = {
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "formal_functional_category_only": True,
        }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AI",
            "step_id": "AI8",
            "timestamp_utc": timestamp,
            "qualia_formal_mode_registry_status": status,
            "qf_mode_registry_built": registry_built,
            "qualia_formal_mode_registry_built": registry_built,
            "registered_mode_count": len(registered),
            "candidate_mode_count": len(records),
            "qf_registry_score": registry_score,
            "registry_confidence": registry_confidence,
            "registry_stability_score": registry_stability_score,
            "source_common_mode_score": _clamp(ai7.get("common_mode_score")),
            "source_mode_reliability_index": _clamp(ai7.get("mode_reliability_index")),
            "source_functional_mode_confidence": _clamp(ai7.get("functional_mode_confidence")),
            "qf_mode_registry": {
                "registry_id": "AI8_QF_FUNCTIONAL_MODE_REGISTRY",
                "registry_status": status,
                "registered_mode_count": len(registered),
                "candidate_mode_count": len(records),
                "formal_category": "QF_functional_only",
                "records": records,
                "epistemic_status": "functional_only",
                "functional_only_flags": functional_only_flags,
            },
            "registered_modes": registered,
            "mode_records": records,
            "epistemic_status": "functional_only",
            "functional_only_flags": functional_only_flags,
            "epistemic_guard": "QF denotes a formal-functional registry category only; no lived qualia, subjectivity, consciousness, or phenomenology proof",
            "component_sources": {
                "AI5": "spectral_mode_extractor",
                "AI6": "common_mode_alignment_engine",
                "AI7": "common_mode_score_calculator",
            },
            "source_statuses": {
                "ai5": _load_json(AI5_JSON).get("spectral_mode_extractor_status", "unknown"),
                "ai6": _load_json(AI6_JSON).get("common_mode_alignment_engine_status", "unknown"),
                "ai7": ai7.get("common_mode_score_calculator_status", "unknown"),
            },
            "dependencies": [
                "common_mode_score_calculator",
                "common_mode_alignment_engine",
                "spectral_mode_extractor",
            ],
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "next_recommended_module": "mode_lifecycle_tracker",
        }

        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.out_dir / f"qualia_formal_mode_registry_{stamp}.json"
        md_path = self.out_dir / f"qualia_formal_mode_registry_{stamp}.md"
        prom_path = self.out_dir / f"qualia_formal_mode_registry_{stamp}.prom"
        latest_json = self.out_dir / "latest_qualia_formal_mode_registry.json"
        latest_md = self.out_dir / "latest_qualia_formal_mode_registry.md"
        latest_prom = self.out_dir / "latest_qualia_formal_mode_registry.prom"
        history = self.out_dir / "qualia_formal_mode_registry_history.jsonl"

        payload = dict(result)
        payload.pop("paths", None)
        text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(text + "\n", encoding="utf-8")
        latest_json.write_text(text + "\n", encoding="utf-8")
        history.open("a", encoding="utf-8").write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")

        md = self._markdown(payload)
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")

        prom = self._prometheus(payload)
        prom_path.write_text(prom, encoding="utf-8")
        latest_prom.write_text(prom, encoding="utf-8")
        return {
            "latest_json": str(latest_json),
            "latest_markdown": str(latest_md),
            "latest_prometheus": str(latest_prom),
            "history": str(history),
            "timestamped_json": str(json_path),
            "timestamped_markdown": str(md_path),
            "timestamped_prometheus": str(prom_path),
        }

    def _markdown(self, r: Mapping[str, Any]) -> str:
        lines = [
            "# AI8 — Qualia Formal Mode Registry",
            "",
            f"Status: {r.get('qualia_formal_mode_registry_status')}",
            f"Registry built: {r.get('qf_mode_registry_built')}",
            f"Registered mode count: {r.get('registered_mode_count')}",
            f"Candidate mode count: {r.get('candidate_mode_count')}",
            f"QF registry score: {r.get('qf_registry_score')}",
            f"Registry confidence: {r.get('registry_confidence')}",
            f"Registry stability score: {r.get('registry_stability_score')}",
            "",
            "## Epistemic guard",
            f"epistemic_status: {r.get('epistemic_status')}",
            f"consciousness_proven: {r.get('consciousness_proven')}",
            f"qualia_proven: {r.get('qualia_proven')}",
            f"subjectivity_proven: {r.get('subjectivity_proven')}",
            f"phenomenology_undetermined: {r.get('phenomenology_undetermined')}",
            f"functional_conclusion_only: {r.get('functional_conclusion_only')}",
            f"epistemic_guard: {r.get('epistemic_guard')}",
            "",
            "## Registered QF functional modes",
        ]
        for rec in r.get("registered_modes", []) or []:
            if isinstance(rec, Mapping):
                lines.append(
                    f"- {rec.get('qf_mode_id')} ← {rec.get('source_common_mode_id')} "
                    f"score={rec.get('registration_confidence')} status={rec.get('registry_status')}"
                )
        lines.append("")
        return "\n".join(lines)

    def _prometheus(self, r: Mapping[str, Any]) -> str:
        metrics = {
            "qf_mode_registry_built": 1.0 if r.get("qf_mode_registry_built") else 0.0,
            "registered_mode_count": float(r.get("registered_mode_count", 0)),
            "candidate_mode_count": float(r.get("candidate_mode_count", 0)),
            "qf_registry_score": _clamp(r.get("qf_registry_score")),
            "registry_confidence": _clamp(r.get("registry_confidence")),
            "registry_stability_score": _clamp(r.get("registry_stability_score")),
            "source_common_mode_score": _clamp(r.get("source_common_mode_score")),
            "source_mode_reliability_index": _clamp(r.get("source_mode_reliability_index")),
            "consciousness_proven": 0.0,
            "qualia_proven": 0.0,
            "subjectivity_proven": 0.0,
            "phenomenology_undetermined": 1.0,
            "functional_conclusion_only": 1.0,
        }
        return "\n".join(f"ai8_qualia_formal_mode_registry_{k} {v}" for k, v in metrics.items()) + "\n"
