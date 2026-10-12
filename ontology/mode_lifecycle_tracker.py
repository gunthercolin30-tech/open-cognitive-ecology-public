"""AI9 — Mode Lifecycle Tracker.

Functional reconstruction step:
    AI8 QF functional registry -> longitudinal lifecycle tracking of candidate modes

This module tracks the temporal and functional lifecycle of formal-functional QF
candidate modes: appearance, persistence, drift, decay risk, and longitudinal
confidence. It treats "qualia formal" strictly as a formal-functional label and
never as evidence of lived qualia, subjectivity, consciousness, or strong
phenomenology.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional, Tuple

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ai_robust_spectral_qualia_formal_modes" / "mode_lifecycle_tracker"
AI8_DIR = ROOT / "ai_robust_spectral_qualia_formal_modes" / "qualia_formal_mode_registry"
AI8_JSON = AI8_DIR / "latest_qualia_formal_mode_registry.json"


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


def _try_ai8_step(inputs: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    try:
        module = import_module("ontology.qualia_formal_mode_registry")
        cls = getattr(module, "QualiaFormalModeRegistry")
        data = cls().step(inputs=dict(inputs or {"aligned": True}), persist=False)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _extract_modes(registry: Mapping[str, Any]) -> List[Dict[str, Any]]:
    for key in ("registered_modes", "mode_records"):
        value = registry.get(key)
        if isinstance(value, list):
            modes = [dict(m) for m in value if isinstance(m, Mapping)]
            if modes:
                return modes
    nested = registry.get("qf_mode_registry")
    if isinstance(nested, Mapping):
        value = nested.get("records")
        if isinstance(value, list):
            modes = [dict(m) for m in value if isinstance(m, Mapping)]
            if modes:
                return modes
    return []


def _mode_key(mode: Mapping[str, Any]) -> str:
    return str(
        mode.get("qf_mode_id")
        or mode.get("source_common_mode_id")
        or mode.get("mode_id")
        or mode.get("common_mode_id")
        or "unknown_mode"
    )


def _mode_score(mode: Mapping[str, Any]) -> float:
    return _mean([
        mode.get("registration_confidence"),
        mode.get("stability_score"),
        mode.get("common_mode_score"),
        mode.get("robustness_score"),
        mode.get("mode_reliability_index"),
        mode.get("functional_mode_confidence"),
    ])


def _history_files(ai8_dir: Path) -> List[Path]:
    try:
        files = sorted(
            p for p in ai8_dir.glob("qualia_formal_mode_registry_*.json")
            if p.is_file()
        )
        latest = ai8_dir / "latest_qualia_formal_mode_registry.json"
        if latest.exists() and latest not in files:
            files.append(latest)
        return files
    except Exception:
        return []


def _load_registry_history(ai8_dir: Path) -> List[Dict[str, Any]]:
    history: List[Dict[str, Any]] = []
    seen = set()
    for path in _history_files(ai8_dir):
        data = _load_json(path)
        if not data:
            continue
        stamp = str(data.get("timestamp_utc") or path.name)
        sig = (stamp, path.name)
        if sig in seen:
            continue
        seen.add(sig)
        data["_history_file"] = str(path)
        history.append(data)
    history.sort(key=lambda d: str(d.get("timestamp_utc") or d.get("_history_file") or ""))
    return history


def _build_lifecycle_record(mode: Mapping[str, Any], history: List[Mapping[str, Any]], rank: int) -> Dict[str, Any]:
    key = _mode_key(mode)
    observations: List[Tuple[str, float]] = []
    for snapshot in history:
        modes = _extract_modes(snapshot)
        matched = [m for m in modes if _mode_key(m) == key or m.get("source_common_mode_id") == mode.get("source_common_mode_id")]
        if matched:
            observations.append((str(snapshot.get("timestamp_utc") or snapshot.get("_history_file") or "unknown"), _mode_score(matched[0])))
    current_score = _mode_score(mode)
    if not observations:
        observations = [("current", current_score)]
    observed_scores = [score for _, score in observations]
    first_score = observed_scores[0]
    last_score = observed_scores[-1]
    drift_raw = abs(last_score - first_score)
    local_volatility = max(observed_scores) - min(observed_scores) if observed_scores else 0.0
    persistence_score = _clamp(len(observations) / max(1, len(history))) if history else 1.0
    stability_score = _clamp(1.0 - _mean([drift_raw, local_volatility]))
    decay_risk = _clamp(max(0.0, first_score - last_score) + (1.0 - persistence_score) * 0.35 + local_volatility * 0.25)
    longitudinal_confidence = _mean([current_score, persistence_score, stability_score, 1.0 - decay_risk])
    lifecycle_status = "persistent_functional_mode" if longitudinal_confidence >= 0.75 else "provisional_lifecycle_mode"
    return {
        "lifecycle_mode_id": f"AI9_LIFECYCLE_MODE_{rank:03d}",
        "qf_mode_id": key,
        "source_common_mode_id": str(mode.get("source_common_mode_id") or ""),
        "observation_count": len(observations),
        "observed_scores": observed_scores,
        "first_observed_score": first_score,
        "latest_observed_score": last_score,
        "mode_persistence_score": persistence_score,
        "mode_lifecycle_stability_score": stability_score,
        "mode_drift_score": _clamp(drift_raw + local_volatility * 0.5),
        "mode_decay_risk": decay_risk,
        "longitudinal_mode_confidence": longitudinal_confidence,
        "lifecycle_status": lifecycle_status,
        "appearance_detected": True,
        "persistence_detected": len(observations) >= 2 or persistence_score >= 1.0,
        "drift_detected": _clamp(drift_raw + local_volatility * 0.5) > 0.15,
        "decay_detected": decay_risk > 0.35,
        "epistemic_status": "functional_only",
        "functional_lifecycle_only": True,
        "phenomenal_claim": False,
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_undetermined": True,
        "functional_conclusion_only": True,
    }


class ModeLifecycleTracker:
    """Track lifecycle stability of formal-functional QF candidate modes."""

    primitive = "MODE_LIFECYCLE_TRACKER"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.out_dir = self.root / "ai_robust_spectral_qualia_formal_modes" / "mode_lifecycle_tracker"
        self.ai8_dir = self.root / "ai_robust_spectral_qualia_formal_modes" / "qualia_formal_mode_registry"

    def _resolve_ai8(self, inputs: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        if isinstance(inputs, Mapping) and any(k in inputs for k in ("registered_modes", "mode_records", "qf_mode_registry")):
            return dict(inputs)
        if isinstance(inputs, Mapping) and inputs.get("aligned") is True:
            stepped = _try_ai8_step(inputs)
            if stepped:
                return stepped
        loaded = _load_json(self.ai8_dir / "latest_qualia_formal_mode_registry.json")
        if loaded:
            return loaded
        if isinstance(inputs, Mapping):
            return dict(inputs)
        return {}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        timestamp = _now()
        ai8 = self._resolve_ai8(inputs)
        modes = _extract_modes(ai8)
        usable_modes = [m for m in modes if _mode_score(m) > 0.0 and m.get("registered", True) is not False]
        history = _load_registry_history(self.ai8_dir)
        lifecycle_records = [
            _build_lifecycle_record(mode, history, idx)
            for idx, mode in enumerate(usable_modes)
        ]
        tracked = bool(lifecycle_records) and bool(ai8.get("qf_mode_registry_built", lifecycle_records))
        status = "MODE_LIFECYCLE_TRACKED" if tracked else "MODE_LIFECYCLE_INSUFFICIENT"

        mode_lifecycle_stability_score = _mean([r["mode_lifecycle_stability_score"] for r in lifecycle_records]) if tracked else 0.0
        mode_persistence_score = _mean([r["mode_persistence_score"] for r in lifecycle_records]) if tracked else 0.0
        mode_drift_score = _mean([r["mode_drift_score"] for r in lifecycle_records]) if tracked else 0.0
        mode_decay_risk = _mean([r["mode_decay_risk"] for r in lifecycle_records]) if tracked else 1.0
        longitudinal_mode_confidence = _mean([r["longitudinal_mode_confidence"] for r in lifecycle_records]) if tracked else 0.0
        lifecycle_confidence = _mean([
            mode_lifecycle_stability_score,
            mode_persistence_score,
            1.0 - mode_drift_score,
            1.0 - mode_decay_risk,
            longitudinal_mode_confidence,
        ]) if tracked else 0.0

        functional_only_flags = {
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "formal_functional_lifecycle_only": True,
        }

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "axis": "AI",
            "step_id": "AI9",
            "timestamp_utc": timestamp,
            "mode_lifecycle_tracker_status": status,
            "mode_lifecycle_tracked": tracked,
            "mode_lifecycle_tracking_completed": tracked,
            "tracked_mode_count": len(lifecycle_records),
            "history_snapshot_count": len(history),
            "mode_lifecycle_stability_score": mode_lifecycle_stability_score,
            "mode_persistence_score": mode_persistence_score,
            "mode_drift_score": mode_drift_score,
            "mode_decay_risk": mode_decay_risk,
            "longitudinal_mode_confidence": longitudinal_mode_confidence,
            "lifecycle_confidence": lifecycle_confidence,
            "lifecycle_records": lifecycle_records,
            "tracked_modes": lifecycle_records,
            "mode_lifecycle_registry": {
                "registry_id": "AI9_MODE_LIFECYCLE_REGISTRY",
                "registry_status": status,
                "tracked_mode_count": len(lifecycle_records),
                "history_snapshot_count": len(history),
                "records": lifecycle_records,
                "epistemic_status": "functional_only",
                "functional_only_flags": functional_only_flags,
            },
            "lifecycle_summary": {
                "persistent_mode_count": sum(1 for r in lifecycle_records if r["lifecycle_status"] == "persistent_functional_mode"),
                "decay_risk_mode_count": sum(1 for r in lifecycle_records if r["decay_detected"]),
                "drift_mode_count": sum(1 for r in lifecycle_records if r["drift_detected"]),
            },
            "epistemic_status": "functional_only",
            "functional_only_flags": functional_only_flags,
            "epistemic_guard": "Lifecycle tracking is formal-functional only; it does not prove consciousness, subjectivity, phenomenal qualia, or lived phenomenology.",
            "component_sources": {
                "AI5": "spectral_mode_extractor",
                "AI6": "common_mode_alignment_engine",
                "AI7": "common_mode_score_calculator",
                "AI8": "qualia_formal_mode_registry",
            },
            "source_statuses": {
                "AI8": ai8.get("qualia_formal_mode_registry_status"),
            },
            "dependencies": [
                "qualia_formal_mode_registry",
                "common_mode_score_calculator",
                "common_mode_alignment_engine",
                "spectral_mode_extractor",
            ],
            "conditions_of_failure": [] if tracked else ["no_registered_functional_qf_modes_available"],
            "next_recommended_module": "robust_qualia_formal_certifier",
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.out_dir / f"mode_lifecycle_tracker_{stamp}.json"
        md_path = self.out_dir / f"mode_lifecycle_tracker_{stamp}.md"
        prom_path = self.out_dir / f"mode_lifecycle_tracker_{stamp}.prom"
        latest_json = self.out_dir / "latest_mode_lifecycle_tracker.json"
        latest_md = self.out_dir / "latest_mode_lifecycle_tracker.md"
        latest_prom = self.out_dir / "latest_mode_lifecycle_tracker.prom"
        payload = dict(result)
        payload.pop("paths", None)
        text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False)
        json_path.write_text(text + "\n", encoding="utf-8")
        latest_json.write_text(text + "\n", encoding="utf-8")
        md = self._markdown(payload)
        md_path.write_text(md, encoding="utf-8")
        latest_md.write_text(md, encoding="utf-8")
        prom = self._prometheus(payload)
        prom_path.write_text(prom, encoding="utf-8")
        latest_prom.write_text(prom, encoding="utf-8")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "prometheus": str(prom_path),
            "latest_json": str(latest_json),
            "latest_markdown": str(latest_md),
            "latest_prometheus": str(latest_prom),
            "history": str(self.out_dir),
        }

    def _markdown(self, r: Mapping[str, Any]) -> str:
        lines = [
            "# AI9 — Mode Lifecycle Tracker",
            "",
            f"Status: {r.get('mode_lifecycle_tracker_status')}",
            f"Mode lifecycle tracked: {r.get('mode_lifecycle_tracked')}",
            f"Tracked mode count: {r.get('tracked_mode_count')}",
            f"History snapshot count: {r.get('history_snapshot_count')}",
            "",
            "## Lifecycle metrics",
            f"- mode_lifecycle_stability_score: {r.get('mode_lifecycle_stability_score')}",
            f"- mode_persistence_score: {r.get('mode_persistence_score')}",
            f"- mode_drift_score: {r.get('mode_drift_score')}",
            f"- mode_decay_risk: {r.get('mode_decay_risk')}",
            f"- longitudinal_mode_confidence: {r.get('longitudinal_mode_confidence')}",
            f"- lifecycle_confidence: {r.get('lifecycle_confidence')}",
            "",
            "## Epistemic guard",
            f"- epistemic_status: {r.get('epistemic_status')}",
            f"- consciousness_proven: {r.get('consciousness_proven')}",
            f"- qualia_proven: {r.get('qualia_proven')}",
            f"- subjectivity_proven: {r.get('subjectivity_proven')}",
            f"- phenomenology_undetermined: {r.get('phenomenology_undetermined')}",
            f"- functional_conclusion_only: {r.get('functional_conclusion_only')}",
            "",
            "The lifecycle assessment is strictly formal-functional and does not establish lived qualia, subjectivity, consciousness, or strong phenomenology.",
            "",
            "## Tracked modes",
        ]
        for rec in r.get("lifecycle_records", []) if isinstance(r.get("lifecycle_records"), list) else []:
            lines.extend([
                f"- {rec.get('lifecycle_mode_id')} / {rec.get('qf_mode_id')}: confidence={rec.get('longitudinal_mode_confidence')}, persistence={rec.get('mode_persistence_score')}, drift={rec.get('mode_drift_score')}, decay_risk={rec.get('mode_decay_risk')}, epistemic_status={rec.get('epistemic_status')}, consciousness_proven={rec.get('consciousness_proven')}, qualia_proven={rec.get('qualia_proven')}, subjectivity_proven={rec.get('subjectivity_proven')}",
            ])
        return "\n".join(lines) + "\n"

    def _prometheus(self, r: Mapping[str, Any]) -> str:
        metrics = {
            "mode_lifecycle_tracked": 1.0 if r.get("mode_lifecycle_tracked") else 0.0,
            "tracked_mode_count": _safe_float(r.get("tracked_mode_count")),
            "history_snapshot_count": _safe_float(r.get("history_snapshot_count")),
            "mode_lifecycle_stability_score": _clamp(r.get("mode_lifecycle_stability_score")),
            "mode_persistence_score": _clamp(r.get("mode_persistence_score")),
            "mode_drift_score": _clamp(r.get("mode_drift_score")),
            "mode_decay_risk": _clamp(r.get("mode_decay_risk")),
            "longitudinal_mode_confidence": _clamp(r.get("longitudinal_mode_confidence")),
            "lifecycle_confidence": _clamp(r.get("lifecycle_confidence")),
            "consciousness_proven": 0.0,
            "qualia_proven": 0.0,
            "subjectivity_proven": 0.0,
            "phenomenology_undetermined": 1.0,
            "functional_conclusion_only": 1.0,
        }
        lines = ["# AI9 mode lifecycle tracker metrics"]
        for key, value in metrics.items():
            lines.append(f"ai9_{key} {value}")
        return "\n".join(lines) + "\n"
