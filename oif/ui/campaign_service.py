from __future__ import annotations

import json
import os
import tempfile
import threading
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

from oif.review.governed_redundancy_review import (
    AUTHORIZED_ROLES,
    CONFIRMATION_PHRASE,
    DECISIONS,
    apply,
    validate_decision,
)

WORKBOOK_NAME = "governed_redundancy_review_workbook.json"


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("workbook root must be a JSON object")
    return value


def _atomic_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class OIFReviewCampaignService:
    """Governed application service between NiceGUI and OIF B4.1.

    The service never edits ontology source files. It only updates the
    human_decision fields of an existing governed workbook. Registry
    application remains a separate, explicitly confirmed operation.
    """

    def __init__(self, root: Path, workbook_path: Path | None = None) -> None:
        self.root = root.expanduser().resolve()
        self.campaign_root = (self.root / "oif_review/campaigns").resolve()
        self._lock = threading.RLock()
        self.workbook_path = self._validate_workbook_path(
            workbook_path or self.latest_workbook()
        )

    def latest_workbook(self) -> Path:
        matches = sorted(
            self.campaign_root.glob(f"OIF-B4-*/{WORKBOOK_NAME}"),
            key=lambda path: (path.stat().st_mtime_ns, str(path)),
        )
        if not matches:
            raise FileNotFoundError("no governed OIF B4 workbook found")
        return matches[-1].resolve()

    def _validate_workbook_path(self, path: Path) -> Path:
        resolved = path.expanduser().resolve()
        try:
            resolved.relative_to(self.campaign_root)
        except ValueError as exc:
            raise ValueError("workbook escapes OIF governed campaign root") from exc
        if resolved.name != WORKBOOK_NAME or not resolved.is_file():
            raise FileNotFoundError(str(resolved))
        return resolved

    def load(self) -> dict[str, Any]:
        with self._lock:
            workbook = _read_json(self.workbook_path)
        self._validate_structure(workbook)
        return workbook

    @staticmethod
    def _validate_structure(workbook: Mapping[str, Any]) -> None:
        entries = workbook.get("entries")
        if not isinstance(entries, list):
            raise TypeError("workbook entries must be a list")
        if workbook.get("candidate_count") != len(entries):
            raise ValueError("candidate_count does not match entries")
        if workbook.get("automatic_changes_made") is not False:
            raise ValueError("automatic_changes_made must remain false")
        seen: set[str] = set()
        for entry in entries:
            if not isinstance(entry, Mapping):
                raise TypeError("workbook entry must be a mapping")
            candidate_id = str(entry.get("candidate_id") or "")
            if not candidate_id or candidate_id in seen:
                raise ValueError("duplicate or missing candidate_id")
            seen.add(candidate_id)
            if entry.get("automatic_change_authorized") is not False:
                raise ValueError("automatic change authorization must remain false")
            decision = entry.get("human_decision")
            if not isinstance(decision, Mapping):
                raise TypeError("human_decision must be a mapping")

    def summary(self, workbook: Mapping[str, Any] | None = None) -> dict[str, Any]:
        current = workbook or self.load()
        entries = current["entries"]
        decided = sum(
            bool(str(entry["human_decision"].get("decision") or "").strip())
            for entry in entries
        )
        classifications: dict[str, int] = {}
        for entry in entries:
            key = str(entry.get("proposed_classification") or "UNKNOWN")
            classifications[key] = classifications.get(key, 0) + 1
        return {
            "campaign_id": current.get("campaign_id"),
            "candidate_count": len(entries),
            "decided_count": decided,
            "remaining_count": len(entries) - decided,
            "completion_ratio": (decided / len(entries)) if entries else 1.0,
            "classifications": dict(sorted(classifications.items())),
            "registry_write_performed": False,
            "automatic_changes_made": False,
        }

    @staticmethod
    def filtered_entries(
        workbook: Mapping[str, Any],
        query: str = "",
        proposed_classification: str = "ALL",
        decision_state: str = "ALL",
    ) -> list[dict[str, Any]]:
        needle = query.strip().lower()
        result: list[dict[str, Any]] = []
        for raw in workbook["entries"]:
            entry = dict(raw)
            decision = str(entry["human_decision"].get("decision") or "").strip()
            if proposed_classification != "ALL" and entry.get("proposed_classification") != proposed_classification:
                continue
            if decision_state == "DECIDED" and not decision:
                continue
            if decision_state == "PENDING" and decision:
                continue
            searchable = " ".join(
                str(entry.get(key) or "")
                for key in (
                    "candidate_id", "left", "right", "proposed_classification",
                    "recommendation", "decision_rule",
                )
            ).lower()
            if needle and needle not in searchable:
                continue
            result.append(entry)
        return result

    def save_decision(
        self,
        candidate_id: str,
        decision: str,
        reviewer_id: str,
        reviewer_role: str,
        rationale: str,
    ) -> dict[str, Any]:
        normalized_decision = decision.strip().upper()
        if normalized_decision and normalized_decision not in DECISIONS:
            raise ValueError("unsupported decision")
        if reviewer_role not in AUTHORIZED_ROLES:
            raise PermissionError("reviewer role not authorized")
        with self._lock:
            workbook = self.load()
            target = next(
                (entry for entry in workbook["entries"] if entry.get("candidate_id") == candidate_id),
                None,
            )
            if target is None:
                raise KeyError(f"unknown candidate_id: {candidate_id}")
            target["human_decision"] = {
                "decision": normalized_decision,
                "reviewer_id": reviewer_id.strip(),
                "reviewer_role": reviewer_role.strip(),
                "rationale": rationale.strip(),
            }
            if normalized_decision:
                validate_decision(target)
            _atomic_json(self.workbook_path, workbook)
        return {
            "candidate_id": candidate_id,
            "saved": True,
            "decision": normalized_decision,
            "registry_write_performed": False,
            "code_change_performed": False,
            "summary": self.summary(workbook),
        }

    def apply_governed(self, confirmation: str) -> dict[str, Any]:
        if confirmation != CONFIRMATION_PHRASE:
            raise PermissionError("confirmation phrase mismatch")
        with self._lock:
            workbook = self.load()
            for entry in workbook["entries"]:
                validate_decision(entry)
            return apply(self.workbook_path, self.root, confirmation)

    def decision_options(self) -> list[str]:
        return sorted(DECISIONS)

    def role_options(self) -> list[str]:
        return sorted(AUTHORIZED_ROLES)

    def immutable_snapshot(self) -> dict[str, Any]:
        workbook = self.load()
        return {
            "campaign_id": workbook.get("campaign_id"),
            "workbook_hash": workbook.get("workbook_hash"),
            "candidate_count": workbook.get("candidate_count"),
            "source_fingerprint": workbook.get("source_fingerprint"),
            "automatic_changes_made": workbook.get("automatic_changes_made"),
            "entries": [
                {
                    "candidate_id": entry.get("candidate_id"),
                    "entry_hash": entry.get("entry_hash"),
                    "candidate_payload_hash": entry.get("candidate_payload_hash"),
                    "source_pair_hash": entry.get("source_pair_hash"),
                }
                for entry in workbook["entries"]
            ],
        }
