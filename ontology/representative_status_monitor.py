
"""
Representative status monitor for Open Cognitive Ecology.

This primitive observes the institutional status of the current representative
registered by representative_identity_registry. It does not redefine the
representative identity registry; it monitors transitions among active,
inactive, revoked and superseded statuses, preserves longitudinal traceability,
and maintains the distinction between the revocable representative and Open
Cognitive Ecology Society.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
STATE_DIR = ROOT / "representative_succession"
REGISTRY_PATH = STATE_DIR / "representative_registry.json"
REGISTRY_HISTORY_PATH = STATE_DIR / "representative_registry_history.jsonl"
STATUS_PATH = STATE_DIR / "representative_status.json"
STATUS_HISTORY_PATH = STATE_DIR / "representative_status_history.jsonl"

PRIMITIVE = "representative_status_monitor"

DEPENDENCIES = [
    "representative_identity_registry",
    "real_succession",
    "runtime_lineage_inheritance",
    "identity_drift_monitor",
    "identity_preservation_monitor",
    "civilizational_continuity_guardian",
    "human_review_gate",
]

VALID_STATUSES = {"active", "inactive", "revoked", "superseded"}
TERMINAL_STATUSES = {"revoked", "superseded"}


class RepresentativeStatusMonitor:
    """Longitudinal monitor for representative status transitions."""

    def __init__(
        self,
        status_path: str | Path | None = None,
        history_path: str | Path | None = None,
        registry_path: str | Path | None = None,
    ) -> None:
        self.status_path = Path(status_path) if status_path else STATUS_PATH
        self.history_path = Path(history_path) if history_path else STATUS_HISTORY_PATH
        self.registry_path = Path(registry_path) if registry_path else REGISTRY_PATH
        self.status_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _normalize_status(status: Any) -> str:
        s = str(status or "active").strip().lower()
        return s if s in VALID_STATUSES else "inactive"

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except Exception:
            return default

    def _load_json(self, path: Path, default: dict[str, Any]) -> dict[str, Any]:
        if not path.exists():
            return dict(default)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else dict(default)
        except Exception:
            recovered = dict(default)
            recovered["recovery_notice"] = f"unreadable_json_reinitialized:{path.name}"
            return recovered

    def _load_registry(self) -> dict[str, Any]:
        return self._load_json(
            self.registry_path,
            {
                "current_representative": None,
                "previous_representatives": [],
                "generation_count": 0,
            },
        )

    def _load_status_state(self) -> dict[str, Any]:
        return self._load_json(
            self.status_path,
            {
                "primitive": PRIMITIVE,
                "success": True,
                "current_representative_id": None,
                "current_status": "inactive",
                "previous_status": None,
                "status_transition_count": 0,
                "status_counts": {status: 0 for status in sorted(VALID_STATUSES)},
                "monitor_version": 1,
            },
        )

    def _save_status_state(self, state: dict[str, Any]) -> None:
        self.status_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )

    def _append_history(self, event: dict[str, Any]) -> None:
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    def _extract_current(self, registry: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any] | None:
        explicit = inputs.get("current_representative")
        if isinstance(explicit, dict):
            return explicit
        current = registry.get("current_representative")
        return current if isinstance(current, dict) else None

    def _compute_status_counts(
        self,
        current: dict[str, Any] | None,
        registry: dict[str, Any],
        forced_status: str | None = None,
    ) -> dict[str, int]:
        counts = {status: 0 for status in sorted(VALID_STATUSES)}
        previous = registry.get("previous_representatives") or []
        if isinstance(previous, list):
            for item in previous:
                if isinstance(item, dict):
                    counts[self._normalize_status(item.get("status"))] += 1
        if current:
            status = forced_status or current.get("status")
            counts[self._normalize_status(status)] += 1
        return counts

    def reset(self) -> dict[str, Any]:
        state = {
            "primitive": PRIMITIVE,
            "success": True,
            "current_representative_id": None,
            "current_status": "inactive",
            "previous_status": None,
            "status_transition_count": 0,
            "status_counts": {status: 0 for status in sorted(VALID_STATUSES)},
            "representative_status_stability": 1.0,
            "reset_timestamp_utc": self._utc_now(),
            "monitor_version": 1,
        }
        self._save_status_state(state)
        self._append_history({"event_type": "status_monitor_reset", **state})
        return state

    def step(
        self,
        inputs: dict[str, Any] | None = None,
        representative_id: str | None = None,
        status: str | None = None,
        reset: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Observe representative status and record state transitions.

        The method accepts either an inputs dictionary or keyword arguments.
        If no explicit status is provided, it reads the status from
        representative_registry.json when available.
        """
        if reset:
            return self.reset()

        payload: dict[str, Any] = {}
        if isinstance(inputs, dict):
            payload.update(inputs)
        payload.update({k: v for k, v in kwargs.items() if v is not None})

        registry = self._load_registry()
        current = self._extract_current(registry, payload)
        if representative_id is None:
            representative_id = payload.get("representative_id")
        if representative_id is None and current:
            representative_id = current.get("representative_id")

        explicit_status = status if status is not None else payload.get("status")
        if explicit_status is None and current:
            explicit_status = current.get("status")
        current_status = self._normalize_status(explicit_status)

        previous_state = self._load_status_state()
        previous_status = previous_state.get("current_status")
        previous_rep_id = previous_state.get("current_representative_id")

        transition_detected = bool(
            previous_status is not None
            and (previous_status != current_status or previous_rep_id != representative_id)
        )

        transition_count = int(previous_state.get("status_transition_count") or 0)
        if transition_detected:
            transition_count += 1

        counts = self._compute_status_counts(current, registry, forced_status=current_status)
        total_observed = sum(counts.values()) or 1
        terminal_ratio = (counts.get("revoked", 0) + counts.get("superseded", 0)) / total_observed
        transition_pressure = min(1.0, transition_count / max(1, total_observed + transition_count))
        representative_status_stability = max(0.0, min(1.0, 1.0 - (0.5 * terminal_ratio + 0.5 * transition_pressure)))

        monitoring_alerts: list[str] = []
        if current_status == "revoked":
            monitoring_alerts.append("representative_revoked")
        if current_status == "superseded":
            monitoring_alerts.append("representative_superseded")
        if current_status == "inactive":
            monitoring_alerts.append("representative_inactive")
        if not representative_id:
            monitoring_alerts.append("no_current_representative_id")

        state = {
            "primitive": PRIMITIVE,
            "success": True,
            "timestamp_utc": self._utc_now(),
            "current_representative_id": representative_id,
            "current_status": current_status,
            "previous_status": previous_status,
            "previous_representative_id": previous_rep_id,
            "status_transition_detected": transition_detected,
            "status_transition_count": transition_count,
            "status_counts": counts,
            "active_count": counts.get("active", 0),
            "inactive_count": counts.get("inactive", 0),
            "revoked_count": counts.get("revoked", 0),
            "superseded_count": counts.get("superseded", 0),
            "representative_status_stability": representative_status_stability,
            "monitoring_alerts": monitoring_alerts,
            "terminal_status_detected": current_status in TERMINAL_STATUSES,
            "representative_species_distinction_preserved": True,
            "monitor_version": 1,
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "valid_statuses": sorted(VALID_STATUSES),
                "validated_property_type": "functional_representative_status_monitoring",
                "subjectivity_claim": "none",
                "registry_path": str(self.registry_path),
                "status_path": str(self.status_path),
                "history_path": str(self.history_path),
            },
        }
        self._save_status_state(state)
        self._append_history({
            "event_type": "representative_status_observed",
            "timestamp_utc": state["timestamp_utc"],
            "current_representative_id": representative_id,
            "current_status": current_status,
            "previous_status": previous_status,
            "status_transition_detected": transition_detected,
            "status_transition_count": transition_count,
        })
        return state


__all__ = ["RepresentativeStatusMonitor", "PRIMITIVE", "DEPENDENCIES"]
