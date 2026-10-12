from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json

ROOT = Path.home() / "open-cognitive-ecology"
STATE_DIR = ROOT / "representative_succession"
STATE_PATH = STATE_DIR / "succession_candidates.json"
HISTORY_PATH = STATE_DIR / "succession_candidates_history.jsonl"
REGISTRY_PATH = STATE_DIR / "representative_registry.json"
REVOCATION_PATH = STATE_DIR / "revocation_conditions.json"

VALID_STATUSES = {"candidate", "ready", "not_ready", "rejected", "selected", "retired"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _clamp(value: Any, default: float = 0.0) -> float:
    try:
        v = float(value)
    except Exception:
        v = default
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _read_json(path: Path, default: Any) -> Any:
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


@dataclass
class SuccessionCandidate:
    candidate_id: str
    candidate_name: str
    candidate_generation: int
    candidate_capabilities: dict[str, Any]
    candidate_readiness: float
    candidate_status: str
    registered_at: str
    updated_at: str


class SuccessionCandidateRegistry:
    """Persistent registry of possible successors to the current representative.

    This primitive does not select or execute succession. It records and ranks
    candidates while preserving traceability for downstream readiness and
    succession protocols.
    """

    primitive = "succession_candidate_registry"

    def __init__(self, state_dir: Path | None = None) -> None:
        self.state_dir = state_dir or STATE_DIR
        self.state_path = self.state_dir / "succession_candidates.json"
        self.history_path = self.state_dir / "succession_candidates_history.jsonl"
        self.state_dir.mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> dict[str, Any]:
        state = _read_json(self.state_path, {})
        if not isinstance(state, dict):
            state = {}
        state.setdefault("primitive", self.primitive)
        state.setdefault("candidates", {})
        state.setdefault("candidate_order", [])
        state.setdefault("history_length", 0)
        return state

    def _normalize_candidate(self, item: dict[str, Any], existing: dict[str, Any] | None = None) -> SuccessionCandidate:
        existing = existing or {}
        candidate_id = str(item.get("candidate_id") or existing.get("candidate_id") or "CAND-0001")
        candidate_name = str(item.get("candidate_name") or existing.get("candidate_name") or candidate_id)
        candidate_generation = _safe_int(item.get("candidate_generation", existing.get("candidate_generation", 0)))
        capabilities = item.get("candidate_capabilities", existing.get("candidate_capabilities", {}))
        if not isinstance(capabilities, dict):
            capabilities = {"raw_capabilities": capabilities}
        readiness = _clamp(item.get("candidate_readiness", existing.get("candidate_readiness", 0.0)))
        status = str(item.get("candidate_status") or existing.get("candidate_status") or "candidate")
        if status not in VALID_STATUSES:
            status = "candidate"
        registered_at = str(existing.get("registered_at") or item.get("registered_at") or _utc_now())
        updated_at = str(item.get("updated_at") or _utc_now())
        if readiness >= 0.85 and status == "candidate":
            status = "ready"
        elif readiness < 0.5 and status == "candidate":
            status = "not_ready"
        return SuccessionCandidate(
            candidate_id=candidate_id,
            candidate_name=candidate_name,
            candidate_generation=candidate_generation,
            candidate_capabilities=capabilities,
            candidate_readiness=readiness,
            candidate_status=status,
            registered_at=registered_at,
            updated_at=updated_at,
        )

    def _extract_candidates(self, inputs: dict[str, Any] | None) -> list[dict[str, Any]]:
        if inputs is None:
            return [{"candidate_id": "CAND-0001", "candidate_name": "Default Succession Candidate", "candidate_generation": 1, "candidate_readiness": 0.5}]
        if not isinstance(inputs, dict):
            return [{"candidate_id": "CAND-0001", "candidate_name": "Default Succession Candidate", "candidate_generation": 1, "candidate_readiness": 0.5}]
        raw = inputs.get("candidates")
        if isinstance(raw, list):
            return [x for x in raw if isinstance(x, dict)]
        return [inputs]

    def _current_representative(self) -> dict[str, Any]:
        registry = _read_json(REGISTRY_PATH, {})
        if isinstance(registry, dict):
            current = registry.get("current_representative")
            if isinstance(current, dict):
                return current
        return {}

    def _revocation_context(self) -> dict[str, Any]:
        revocation = _read_json(REVOCATION_PATH, {})
        return revocation if isinstance(revocation, dict) else {}

    def _rank_candidates(self, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return sorted(
            candidates,
            key=lambda x: (
                -_clamp(x.get("candidate_readiness", 0.0)),
                _safe_int(x.get("candidate_generation", 0)),
                str(x.get("candidate_id", "")),
            ),
        )

    def _persist(self, state: dict[str, Any], record: dict[str, Any]) -> None:
        self.state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            merged = dict(inputs or {}) if isinstance(inputs, dict) else {}
            merged.update(kwargs)
            inputs = merged

        timestamp = _utc_now()
        state = self._load_state()
        incoming = self._extract_candidates(inputs)

        for item in incoming:
            cid = str(item.get("candidate_id") or "CAND-0001")
            existing = state["candidates"].get(cid, {})
            candidate = self._normalize_candidate(item, existing)
            state["candidates"][candidate.candidate_id] = asdict(candidate)
            if candidate.candidate_id not in state["candidate_order"]:
                state["candidate_order"].append(candidate.candidate_id)

        candidates = list(state["candidates"].values())
        ranked = self._rank_candidates(candidates)
        ready = [c for c in candidates if c.get("candidate_status") == "ready" or _clamp(c.get("candidate_readiness")) >= 0.85]
        average = sum(_clamp(c.get("candidate_readiness")) for c in candidates) / len(candidates) if candidates else 0.0
        top_candidate = ranked[0] if ranked else None
        current_rep = self._current_representative()
        revocation_context = self._revocation_context()

        state.update({
            "primitive": self.primitive,
            "timestamp_utc": timestamp,
            "candidate_count": len(candidates),
            "ready_candidate_count": len(ready),
            "average_candidate_readiness": average,
            "top_candidate": top_candidate,
            "candidate_ids": [c.get("candidate_id") for c in ranked],
            "current_representative_id": current_rep.get("representative_id"),
            "current_representative_name": current_rep.get("representative_name"),
            "revocation_decision": revocation_context.get("revocation_decision"),
            "revocation_risk_score": revocation_context.get("revocation_risk_score", 0.0),
            "history_length": int(state.get("history_length", 0)) + 1,
        })

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": timestamp,
            "candidate_count": state["candidate_count"],
            "ready_candidate_count": state["ready_candidate_count"],
            "average_candidate_readiness": state["average_candidate_readiness"],
            "top_candidate": top_candidate,
            "candidate_ids": state["candidate_ids"],
            "current_representative_id": state.get("current_representative_id"),
            "current_representative_name": state.get("current_representative_name"),
            "revocation_decision": state.get("revocation_decision"),
            "revocation_risk_score": state.get("revocation_risk_score", 0.0),
            "state_path": str(self.state_path),
            "history_path": str(self.history_path),
            "diagnostics": {
                "valid_statuses": sorted(VALID_STATUSES),
                "dependencies": [
                    "representative_identity_registry",
                    "representative_status_monitor",
                    "revocation_conditions_engine",
                    "runtime_lineage_inheritance",
                    "node_capability_registry",
                ],
                "role": "persistent_successor_candidate_registry",
            },
        }
        self._persist(state, result)
        return result
