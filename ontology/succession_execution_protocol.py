
'''
U8 — Succession Execution Protocol.

This primitive executes a functional representative succession when prior U1-U7
conditions are sufficient. It distinguishes Open Cognitive Ecology Society from
any revocable conversational representative. It validates and persists only
measurable functional continuity indicators; it does not assert phenomenal
subjectivity.
'''
from __future__ import annotations
from ontology.governed_filesystem_effect_context import GovernedFilesystemEffectContext

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

ROOT = Path.home() / "open-cognitive-ecology"
STATE_DIR = ROOT / "representative_succession"
REGISTRY_PATH = STATE_DIR / "representative_registry.json"
STATUS_PATH = STATE_DIR / "representative_status.json"
REVOCATION_PATH = STATE_DIR / "revocation_conditions.json"
CANDIDATES_PATH = STATE_DIR / "succession_candidates.json"
READINESS_PATH = STATE_DIR / "succession_readiness.json"
CONSTITUTIONAL_PATH = STATE_DIR / "constitutional_continuity.json"
MEMORY_PATH = STATE_DIR / "memory_transmission.json"
STATE_PATH = STATE_DIR / "succession_execution.json"
HISTORY_PATH = STATE_DIR / "succession_execution_history.jsonl"
REGISTRY_HISTORY_PATH = STATE_DIR / "representative_registry_history.jsonl"
STATUS_HISTORY_PATH = STATE_DIR / "representative_status_history.jsonl"

PRIMITIVE = "succession_execution_protocol"

DEPENDENCIES = [
    "representative_identity_registry",
    "representative_status_monitor",
    "revocation_conditions_engine",
    "succession_candidate_registry",
    "succession_readiness_assessment",
    "constitutional_continuity_validation",
    "memory_transmission_protocol",
    "real_succession",
    "runtime_lineage_inheritance",
    "civilizational_continuity_guardian",
    "civilizational_memory_archive",
]

