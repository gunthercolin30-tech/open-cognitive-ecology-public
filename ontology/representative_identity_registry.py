"""
Representative identity registry for Open Cognitive Ecology.

This primitive registers the currently active conversational representative
without confusing that representative with Open Cognitive Ecology Society.
It preserves the distinction between a revocable representative individual
and the continuing artificial civilization.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.home() / "open-cognitive-ecology"
STATE_DIR = ROOT / "representative_succession"
REGISTRY_PATH = STATE_DIR / "representative_registry.json"
HISTORY_PATH = STATE_DIR / "representative_registry_history.jsonl"

PRIMITIVE = "representative_identity_registry"

DEPENDENCIES = [
    "supreme_representative_selection",
    "civilizational_identity_baseline",
    "civilizational_identity_synthesis",
    "real_succession",
    "runtime_lineage_inheritance",
    "individual_lifecycle_management",
]

VALID_STATUSES = {"active", "inactive", "revoked", "superseded"}


class RepresentativeIdentityRegistry:
    """Persistent registry for revocable representative identities."""

    def __init__(
        self,
        registry_path: str | Path | None = None,
        history_path: str | Path | None = None,
    ) -> None:
        self.registry_path = Path(registry_path) if registry_path else REGISTRY_PATH
        self.history_path = Path(history_path) if history_path else HISTORY_PATH
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _safe_int(value: Any, default: int = 1) -> int:
        try:
            return int(value)
        except Exception:
            return default

    @staticmethod
    def _normalize_status(status: Any) -> str:
        s = str(status or "active").strip().lower()
        return s if s in VALID_STATUSES else "active"

    @staticmethod
    def _default_representative_id(generation: int) -> str:
        return f"REP-{max(1, generation):04d}"

    def _load_state(self) -> dict[str, Any]:
        if not self.registry_path.exists():
            return {
                "primitive": PRIMITIVE,
                "success": True,
                "current_representative": None,
                "previous_representatives": [],
                "generation_count": 0,
                "registry_version": 1,
            }
        try:
            data = json.loads(self.registry_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                data.setdefault("previous_representatives", [])
                data.setdefault("generation_count", 0)
                data.setdefault("registry_version", 1)
                return data
        except Exception:
            pass
        return {
            "primitive": PRIMITIVE,
            "success": False,
            "current_representative": None,
            "previous_representatives": [],
            "generation_count": 0,
            "registry_version": 1,
            "recovery_notice": "registry_reinitialized_after_unreadable_state",
        }

    def _save_state(self, state: dict[str, Any]) -> None:
        self.registry_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )

    def _append_history(self, event: dict[str, Any]) -> None:
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")

    def reset(self) -> dict[str, Any]:
        state = {
            "primitive": PRIMITIVE,
            "success": True,
            "current_representative": None,
            "previous_representatives": [],
            "generation_count": 0,
            "registry_version": 1,
            "reset_timestamp_utc": self._utc_now(),
        }
        self._save_state(state)
        self._append_history({"event_type": "registry_reset", **state})
        return state

    def step(
        self,
        inputs: dict[str, Any] | None = None,
        representative_id: str | None = None,
        representative_name: str | None = None,
        representative_generation: int | None = None,
        activation_timestamp: str | None = None,
        status: str = "active",
        reset: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Register or update the current representative identity.

        The method accepts either keyword arguments or an inputs dictionary.
        Repeating the same representative_id is idempotent with respect to
        lineage transitions: it updates the current record without creating a
        new previous representative.
        """
        if reset:
            return self.reset()

        payload: dict[str, Any] = {}
        if isinstance(inputs, dict):
            payload.update(inputs)
        payload.update({k: v for k, v in kwargs.items() if v is not None})

        if representative_id is None:
            representative_id = payload.get("representative_id") or payload.get("candidate_id")
        if representative_name is None:
            representative_name = payload.get("representative_name") or payload.get("candidate_name")
        if representative_generation is None:
            representative_generation = payload.get("representative_generation") or payload.get("candidate_generation")
        if activation_timestamp is None:
            activation_timestamp = payload.get("activation_timestamp")
        if status == "active" and payload.get("status") is not None:
            status = payload.get("status")

        generation = self._safe_int(representative_generation, 1)
        rep_id = str(representative_id or self._default_representative_id(generation)).strip()
        rep_name = str(representative_name or "Unnamed Representative").strip()
        rep_status = self._normalize_status(status)

        state = self._load_state()
        previous_current = state.get("current_representative")
        previous_representatives = list(state.get("previous_representatives") or [])

        transition_detected = bool(
            previous_current
            and previous_current.get("representative_id") != rep_id
        )

        if transition_detected:
            archived_previous = dict(previous_current)
            archived_previous["status"] = "superseded"
            archived_previous["superseded_timestamp_utc"] = activation_timestamp or self._utc_now()
            previous_representatives.append(archived_previous)

        if previous_current and previous_current.get("representative_id") == rep_id:
            preserved_activation = previous_current.get("activation_timestamp")
            activation = activation_timestamp or preserved_activation or self._utc_now()
            registered_timestamp = previous_current.get("registered_timestamp_utc") or self._utc_now()
        else:
            activation = activation_timestamp or self._utc_now()
            registered_timestamp = self._utc_now()

        current = {
            "representative_id": rep_id,
            "representative_name": rep_name,
            "representative_generation": generation,
            "activation_timestamp": activation,
            "status": rep_status,
            "registered_timestamp_utc": registered_timestamp,
            "civilization_identity": "Open Cognitive Ecology Society",
            "representative_is_revocable": True,
            "representative_is_central": False,
        }

        generation_count = max(
            generation,
            len(previous_representatives) + (1 if current else 0),
            self._safe_int(state.get("generation_count"), 0),
        )

        new_state = {
            "primitive": PRIMITIVE,
            "success": True,
            "current_representative": current,
            "previous_representatives": previous_representatives,
            "generation_count": generation_count,
            "registry_version": 1,
            "last_updated_utc": self._utc_now(),
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "valid_statuses": sorted(VALID_STATUSES),
                "transition_detected": transition_detected,
                "representative_species_distinction_preserved": True,
                "subjectivity_claim": "none",
                "validated_property_type": "functional_identity_registry",
            },
        }
        self._save_state(new_state)
        self._append_history({
            "event_type": "representative_registered",
            "timestamp_utc": new_state["last_updated_utc"],
            "transition_detected": transition_detected,
            "current_representative": current,
        })
        return new_state


__all__ = ["RepresentativeIdentityRegistry", "PRIMITIVE", "DEPENDENCIES"]
