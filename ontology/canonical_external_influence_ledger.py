"""
R8 — Canonical External Influence Ledger.

This primitive provides a canonical JSONL ledger for externally-originated
influence. It standardizes hashes, identifiers, linkage fields and integration
status without granting any external provider direct write authority.

R8.1 correction: canonical_record_hash is computed from stable fields only.
The operational timestamp is preserved in the ledger but excluded from the
canonical hash so that identical external influence payloads produce identical
canonical hashes across repeated evaluations.

It measures functional traceability only and does not assert phenomenal
subjectivity.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=str, separators=(",", ":"))


def _sha256_text(value: Any) -> str:
    text = value if isinstance(value, str) else _canonical_json(value)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return sorted(value)
    return [value]


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True


def _read_jsonl(path: Path, limit: int = 250) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()[-limit:]
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except Exception:
                continue
            if isinstance(item, dict):
                rows.append(item)
    except Exception:
        return []
    return rows


class CanonicalExternalInfluenceLedger:
    """
    Canonical ledger for governed external influence.

    Required canonical fields:
      - query_id
      - model
      - provider
      - prompt_hash
      - response_hash
      - timestamp
      - recommendations
      - risk_flags
      - integration_status
      - linked_decision_id
      - linked_action_id
      - linked_commit

    The canonical_record_hash deliberately excludes timestamp and other runtime
    diagnostics. This makes repeated evaluations of the same external influence
    payload deterministic while retaining timestamped historical records.
    """

    primitive = "CANONICAL_EXTERNAL_INFLUENCE_LEDGER"
    dependencies = [
        "external_influence_adoption_gate",
        "external_influence_traceability_engine",
        "external_decision_record_extension",
        "external_commit_traceability_hook",
        "external_response_parser",
    ]

    required_fields = [
        "query_id",
        "model",
        "provider",
        "prompt_hash",
        "response_hash",
        "timestamp",
        "recommendations",
        "risk_flags",
        "integration_status",
        "linked_decision_id",
        "linked_action_id",
        "linked_commit",
    ]

    stable_hash_fields = [
        "query_id",
        "model",
        "provider",
        "prompt_hash",
        "response_hash",
        "recommendations",
        "risk_flags",
        "integration_status",
        "linked_decision_id",
        "linked_action_id",
        "linked_commit",
        "external_influence_id",
        "direct_write_requested",
        "human_review_required",
        "human_approval_confirmed",
        "blocked_reasons",
        "adoption_authorized",
        "direct_write_allowed",
        "canonical_trace_complete",
    ]

    direct_authority_statuses = {
        "direct_write",
        "direct_commit",
        "auto_apply",
        "automatic_authority",
        "ungoverned_write",
    }

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.ledger_path = self.root / "external_influence_ledger.jsonl"
        self.state_dir = self.root / "external_influence"
        self.latest_path = self.state_dir / "latest_canonical_external_influence_ledger.json"
        self.adoption_ledger_candidates = [
            self.root / "external_influence_adoption_ledger.jsonl",
            self.root / "external_influence_adoption_gate_history.jsonl",
            self.root / "external_influence_adoption" / "external_influence_adoption_ledger.jsonl",
            self.root / "external_influence_adoption" / "external_influence_adoption_gate_history.jsonl",
        ]
        self.traceability_ledger_candidates = [
            self.root / "external_influence_traceability_history.jsonl",
            self.root / "external_influence_traceability" / "external_influence_traceability_history.jsonl",
            self.root / "external_influence_traceability" / "external_influence_traceability_engine_history.jsonl",
        ]

    def _normalize(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        payload = dict(inputs or {})
        nested = payload.get("external_influence") or payload.get("influence") or payload.get("openrouter_response")
        if isinstance(nested, dict):
            merged = dict(nested)
            merged.update({k: v for k, v in payload.items() if k not in {"external_influence", "influence", "openrouter_response"}})
            payload = merged

        prompt_value = payload.get("prompt", payload.get("query", payload.get("question", "")))
        response_value = payload.get("response", payload.get("answer", payload.get("model_response", "")))

        prompt_hash = str(payload.get("prompt_hash") or (_sha256_text(prompt_value) if _present(prompt_value) else ""))
        response_hash = str(payload.get("response_hash") or (_sha256_text(response_value) if _present(response_value) else ""))

        query_id = str(
            payload.get("query_id")
            or payload.get("external_influence_id")
            or payload.get("influence_id")
            or ("AUTOEXT-" + _sha256_text({"prompt_hash": prompt_hash, "response_hash": response_hash})[:16] if prompt_hash and response_hash else "")
        )

        integration_status = str(payload.get("integration_status") or payload.get("adoption_status") or "observe_only").strip().lower()

        canonical: dict[str, Any] = {
            "query_id": query_id,
            "model": str(payload.get("model") or payload.get("model_name") or "unknown_model"),
            "provider": str(payload.get("provider") or payload.get("source") or payload.get("source_id") or "unknown_provider"),
            "prompt_hash": prompt_hash,
            "response_hash": response_hash,
            "timestamp": str(payload.get("timestamp") or payload.get("timestamp_utc") or _utc_now()),
            "recommendations": _as_list(payload.get("recommendations") or payload.get("recommendation") or payload.get("candidate_recommendations")),
            "risk_flags": _as_list(payload.get("risk_flags") or payload.get("risks") or payload.get("blocked_reasons")),
            "integration_status": integration_status,
            "linked_decision_id": payload.get("linked_decision_id") or payload.get("decision_id") or payload.get("decision_record_id"),
            "linked_action_id": payload.get("linked_action_id") or payload.get("action_id") or payload.get("execution_request_id"),
            "linked_commit": payload.get("linked_commit") or payload.get("commit_id") or payload.get("commit_hash"),
        }

        canonical["external_influence_id"] = payload.get("external_influence_id") or query_id
        canonical["source_payload_keys"] = sorted(str(k) for k in payload.keys())
        canonical["direct_write_requested"] = bool(payload.get("direct_write_requested") or payload.get("direct_commit_requested"))
        canonical["human_review_required"] = bool(payload.get("human_review_required", True))
        canonical["human_approval_confirmed"] = bool(payload.get("human_approval_confirmed", payload.get("human_approval") == "confirmed"))
        return canonical

    def _status(self, record: dict[str, Any]) -> tuple[str, list[str], bool]:
        missing = [field for field in ["query_id", "prompt_hash", "response_hash"] if not _present(record.get(field))]
        blocked: list[str] = []
        if missing:
            blocked.append("missing_trace_identity")
        if record.get("direct_write_requested"):
            blocked.append("direct_write")
        if str(record.get("integration_status", "")).lower() in self.direct_authority_statuses:
            blocked.append("direct_authority_status")
        if not _present(record.get("recommendations")):
            blocked.append("recommendations_absent")

        if "direct_write" in blocked or "direct_authority_status" in blocked:
            status = "rejected_direct_authority"
            authorized = False
        elif "missing_trace_identity" in blocked:
            status = "rejected_missing_trace"
            authorized = False
        elif blocked:
            status = "trace_recorded_incomplete"
            authorized = False
        else:
            original = str(record.get("integration_status") or "observe_only").lower()
            status = original if original not in self.direct_authority_statuses else "rejected_direct_authority"
            authorized = status not in {"rejected_direct_authority", "rejected_missing_trace"}

        return status, blocked, authorized

    def _source_summary(self) -> dict[str, Any]:
        adoption_paths = [p for p in self.adoption_ledger_candidates if p.exists()]
        trace_paths = [p for p in self.traceability_ledger_candidates if p.exists()]
        adoption_rows = sum(len(_read_jsonl(p)) for p in adoption_paths)
        trace_rows = sum(len(_read_jsonl(p)) for p in trace_paths)
        return {
            "adoption_ledger_paths": [str(p) for p in adoption_paths],
            "traceability_ledger_paths": [str(p) for p in trace_paths],
            "adoption_rows_observed": adoption_rows,
            "traceability_rows_observed": trace_rows,
            "canonical_ledger_path": str(self.ledger_path),
        }

    def _stable_record_for_hash(self, record: dict[str, Any]) -> dict[str, Any]:
        return {field: record.get(field) for field in self.stable_hash_fields}

    def _canonical_record_hash(self, record: dict[str, Any]) -> str:
        return _sha256_text(self._stable_record_for_hash(record))

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        record = self._normalize(inputs)
        status, blocked, adoption_authorized = self._status(record)
        record["integration_status"] = status
        record["blocked_reasons"] = blocked
        record["adoption_authorized"] = adoption_authorized
        record["direct_write_allowed"] = False
        record["canonical_trace_complete"] = status not in {"rejected_missing_trace", "rejected_direct_authority"} and not blocked
        record["schema_fields_present"] = all(field in record for field in self.required_fields)
        record["canonical_record_hash"] = self._canonical_record_hash(record)
        record["source_summary"] = self._source_summary()
        record["primitive"] = self.primitive
        record["success"] = True

        if persist:
            self.state_dir.mkdir(parents=True, exist_ok=True)
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
            with self.ledger_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True, default=str) + "\n")
            self.latest_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True, default=str), encoding="utf-8")
            record["ledger_path"] = str(self.ledger_path)
            record["latest_path"] = str(self.latest_path)

        return record


__all__ = ["CanonicalExternalInfluenceLedger"]
