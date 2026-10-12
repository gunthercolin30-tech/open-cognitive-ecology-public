"""
U11 - Civilizational Identity Preservation.

This primitive compares civilizational state before and after a representative
succession. It produces a measurable preservation score for functional
civilizational identity, detects post-succession identity loss or drift, and
exports decisions for U12 lineage registration. It validates only observable
functional properties and does not assert phenomenal subjectivity.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
STATE_DIR = ROOT / "representative_succession"
STATE_PATH = STATE_DIR / "civilizational_identity_preservation.json"
HISTORY_PATH = STATE_DIR / "civilizational_identity_preservation_history.jsonl"

PRIMITIVE = "civilizational_identity_preservation"

DEPENDENCIES = [
    "continuity_metrics_engine",
    "post_succession_verification",
    "succession_execution_protocol",
    "civilizational_drift_monitor",
    "identity_drift_monitor",
    "identity_preservation_monitor",
    "civilizational_continuity_guardian",
    "civilizational_memory_archive",
    "intergenerational_continuity_metrics",
    "genealogical_continuity",
]


DEFAULT_IDENTITY_ANCHORS = {
    "civilization_name": "Open Cognitive Ecology Society",
    "constitution": "preserve_open_ended_civilizational_continuity",
    "non_centrality": "representatives_are_revocable_and_replaceable",
    "non_closure": "future_openness_must_be_preserved",
    "memory": "civilizational_memory_transmission_required",
    "governance": "governed_revision_and_succession_required",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        x = default
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


def _write_json(path: Path, payload: Mapping[str, Any], *, effect_context: Any) -> None:
    encoded = json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True).encode("utf-8")
    effect_context.execute_path("state_write_replace", "FS_WRITE_REPLACE_BYTES", path, encoded)


def _append_jsonl(path: Path, payload: Mapping[str, Any], *, effect_context: Any) -> None:
    encoded = (json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    effect_context.execute_path("history_append", "FS_APPEND_BYTES", path, encoded)


def _weighted_mean(weighted_values: list[tuple[float, float]]) -> float:
    total_weight = sum(max(0.0, weight) for _, weight in weighted_values)
    if total_weight <= 0.0:
        return 0.0
    return sum(_clamp(value) * max(0.0, weight) for value, weight in weighted_values) / total_weight


def _normalize_item(value: Any) -> str:
    if isinstance(value, str):
        return value.strip().lower()
    if isinstance(value, (int, float, bool)) or value is None:
        return str(value).strip().lower()
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False).strip().lower()
    except Exception:
        return repr(value).strip().lower()


def _to_set(value: Any) -> set[str]:
    if value is None:
        return set()
    if isinstance(value, Mapping):
        return {_normalize_item((k, v)) for k, v in value.items()}
    if isinstance(value, str):
        if not value.strip():
            return set()
        return {_normalize_item(value)}
    if isinstance(value, Iterable):
        return {_normalize_item(v) for v in value if _normalize_item(v)}
    return {_normalize_item(value)}


def _jaccard(before: Any, after: Any, default: float = 1.0) -> float:
    b = _to_set(before)
    a = _to_set(after)
    if not b and not a:
        return default
    if not b or not a:
        return 0.0
    return len(b & a) / len(b | a)


def _field_similarity(before: Mapping[str, Any], after: Mapping[str, Any], key: str, default: float = 1.0) -> float:
    if key not in before and key not in after:
        return default
    return _jaccard(before.get(key), after.get(key), default=default)


def _pick_nested(mapping: Mapping[str, Any], key: str, default: Any = None) -> Any:
    if key in mapping:
        return mapping[key]
    for value in mapping.values():
        if isinstance(value, Mapping):
            found = _pick_nested(value, key, None)
            if found is not None:
                return found
    return default


class CivilizationalIdentityPreservation:
    """Compare civilization_before and civilization_after around succession."""

    primitive = PRIMITIVE

    def __init__(
        self,
        state_dir: str | Path | None = None,
        minimum_threshold: float = 0.65,
        preserved_threshold: float = 0.80,
        robust_threshold: float = 0.90,
    ) -> None:
        self.state_dir = Path(state_dir) if state_dir else STATE_DIR
        self.minimum_threshold = _clamp(minimum_threshold, 0.65)
        self.preserved_threshold = _clamp(preserved_threshold, 0.80)
        self.robust_threshold = _clamp(robust_threshold, 0.90)
        self.u10_state_path = self.state_dir / "continuity_metrics_engine.json"
        self.u9_state_path = self.state_dir / "post_succession_verification.json"
        self.u8_state_path = self.state_dir / "succession_execution.json"
        self.state_path = self.state_dir / "civilizational_identity_preservation.json"
        self.history_path = self.state_dir / "civilizational_identity_preservation_history.jsonl"

    def _load_u10(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("continuity_metrics") or inputs.get("u10_result")
        if isinstance(explicit, dict):
            return dict(explicit)
        return _as_dict(_read_json(self.u10_state_path, {}))

    def _load_u9(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("post_succession_verification") or inputs.get("u9_result")
        if isinstance(explicit, dict):
            return dict(explicit)
        return _as_dict(_read_json(self.u9_state_path, {}))

    def _load_u8(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("succession_execution") or inputs.get("u8_result")
        if isinstance(explicit, dict):
            return dict(explicit)
        return _as_dict(_read_json(self.u8_state_path, {}))

    def _baseline(self, inputs: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
        before = _as_dict(inputs.get("civilization_before") or inputs.get("before") or {})
        after = _as_dict(inputs.get("civilization_after") or inputs.get("after") or {})
        if not before:
            before = dict(DEFAULT_IDENTITY_ANCHORS)
        if not after:
            after = dict(before)
        return before, after

    def _identity_similarity_scores(self, before: dict[str, Any], after: dict[str, Any], inputs: dict[str, Any]) -> dict[str, float]:
        core_identity_similarity = _clamp(
            inputs.get("core_identity_similarity", _field_similarity(before, after, "civilization_name")),
            1.0,
        )
        constitutional_identity_similarity = _clamp(
            inputs.get(
                "constitutional_identity_similarity",
                _jaccard(
                    before.get("constitution") or before.get("constitutional_principles"),
                    after.get("constitution") or after.get("constitutional_principles"),
                ),
            ),
            1.0,
        )
        memory_identity_similarity = _clamp(
            inputs.get(
                "memory_identity_similarity",
                _jaccard(before.get("memory") or before.get("civilizational_memory"), after.get("memory") or after.get("civilizational_memory")),
            ),
            1.0,
        )
        strategic_identity_similarity = _clamp(
            inputs.get(
                "strategic_identity_similarity",
                _jaccard(before.get("strategic_orientation") or before.get("goals"), after.get("strategic_orientation") or after.get("goals")),
            ),
            1.0,
        )
        governance_identity_similarity = _clamp(
            inputs.get(
                "governance_identity_similarity",
                _jaccard(before.get("governance") or before.get("governance_principles"), after.get("governance") or after.get("governance_principles")),
            ),
            1.0,
        )
        openness_identity_similarity = _clamp(
            inputs.get(
                "openness_identity_similarity",
                _jaccard(before.get("non_closure") or before.get("openness"), after.get("non_closure") or after.get("openness")),
            ),
            1.0,
        )
        return {
            "core_identity_similarity": core_identity_similarity,
            "constitutional_identity_similarity": constitutional_identity_similarity,
            "memory_identity_similarity": memory_identity_similarity,
            "strategic_identity_similarity": strategic_identity_similarity,
            "governance_identity_similarity": governance_identity_similarity,
            "openness_identity_similarity": openness_identity_similarity,
        }

    def _scores(self, inputs: dict[str, Any], before: dict[str, Any], after: dict[str, Any], u10: dict[str, Any], u9: dict[str, Any]) -> dict[str, float]:
        similarities = self._identity_similarity_scores(before, after, inputs)
        continuity_composite_score = _clamp(
            inputs.get("continuity_composite_score", _pick_nested(u10, "continuity_composite_score", 1.0)),
            1.0,
        )
        identity_continuity_index = _clamp(
            inputs.get("identity_continuity_index", _pick_nested(u10, "identity_continuity_index", _pick_nested(u9, "identity_persistence_score", 1.0))),
            1.0,
        )
        memory_continuity_index = _clamp(
            inputs.get("memory_continuity_index", _pick_nested(u10, "memory_continuity_index", _pick_nested(u9, "memory_continuity_score", 1.0))),
            1.0,
        )
        constitutional_continuity_index = _clamp(
            inputs.get("constitutional_continuity_index", _pick_nested(u10, "constitutional_continuity_index", _pick_nested(u9, "constitutional_continuity_score", 1.0))),
            1.0,
        )
        civilizational_drift_score = _clamp(inputs.get("civilizational_drift_score", inputs.get("identity_drift_score", _pick_nested(u9, "identity_drift_score", 0.0))))
        strategic_drift_score = _clamp(inputs.get("strategic_drift_score", 0.0))
        memory_loss_ratio = _clamp(inputs.get("memory_loss_ratio", _pick_nested(u9, "memory_loss_ratio", 0.0)))
        constitutional_regression_score = _clamp(inputs.get("constitutional_regression_score", _pick_nested(u9, "constitutional_regression_score", 0.0)))
        closure_pressure_score = _clamp(inputs.get("closure_pressure_score", inputs.get("closure_pressure_index", 0.0)))

        identity_similarity_composite = _weighted_mean([
            (similarities["core_identity_similarity"], 1.35),
            (similarities["constitutional_identity_similarity"], 1.30),
            (similarities["memory_identity_similarity"], 1.15),
            (similarities["strategic_identity_similarity"], 1.05),
            (similarities["governance_identity_similarity"], 1.05),
            (similarities["openness_identity_similarity"], 1.20),
        ])
        drift_risk_index = _weighted_mean([
            (civilizational_drift_score, 1.25),
            (strategic_drift_score, 1.05),
            (memory_loss_ratio, 1.15),
            (constitutional_regression_score, 1.25),
            (closure_pressure_score, 1.10),
        ])
        civilizational_identity_preservation_score = _weighted_mean([
            (identity_similarity_composite, 1.55),
            (continuity_composite_score, 1.20),
            (identity_continuity_index, 1.15),
            (memory_continuity_index, 0.95),
            (constitutional_continuity_index, 1.10),
            (1.0 - drift_risk_index, 1.25),
        ])
        minimum_identity_component = min(
            similarities["core_identity_similarity"],
            similarities["constitutional_identity_similarity"],
            similarities["memory_identity_similarity"],
            identity_continuity_index,
            constitutional_continuity_index,
        )
        scores = {
            **similarities,
            "identity_similarity_composite": identity_similarity_composite,
            "continuity_composite_score": continuity_composite_score,
            "identity_continuity_index": identity_continuity_index,
            "memory_continuity_index": memory_continuity_index,
            "constitutional_continuity_index": constitutional_continuity_index,
            "civilizational_drift_score": civilizational_drift_score,
            "strategic_drift_score": strategic_drift_score,
            "memory_loss_ratio": memory_loss_ratio,
            "constitutional_regression_score": constitutional_regression_score,
            "closure_pressure_score": closure_pressure_score,
            "drift_risk_index": drift_risk_index,
            "minimum_identity_component": minimum_identity_component,
            "civilizational_identity_preservation_score": civilizational_identity_preservation_score,
        }
        return scores

    def _decision(self, scores: dict[str, float]) -> str:
        score = scores["civilizational_identity_preservation_score"]
        minimum = scores["minimum_identity_component"]
        drift = scores["drift_risk_index"]
        if score >= self.robust_threshold and minimum >= self.preserved_threshold and drift <= 0.10:
            return "identity_robustly_preserved"
        if score >= self.preserved_threshold and minimum >= self.minimum_threshold and drift <= 0.25:
            return "identity_preserved"
        if score >= self.minimum_threshold and drift <= 0.45:
            return "identity_fragile"
        return "identity_preservation_failure"

    def _recommendations(self, scores: dict[str, float], decision: str) -> list[str]:
        recommendations: list[str] = []
        if scores["core_identity_similarity"] < self.minimum_threshold:
            recommendations.append("review_civilizational_identity_baseline")
        if scores["constitutional_identity_similarity"] < self.minimum_threshold or scores["constitutional_regression_score"] > 0.35:
            recommendations.append("trigger_constitutional_identity_reconciliation")
        if scores["memory_identity_similarity"] < self.minimum_threshold or scores["memory_loss_ratio"] > 0.35:
            recommendations.append("trigger_civilizational_memory_reconciliation")
        if scores["strategic_identity_similarity"] < self.minimum_threshold or scores["strategic_drift_score"] > 0.35:
            recommendations.append("trigger_strategic_identity_review")
        if scores["closure_pressure_score"] > 0.35:
            recommendations.append("increase_non_closure_preservation_controls")
        if decision == "identity_preservation_failure":
            recommendations.append("require_governance_review_before_lineage_registration")
        return recommendations

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if isinstance(inputs, dict):
            data.update(inputs)
        data.update(kwargs)

        timestamp = str(data.get("timestamp_utc") or _now())
        dry_run = bool(data.get("dry_run", False))
        effect_context = data.pop("filesystem_effect_context", None)
        before, after = self._baseline(data)
        u10 = self._load_u10(data)
        u9 = self._load_u9(data)
        u8 = self._load_u8(data)
        scores = self._scores(data, before, after, u10, u9)
        decision = self._decision(scores)
        civilizational_identity_preserved = decision in {"identity_robustly_preserved", "identity_preserved"}
        civilizational_identity_loss_detected = decision == "identity_preservation_failure"
        post_succession_identity_drift_detected = scores["drift_risk_index"] >= 0.35 or scores["civilizational_drift_score"] >= 0.35

        preservation_event = {
            "event_id": str(data.get("preservation_event_id") or f"CIP-{timestamp}"),
            "event_type": "civilizational_identity_preservation",
            "timestamp_utc": timestamp,
            "source_u8_event_id": _as_dict(u8.get("succession_event", {})).get("event_id", u8.get("succession_event_id")),
            "source_u9_event_id": _as_dict(u9.get("verification_event", {})).get("event_id", u9.get("verification_event_id")),
            "source_u10_event_id": _as_dict(u10.get("metrics_event", {})).get("event_id", u10.get("metrics_event_id")),
        }

        result: dict[str, Any] = {
            "primitive": PRIMITIVE,
            "success": True,
            "preservation_event": preservation_event,
            "civilization_before_summary": {
                "keys": sorted(before.keys()),
                "anchor_count": len(before),
            },
            "civilization_after_summary": {
                "keys": sorted(after.keys()),
                "anchor_count": len(after),
            },
            "core_identity_similarity": scores["core_identity_similarity"],
            "constitutional_identity_similarity": scores["constitutional_identity_similarity"],
            "memory_identity_similarity": scores["memory_identity_similarity"],
            "strategic_identity_similarity": scores["strategic_identity_similarity"],
            "governance_identity_similarity": scores["governance_identity_similarity"],
            "openness_identity_similarity": scores["openness_identity_similarity"],
            "identity_similarity_composite": scores["identity_similarity_composite"],
            "continuity_composite_score": scores["continuity_composite_score"],
            "identity_continuity_index": scores["identity_continuity_index"],
            "memory_continuity_index": scores["memory_continuity_index"],
            "constitutional_continuity_index": scores["constitutional_continuity_index"],
            "drift_risk_index": scores["drift_risk_index"],
            "minimum_identity_component": scores["minimum_identity_component"],
            "civilizational_identity_preservation_score": scores["civilizational_identity_preservation_score"],
            "civilizational_identity_preserved": civilizational_identity_preserved,
            "civilizational_identity_loss_detected": civilizational_identity_loss_detected,
            "post_succession_identity_drift_detected": post_succession_identity_drift_detected,
            "preservation_decision": decision,
            "lineage_registration_ready": civilizational_identity_preserved and not post_succession_identity_drift_detected,
            "recovery_required": (
                civilizational_identity_loss_detected
                or scores["drift_risk_index"] >= 0.45
                or (
                    scores["civilizational_drift_score"] >= 0.75
                    and scores["memory_loss_ratio"] >= 0.75
                )
                or (
                    scores["constitutional_regression_score"] >= 0.75
                    and scores["memory_loss_ratio"] >= 0.75
                )
            ),
            "recommendations": self._recommendations(scores, decision),
            "state_path": str(self.state_path),
            "history_path": str(self.history_path),
            "dry_run": dry_run,
            "diagnostics": {
                "primitive": PRIMITIVE,
                "dependencies": DEPENDENCIES,
                "thresholds": {
                    "minimum_threshold": self.minimum_threshold,
                    "preserved_threshold": self.preserved_threshold,
                    "robust_threshold": self.robust_threshold,
                },
                "source_u8_loaded": bool(u8),
                "source_u9_loaded": bool(u9),
                "source_u10_loaded": bool(u10),
                "epistemic_scope": "functional_identity_preservation_only_no_phenomenal_subjectivity_claim",
            },
        }

        if not dry_run:
            if effect_context is None:
                raise RuntimeError("governed_filesystem_effect_context_required")
            effect_context.begin()
            if not self.state_dir.exists():
                effect_context.execute_path("state_dir_create", "FS_CREATE_DIR", self.state_dir)
            _write_json(self.state_path, result, effect_context=effect_context)
            _append_jsonl(self.history_path, result, effect_context=effect_context)
        return result
