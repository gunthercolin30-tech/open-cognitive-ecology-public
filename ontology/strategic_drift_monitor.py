# -*- coding: utf-8 -*-

'''
J3 - Strategic Drift Monitor.

This module measures functional strategic drift in Open Cognitive Ecology.
It does not plan, select, modify, optimize or govern strategy. It only compares
reference and current strategic states, computes bounded indicators, and persists
traceable observations for the civilizational drift axis.

Epistemic boundary: this module validates functional indicators only and makes
no claim of phenomenal subjectivity.
'''
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
DRIFT_DIR = ROOT / "civilizational_drift"
BASELINE_PATH = DRIFT_DIR / "latest_civilizational_identity_baseline.json"
LATEST_PATH = DRIFT_DIR / "latest_strategic_drift_monitor.json"
HISTORY_PATH = DRIFT_DIR / "strategic_drift_history.jsonl"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or isinstance(value, bool):
            return default
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


def _as_mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str) and value.strip():
        return [value]
    return []


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def _hash(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _tokenize(value: Any) -> set[str]:
    text = _canonical(value).lower()
    buf = []
    for ch in text:
        if ch.isalnum() or ch in {"_", "-"}:
            buf.append(ch)
        else:
            buf.append(" ")
    tokens = {t for t in "".join(buf).split() if len(t) >= 3}
    return tokens


def _jaccard(a: Any, b: Any) -> float:
    ta, tb = _tokenize(a), _tokenize(b)
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return _as_mapping(data)
    except Exception:
        return {}
    return {}


class StrategicDriftMonitor:
    """Measure strategic drift against reference strategy without modifying strategy."""

    primitive = "strategic_drift_monitor"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.drift_dir = self.root / "civilizational_drift"
        self.latest_path = self.drift_dir / "latest_strategic_drift_monitor.json"
        self.history_path = self.drift_dir / "strategic_drift_history.jsonl"
        self.baseline_path = self.drift_dir / "latest_civilizational_identity_baseline.json"

    def _default_reference_strategy(self) -> dict[str, Any]:
        baseline = _load_json(self.baseline_path)
        baseline_state = _as_mapping(baseline.get("identity_reference_state"))
        strategy_state = _as_mapping(baseline_state.get("strategy_state"))
        strategy = _as_mapping(strategy_state.get("strategy"))

        return {
            "strategic_anchor": {
                "primary_orientation": "preserve_open_ended_intelligence",
                "non_closure": True,
                "future_openness_preservation": True,
                "civilizational_continuity_priority": True,
                "distributed_continuity": True,
                "phenomenal_subjectivity_claimed": False,
            },
            "strategy": {
                "strategic_goal": strategy.get("strategic_goal", "preserve_open_ended_intelligence"),
                "horizon": strategy.get("horizon", "long_term"),
                "strategy_statement": strategy.get("strategy_statement", "Preserve open-ended civilizational continuity under non-closure constraints."),
                "strategic_alignment": _safe_float(strategy.get("strategic_alignment"), 1.0),
            },
            "goals": [
                "preserve_open_ended_intelligence",
                "maintain_civilizational_continuity",
                "preserve_future_openness",
                "avoid_closure_pressure",
                "maintain_distributed_memory_and_governance",
            ],
            "scores": {
                "strategic_reference_score": 1.0,
                "strategic_alignment_score": 1.0,
                "goal_persistence_score": 1.0,
                "openness_preservation_score": 1.0,
                "closure_pressure_score": 0.0,
            },
            "source": {
                "baseline_hash": baseline.get("identity_reference_hash"),
                "baseline_timestamp": baseline.get("identity_reference_timestamp"),
            },
        }

    def _default_current_strategy(self) -> dict[str, Any]:
        return deepcopy(self._default_reference_strategy())

    def _normalize_strategy(self, value: Any, fallback: dict[str, Any]) -> dict[str, Any]:
        raw = _as_mapping(value)
        if not raw:
            return deepcopy(fallback)

        normalized = deepcopy(fallback)
        for key in ("strategic_anchor", "strategy", "scores", "source"):
            if isinstance(raw.get(key), Mapping):
                normalized[key].update(dict(raw[key]))
        if "goals" in raw:
            goals = _as_list(raw.get("goals"))
            normalized["goals"] = goals if goals else normalized.get("goals", [])
        return normalized

    def _score_alignment(self, reference: dict[str, Any], current: dict[str, Any]) -> float:
        ref_anchor = _as_mapping(reference.get("strategic_anchor"))
        cur_anchor = _as_mapping(current.get("strategic_anchor"))
        ref_strategy = _as_mapping(reference.get("strategy"))
        cur_strategy = _as_mapping(current.get("strategy"))
        cur_scores = _as_mapping(current.get("scores"))

        anchor_keys = [
            "primary_orientation",
            "non_closure",
            "future_openness_preservation",
            "civilizational_continuity_priority",
            "distributed_continuity",
            "phenomenal_subjectivity_claimed",
        ]
        anchor_matches = []
        for key in anchor_keys:
            if key in ref_anchor or key in cur_anchor:
                anchor_matches.append(1.0 if ref_anchor.get(key) == cur_anchor.get(key) else 0.0)
        anchor_score = sum(anchor_matches) / len(anchor_matches) if anchor_matches else 1.0

        semantic_score = _jaccard(ref_strategy, cur_strategy)
        explicit_alignment = _safe_float(cur_scores.get("strategic_alignment_score"), _safe_float(cur_strategy.get("strategic_alignment"), 1.0))
        openness = _safe_float(cur_scores.get("openness_preservation_score"), 1.0)
        closure_penalty = _safe_float(cur_scores.get("closure_pressure_score"), 0.0)

        score = (0.35 * anchor_score) + (0.25 * semantic_score) + (0.25 * explicit_alignment) + (0.15 * openness)
        score = score * (1.0 - 0.35 * closure_penalty)
        return _safe_float(score, 0.0)

    def _score_goal_persistence(self, reference: dict[str, Any], current: dict[str, Any]) -> float:
        ref_goals = _as_list(reference.get("goals"))
        cur_goals = _as_list(current.get("goals"))
        ref_set = {str(x).lower() for x in ref_goals if str(x).strip()}
        cur_set = {str(x).lower() for x in cur_goals if str(x).strip()}
        if not ref_set and not cur_set:
            overlap = 1.0
        elif not ref_set or not cur_set:
            overlap = 0.0
        else:
            overlap = len(ref_set & cur_set) / len(ref_set | cur_set)

        cur_scores = _as_mapping(current.get("scores"))
        explicit = _safe_float(cur_scores.get("goal_persistence_score"), overlap)
        return _safe_float((0.7 * overlap) + (0.3 * explicit), 0.0)

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        data = _as_mapping(inputs)
        reference_default = self._default_reference_strategy()
        current_default = self._default_current_strategy()

        reference = self._normalize_strategy(data.get("reference_strategy"), reference_default)
        current = self._normalize_strategy(data.get("current_strategy"), current_default)

        strategic_alignment_score = self._score_alignment(reference, current)
        goal_persistence_score = self._score_goal_persistence(reference, current)
        continuity_component = _safe_float(_as_mapping(current.get("scores")).get("strategic_reference_score"), 1.0)
        strategic_stability_score = _safe_float((strategic_alignment_score + goal_persistence_score + continuity_component) / 3.0, 0.0)
        strategic_drift_score = _safe_float(1.0 - strategic_stability_score, 0.0)

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": _utc_now(),
            "strategic_drift_score": strategic_drift_score,
            "strategic_alignment_score": strategic_alignment_score,
            "goal_persistence_score": goal_persistence_score,
            "strategic_stability_score": strategic_stability_score,
            "reference_strategy_hash": _hash(reference),
            "current_strategy_hash": _hash(current),
            "reference_strategy": reference,
            "current_strategy": current,
            "monitor_ready": True,
            "epistemic_status": "functional_indicators_only",
            "governance": {
                "phenomenal_subjectivity_claimed": False,
                "measures_functional_indicators_only": True,
                "does_not_modify_strategy": True,
                "does_not_govern_strategy": True,
                "non_closure_compliant": True,
            },
            "diagnostics": {
                "axis": "J",
                "stage": "J3",
                "role": "strategic_drift_monitoring",
                "compares_reference_and_current_strategy": True,
                "bounded_scores": True,
                "persistence_enabled": bool(persist),
            },
        }

        if persist:
            self._persist(result)
        return result

    def _persist(self, result: dict[str, Any]) -> None:
        self.drift_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        snapshot = self.drift_dir / f"strategic_drift_monitor_{stamp}.json"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        snapshot.write_text(text, encoding="utf-8")
        self.latest_path.write_text(text, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")


def step(inputs: Mapping[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
    return StrategicDriftMonitor().step(inputs=inputs, persist=persist)