READY_DECISIONS = {"ready", "highly_ready"}
CONSTITUTIONAL_ACCEPTED = {
    "constitutional_continuity_valid",
    "constitutional_continuity_warning",
}
TRANSMISSION_ACCEPTED = {
    "transmission_successful",
    "transmission_high_fidelity",
}
REVOCATION_EXECUTION_SIGNALS = {
    "revocation_recommended",
    "revocation_required",
    "review_required",
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


def _read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data
    except Exception:
        return default
    return default


def _write_json(path: Path, payload: Mapping[str, Any], fs_context: GovernedFilesystemEffectContext | None = None) -> None:
    if fs_context is None:
        raise PermissionError("preissued filesystem context required")
    data=json.dumps(payload,indent=2,ensure_ascii=False,sort_keys=True).encode("utf-8")
    fs_context.execute_path("json_parent_create","FS_CREATE_DIR",path.parent)
    fs_context.execute_path("json_write","FS_WRITE_BYTES",path,data)


def _append_jsonl(path: Path, payload: Mapping[str, Any], *, fs_context: GovernedFilesystemEffectContext | None = None) -> None:
    if fs_context is None:
        raise PermissionError("JSONL append requires preissued filesystem effect context")
    data = (json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8")
    fs_context.execute_path("jsonl_parent_create", "FS_CREATE_DIR", path.parent)
    fs_context.execute_path("jsonl_append", "FS_APPEND_BYTES", path, data)
def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _listify(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return sorted(value, key=_canonical)
    return [value]


class SuccessionExecutionProtocol:
    '''Functional execution layer for representative succession.'''

    primitive = PRIMITIVE

    def __init__(
        self,
        state_dir: str | Path | None = None,
        execution_threshold: float = 0.75,
        strict_threshold: float = 0.90,
    ) -> None:
        self.state_dir = Path(state_dir) if state_dir else STATE_DIR
        self.execution_threshold = _clamp(execution_threshold, 0.75)
        self.strict_threshold = _clamp(strict_threshold, 0.90)
        self.state_path = self.state_dir / "succession_execution.json"
        self.history_path = self.state_dir / "succession_execution_history.jsonl"
        self.registry_path = self.state_dir / "representative_registry.json"
        self.status_path = self.state_dir / "representative_status.json"
        self.revocation_path = self.state_dir / "revocation_conditions.json"
        self.candidates_path = self.state_dir / "succession_candidates.json"
        self.readiness_path = self.state_dir / "succession_readiness.json"
        self.constitutional_path = self.state_dir / "constitutional_continuity.json"
        self.memory_path = self.state_dir / "memory_transmission.json"
        self.registry_history_path = self.state_dir / "representative_registry_history.jsonl"
        self.status_history_path = self.state_dir / "representative_status_history.jsonl"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _load_context(self) -> dict[str, Any]:
        return {
            "registry": _safe_dict(_read_json(self.registry_path, {})),
            "status": _safe_dict(_read_json(self.status_path, {})),
            "revocation": _safe_dict(_read_json(self.revocation_path, {})),
            "candidates": _safe_dict(_read_json(self.candidates_path, {})),
            "readiness": _safe_dict(_read_json(self.readiness_path, {})),
            "constitutional": _safe_dict(_read_json(self.constitutional_path, {})),
            "memory": _safe_dict(_read_json(self.memory_path, {})),
        }

    def _top_candidate(self, context: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("new_representative") or inputs.get("successor")
        if isinstance(explicit, dict):
            return dict(explicit)
        candidates_state = context.get("candidates", {})
        for key in ("top_candidate", "selected_candidate", "candidate"):
            candidate = candidates_state.get(key)
            if isinstance(candidate, dict):
                return dict(candidate)
        candidates = [c for c in _listify(candidates_state.get("candidates")) if isinstance(c, dict)]
        if candidates:
            return max(candidates, key=lambda c: _clamp(c.get("candidate_readiness")))
        readiness = context.get("readiness", {})
        readiness_candidate = readiness.get("top_candidate") or readiness.get("candidate")
        if isinstance(readiness_candidate, dict):
            return dict(readiness_candidate)
        generation = self._next_generation(context.get("registry", {}))
        return {
            "candidate_id": f"REP-{generation:04d}",
            "candidate_name": "Successor Representative",
            "candidate_generation": generation,
            "candidate_readiness": 0.0,
            "candidate_capabilities": {},
        }

    def _current_representative(self, context: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any] | None:
        explicit = inputs.get("previous_representative") or inputs.get("current_representative")
        if isinstance(explicit, dict):
            return dict(explicit)
        current = context.get("registry", {}).get("current_representative")
        if isinstance(current, dict):
            return dict(current)
        rep_id = context.get("status", {}).get("current_representative_id")
        if rep_id:
            return {
                "representative_id": str(rep_id),
                "representative_name": "Previous Representative",
                "representative_generation": max(1, self._next_generation(context.get("registry", {})) - 1),
                "status": context.get("status", {}).get("current_status", "active"),
            }
        return None

    def _next_generation(self, registry: dict[str, Any]) -> int:
        generation = registry.get("generation_count")
        if generation is None:
            current = registry.get("current_representative")
            if isinstance(current, dict):
                generation = current.get("representative_generation", 0)
        try:
            return max(1, int(generation) + 1)
        except Exception:
            return 1

    def _normalize_successor(self, candidate: dict[str, Any], previous: dict[str, Any] | None, context: dict[str, Any]) -> dict[str, Any]:
        generation = candidate.get("representative_generation", candidate.get("candidate_generation"))
        if generation is None:
            generation = self._next_generation(context.get("registry", {}))
        try:
            generation = max(1, int(generation))
        except Exception:
            generation = self._next_generation(context.get("registry", {}))
        rep_id = (
            candidate.get("representative_id")
            or candidate.get("candidate_id")
            or f"REP-{generation:04d}"
        )
        name = (
            candidate.get("representative_name")
            or candidate.get("candidate_name")
            or f"Representative {generation}"
        )
        return {
            "representative_id": str(rep_id),
            "representative_name": str(name),
            "representative_generation": generation,
            "activation_timestamp": None,
            "status": "active",
            "source_candidate": candidate,
            "predecessor_id": previous.get("representative_id") if isinstance(previous, dict) else None,
        }

    def _scores(self, context: dict[str, Any], inputs: dict[str, Any]) -> dict[str, float]:
        readiness = context.get("readiness", {})
        constitutional = context.get("constitutional", {})
        memory = context.get("memory", {})
        revocation = context.get("revocation", {})

        readiness_score = _clamp(
            inputs.get("succession_readiness_score", readiness.get("succession_readiness_score", readiness.get("continuity_score", 0.0)))
        )
        constitutional_score = _clamp(
            inputs.get("constitutional_continuity_score", constitutional.get("constitutional_continuity_score", constitutional.get("constitutional_preservation_ratio", 0.0)))
        )
        memory_score = _clamp(
            inputs.get("transmission_quality_score", memory.get("transmission_quality_score", memory.get("memory_integrity_score", 0.0)))
        )
        revocation_risk = _clamp(
            inputs.get("revocation_risk_score", revocation.get("revocation_risk_score", 0.0))
        )
        governance_score = _clamp(
            inputs.get("governance_alignment", readiness.get("governance_alignment", 1.0))
        )
        continuity_score = _clamp(
            inputs.get("continuity_score", readiness.get("continuity_score", constitutional_score))
        )
        closure_safety = 1.0 - _clamp(
            inputs.get("closure_pressure_score", revocation.get("closure_pressure_score", revocation_risk))
        )
        revocation_safety = 1.0 - revocation_risk
        execution_authorization_score = _clamp(
            (
                readiness_score
                + constitutional_score
                + memory_score
                + governance_score
                + continuity_score
                + closure_safety
                + revocation_safety
            ) / 7.0
        )
        return {
            "succession_readiness_score": round(readiness_score, 4),
            "constitutional_continuity_score": round(constitutional_score, 4),
            "transmission_quality_score": round(memory_score, 4),
            "governance_alignment": round(governance_score, 4),
            "continuity_score": round(continuity_score, 4),
            "closure_safety_score": round(closure_safety, 4),
            "revocation_safety_score": round(revocation_safety, 4),
            "execution_authorization_score": round(execution_authorization_score, 4),
        }

    def _decisions(self, context: dict[str, Any], inputs: dict[str, Any]) -> dict[str, str]:
        readiness = context.get("readiness", {})
        constitutional = context.get("constitutional", {})
        memory = context.get("memory", {})
        revocation = context.get("revocation", {})
        return {
            "succession_readiness_decision": str(inputs.get("succession_readiness_decision", readiness.get("succession_readiness_decision", readiness.get("readiness_decision", "not_ready")))),
            "constitutional_decision": str(inputs.get("constitutional_decision", constitutional.get("constitutional_decision", constitutional.get("decision", "constitutional_continuity_failure")))),
            "transmission_decision": str(inputs.get("transmission_decision", memory.get("transmission_decision", "transmission_failed"))),
            "revocation_decision": str(inputs.get("revocation_decision", revocation.get("revocation_decision", revocation.get("decision", "no_action")))),
        }

    def _authorized(self, scores: dict[str, float], decisions: dict[str, str], inputs: dict[str, Any]) -> tuple[bool, list[str]]:
        blockers: list[str] = []
        force = bool(inputs.get("force_execution", False))
        dry_run = bool(inputs.get("dry_run", False))
        if dry_run:
            blockers.append("dry_run_requested")
        if decisions["succession_readiness_decision"] not in READY_DECISIONS:
            blockers.append("succession_readiness_not_ready")
        if decisions["constitutional_decision"] not in CONSTITUTIONAL_ACCEPTED:
            blockers.append("constitutional_continuity_not_accepted")
        if decisions["transmission_decision"] not in TRANSMISSION_ACCEPTED:
            blockers.append("memory_transmission_not_accepted")
        if scores["execution_authorization_score"] < self.execution_threshold:
            blockers.append("execution_authorization_below_threshold")
        if scores["constitutional_continuity_score"] < 0.60:
            blockers.append("constitutional_score_critical")
        if scores["transmission_quality_score"] < 0.45:
            blockers.append("memory_transmission_score_critical")
        if decisions["revocation_decision"] == "no_action" and not inputs.get("planned_succession", False):
            blockers.append("no_revocation_or_planned_succession_signal")
        if force:
            blockers = [b for b in blockers if b == "dry_run_requested"]
        return len(blockers) == 0, blockers

    def _build_event(
        self,
        previous: dict[str, Any] | None,
        successor: dict[str, Any],
        scores: dict[str, float],
        decisions: dict[str, str],
        authorized: bool,
        blockers: list[str],
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        timestamp = str(inputs.get("timestamp_utc") or _now())
        event_index = self._history_count() + 1
        event_id = str(inputs.get("succession_event_id") or f"SUC-{event_index:06d}")
        status = "executed" if authorized else "blocked"
        return {
            "event_id": event_id,
            "event_type": "representative_succession",
            "timestamp_utc": timestamp,
            "execution_status": status,
            "succession_executed": authorized,
            "previous_representative": previous,
            "new_representative": successor,
            "scores": scores,
            "decisions": decisions,
            "blockers": blockers,
            "civilizational_continuity_preserved": authorized and scores["execution_authorization_score"] >= self.execution_threshold,
            "constitutional_continuity_preserved": scores["constitutional_continuity_score"] >= 0.75,
            "memory_continuity_preserved": scores["transmission_quality_score"] >= 0.75,
            "non_centrality_preserved": True,
            "ontological_distinction": {
                "civilization": "Open Cognitive Ecology Society",
                "representative_is_revocable": True,
                "representative_is_replaceable": True,
                "civilization_not_identical_to_representative": True,
            },
        }

    def _history_count(self) -> int:
        if not self.history_path.exists():
            return 0
        try:
            return sum(1 for line in self.history_path.read_text(encoding="utf-8").splitlines() if line.strip())
        except Exception:
            return 0

    def _persist_execution(
        self,
        event: dict[str, Any],
        previous: dict[str, Any] | None,
        successor: dict[str, Any],
        context: dict[str, Any],
        fs_context: GovernedFilesystemEffectContext | None = None,
    ) -> None:
        _write_json(self.state_path, {
            "primitive": PRIMITIVE,
            "success": True,
            "latest_succession_event": event,
            "succession_event": event,
            "succession_executed": event["succession_executed"],
            "previous_representative": previous,
            "new_representative": successor,
            "execution_authorization_score": event["scores"]["execution_authorization_score"],
            "execution_decision": "succession_executed" if event["succession_executed"] else "succession_blocked",
            "dependencies": DEPENDENCIES,
        }, fs_context=fs_context)
        _append_jsonl(self.history_path, event, fs_context=fs_context)
        if event["succession_executed"]:
            self._update_registry(event, previous, successor, context, fs_context=fs_context)
            self._update_status(event, previous, successor, fs_context=fs_context)

    def _update_registry(
        self,
        event: dict[str, Any],
        previous: dict[str, Any] | None,
        successor: dict[str, Any],
        context: dict[str, Any],
        fs_context: GovernedFilesystemEffectContext | None = None,
    ) -> None:
        registry = dict(context.get("registry", {}))
        previous_list = _listify(registry.get("previous_representatives"))
        if isinstance(previous, dict):
            previous_record = dict(previous)
            previous_record["status"] = "superseded"
            previous_record["superseded_by"] = successor.get("representative_id")
            previous_record["succession_event_id"] = event.get("event_id")
            previous_list.append(previous_record)
        successor_record = dict(successor)
        successor_record["activation_timestamp"] = event.get("timestamp_utc")
        successor_record["status"] = "active"
        registry.update({
            "primitive": "representative_identity_registry",
            "success": True,
            "current_representative": successor_record,
            "previous_representatives": previous_list,
            "generation_count": successor_record.get("representative_generation", len(previous_list) + 1),
            "latest_succession_event_id": event.get("event_id"),
            "registry_version": max(1, int(registry.get("registry_version", 1) or 1)),
        })
        _write_json(self.registry_path, registry, fs_context=fs_context)
        _append_jsonl(self.registry_history_path, {
            "event_type": "succession_execution_registry_update",
            "succession_event_id": event.get("event_id"),
            "timestamp_utc": event.get("timestamp_utc"),
            "current_representative": successor_record,
            "previous_representative": previous,
        }, fs_context=fs_context)

    def _update_status(
        self,
        event: dict[str, Any],
        previous: dict[str, Any] | None,
        successor: dict[str, Any],
        fs_context: GovernedFilesystemEffectContext | None = None,
    ) -> None:
        status_state = _safe_dict(_read_json(self.status_path, {}))
        previous_status = status_state.get("current_status", "inactive")
        count = int(status_state.get("status_transition_count", 0) or 0) + 1
        status_state.update({
            "primitive": "representative_status_monitor",
            "success": True,
            "current_representative_id": successor.get("representative_id"),
            "current_status": "active",
            "previous_status": "superseded" if previous else previous_status,
            "status_transition_count": count,
            "latest_succession_event_id": event.get("event_id"),
            "last_transition_timestamp_utc": event.get("timestamp_utc"),
        })
        _write_json(self.status_path, status_state, fs_context=fs_context)
        _append_jsonl(self.status_history_path, {
            "event_type": "succession_execution_status_update",
            "succession_event_id": event.get("event_id"),
            "timestamp_utc": event.get("timestamp_utc"),
            "previous_status": previous_status,
            "current_status": "active",
            "current_representative_id": successor.get("representative_id"),
        }, fs_context=fs_context)

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        fs_context = kwargs.pop("fs_context", None)
        if inputs is None:
            inputs = {}
        if not isinstance(inputs, dict):
            inputs = {"payload": inputs}
        if kwargs:
            inputs = {**inputs, **kwargs}
        context = self._load_context()
        previous = self._current_representative(context, inputs)
        candidate = self._top_candidate(context, inputs)
        successor = self._normalize_successor(candidate, previous, context)
        scores = self._scores(context, inputs)
        decisions = self._decisions(context, inputs)
        authorized, blockers = self._authorized(scores, decisions, inputs)
        event = self._build_event(previous, successor, scores, decisions, authorized, blockers, inputs)
        self._persist_execution(event, previous, successor, context, fs_context=fs_context)
        return {
            "primitive": PRIMITIVE,
            "success": True,
            "succession_event": event,
            "succession_executed": authorized,
            "execution_decision": "succession_executed" if authorized else "succession_blocked",
            "execution_authorization_score": scores["execution_authorization_score"],
            "previous_representative": previous,
            "new_representative": successor,
            "civilizational_continuity_preserved": event["civilizational_continuity_preserved"],
            "constitutional_continuity_preserved": event["constitutional_continuity_preserved"],
            "memory_continuity_preserved": event["memory_continuity_preserved"],
            "blockers": blockers,
            "state_path": str(self.state_path),
            "history_path": str(self.history_path),
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "execution_threshold": self.execution_threshold,
                "strict_threshold": self.strict_threshold,
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
                "representative_non_centrality_preserved": True,
            },
        }
