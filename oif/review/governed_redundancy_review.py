from __future__ import annotations

import fcntl
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

SCHEMA_VERSION = "oif-0-b4-governed-review-v1"
STATUS_PREPARED = "OIF_GOVERNED_REDUNDANCY_REVIEW_PREPARED"
STATUS_APPLIED = "OIF_GOVERNED_REDUNDANCY_REVIEW_APPLIED"
REVIEW_CLASSES = {
    "DISTINCT",
    "COMPLEMENTARY",
    "VIEW",
    "ADAPTER",
    "PARTIAL_OVERLAP",
    "PROBABLE_REDUNDANCY",
}
DECISIONS = REVIEW_CLASSES | {"REQUEST_MORE_EVIDENCE", "DEFER", "ABSTAIN"}
AUTHORIZED_ROLES = {
    "human_reviewer",
    "scientific_reviewer",
    "architecture_reviewer",
    "principal_investigator",
}
CONFIRMATION_PHRASE = "APPLIQUER LES DECISIONS OIF"


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="." + path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _within(path: Path, parent: Path) -> Path:
    resolved = path.expanduser().resolve()
    try:
        resolved.relative_to(parent.expanduser().resolve())
    except ValueError as exc:
        raise ValueError(f"path escapes governed root: {resolved}") from exc
    return resolved


def _inventory_index(inventory: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    modules = inventory.get("modules")
    if not isinstance(modules, list):
        raise ValueError("active interface inventory modules must be a list")
    result: dict[str, Mapping[str, Any]] = {}
    for item in modules:
        if isinstance(item, Mapping) and item.get("module"):
            result[str(item["module"])] = item
    return result


def _source_dossier(root: Path, module_name: str, metadata: Mapping[str, Any]) -> dict[str, Any]:
    relative = str(metadata.get("path") or "")
    path = root / relative if relative else None
    present = bool(path and path.is_file())
    current_hash = _sha_file(path) if present and path else None
    inventoried_hash = str(metadata.get("source_sha256") or "") or None
    return {
        "module": module_name,
        "path": relative,
        "classification": metadata.get("classification"),
        "representative_entrypoint": bool(metadata.get("representative_entrypoint")),
        "entrypoints": list(metadata.get("entrypoints") or []),
        "functions": list(metadata.get("functions") or []),
        "classes": list(metadata.get("classes") or []),
        "imports": list(metadata.get("imports") or []),
        "gate_references": list(metadata.get("gate_references") or []),
        "persistence_calls": list(metadata.get("persistence_calls") or []),
        "source_present": present,
        "inventoried_source_sha256": inventoried_hash,
        "current_source_sha256": current_hash,
        "source_hash_consistent": bool(present and inventoried_hash and current_hash == inventoried_hash),
    }


def _immutable_entry(entry: Mapping[str, Any]) -> dict[str, Any]:
    return {key: entry.get(key) for key in (
        "position",
        "candidate_id",
        "proposed_classification",
        "confidence",
        "combined_score",
        "decision_rule",
        "recommendation",
        "automatic_change_authorized",
        "evidence",
        "contradicting_evidence",
        "left",
        "right",
        "left_dossier",
        "right_dossier",
        "candidate_payload_hash",
        "source_pair_hash",
    )}


def _entry_hash(entry: Mapping[str, Any]) -> str:
    return _sha(_immutable_entry(entry))


def _workbook_baseline(workbook: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: workbook.get(key)
        for key in (
            "schema_version",
            "campaign_id",
            "status",
            "source_fingerprint",
            "analysis_sha256",
            "inventory_sha256",
            "candidate_count",
            "automatic_changes_made",
            "entries",
            "functional_conclusion_only",
            "phenomenology_undetermined",
            "consciousness_proven",
            "subjectivity_proven",
            "qualia_proven",
            "phenomenology_proven",
        )
    }


def build_workbook(root: Path) -> dict[str, Any]:
    root = root.resolve()
    analysis_path = root / "oif_audit/oif_redundancy_qualitative_analysis.json"
    inventory_path = root / "oif_audit/oif_active_interface_inventory.json"
    if not analysis_path.is_file() or not inventory_path.is_file():
        raise FileNotFoundError("OIF calibrated analysis or active interface inventory missing")
    analysis = _read_json(analysis_path)
    inventory = _read_json(inventory_path)
    rows = analysis.get("analyses")
    if not isinstance(rows, list):
        raise ValueError("qualitative analysis analyses must be a list")
    if analysis.get("automatic_changes_made") is not False:
        raise ValueError("analysis must certify automatic_changes_made=false")
    index = _inventory_index(inventory)
    review_rows = [row for row in rows if isinstance(row, Mapping) and row.get("classification") != "DISTINCT"]
    review_rows.sort(key=lambda row: (str(row.get("classification")), str(row.get("candidate_id"))))
    entries = []
    for position, row in enumerate(review_rows, 1):
        candidate_id = str(row.get("candidate_id") or "")
        left = str(row.get("left") or "")
        right = str(row.get("right") or "")
        if not candidate_id or not left or not right or left == right:
            raise ValueError("invalid redundancy candidate identity")
        if left not in index or right not in index:
            raise ValueError(f"candidate references module absent from active inventory: {candidate_id}")
        left_dossier = _source_dossier(root, left, index[left])
        right_dossier = _source_dossier(root, right, index[right])
        candidate_core = {
            "candidate_id": candidate_id,
            "classification": row.get("classification"),
            "confidence": row.get("confidence"),
            "combined_score": row.get("combined_score"),
            "decision_rule": row.get("decision_rule"),
            "recommendation": row.get("recommendation"),
            "automatic_change_authorized": row.get("automatic_change_authorized"),
            "evidence": list(row.get("evidence") or []),
            "contradicting_evidence": list(row.get("contradicting_evidence") or []),
            "left": left,
            "right": right,
        }
        if candidate_core["automatic_change_authorized"] is not False:
            raise ValueError("automatic change authorization must remain false")
        source_pair = {
            "left": left,
            "right": right,
            "left_source_sha256": left_dossier.get("current_source_sha256") or left_dossier.get("inventoried_source_sha256"),
            "right_source_sha256": right_dossier.get("current_source_sha256") or right_dossier.get("inventoried_source_sha256"),
        }
        entry = {
            "position": position,
            "candidate_id": candidate_id,
            "proposed_classification": candidate_core["classification"],
            "confidence": candidate_core["confidence"],
            "combined_score": candidate_core["combined_score"],
            "decision_rule": candidate_core["decision_rule"],
            "recommendation": candidate_core["recommendation"],
            "automatic_change_authorized": False,
            "evidence": candidate_core["evidence"],
            "contradicting_evidence": candidate_core["contradicting_evidence"],
            "left": left,
            "right": right,
            "left_dossier": left_dossier,
            "right_dossier": right_dossier,
            "candidate_payload_hash": _sha(candidate_core),
            "source_pair_hash": _sha(source_pair),
            "human_decision": {
                "decision": "",
                "reviewer_id": "",
                "reviewer_role": "principal_investigator",
                "rationale": "",
            },
        }
        entry["entry_hash"] = _entry_hash(entry)
        entries.append(entry)
    source_fingerprint = str(analysis.get("source_fingerprint") or "")
    campaign_id = "OIF-B4-" + _sha({
        "source_fingerprint": source_fingerprint,
        "analysis_sha256": _sha_file(analysis_path),
        "inventory_sha256": _sha_file(inventory_path),
    })[:20]
    workbook = {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": campaign_id,
        "status": STATUS_PREPARED,
        "source_fingerprint": source_fingerprint,
        "analysis_sha256": _sha_file(analysis_path),
        "inventory_sha256": _sha_file(inventory_path),
        "candidate_count": len(entries),
        "automatic_changes_made": False,
        "entries": entries,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
        "consciousness_proven": False,
        "subjectivity_proven": False,
        "qualia_proven": False,
        "phenomenology_proven": False,
    }
    workbook["workbook_hash"] = _sha(_workbook_baseline(workbook))
    return workbook


def _merge_existing_decisions(new: dict[str, Any], existing: Mapping[str, Any]) -> dict[str, Any]:
    if existing.get("workbook_hash") != new.get("workbook_hash"):
        return new
    old = {str(e.get("candidate_id")): e for e in existing.get("entries", []) if isinstance(e, Mapping)}
    for entry in new["entries"]:
        previous = old.get(entry["candidate_id"])
        if previous and previous.get("entry_hash") == entry.get("entry_hash"):
            decision = previous.get("human_decision")
            if isinstance(decision, Mapping):
                entry["human_decision"] = dict(decision)
    return new


def prepare(root: Path, output_root: Path | None = None) -> Path:
    root = root.resolve()
    workbook = build_workbook(root)
    base = (output_root or (root / "oif_review/campaigns")).resolve()
    base.mkdir(parents=True, exist_ok=True)
    campaign_dir = _within(base / workbook["campaign_id"], base)
    path = campaign_dir / "governed_redundancy_review_workbook.json"
    if path.is_file():
        workbook = _merge_existing_decisions(workbook, _read_json(path))
    _atomic_json(path, workbook)
    _atomic_json(campaign_dir / "review_manifest.json", {
        "schema_version": SCHEMA_VERSION,
        "campaign_id": workbook["campaign_id"],
        "candidate_count": workbook["candidate_count"],
        "decision_count": sum(bool(e["human_decision"].get("decision")) for e in workbook["entries"]),
        "automatic_changes_made": False,
        "registry_write_performed": False,
        "workbook_hash": workbook["workbook_hash"],
    })
    return path


def validate_decision(entry: Mapping[str, Any]) -> dict[str, Any]:
    if entry.get("entry_hash") != _entry_hash(entry):
        raise ValueError("immutable entry hash mismatch")
    decision = entry.get("human_decision")
    if not isinstance(decision, Mapping):
        raise TypeError("human_decision must be a mapping")
    value = str(decision.get("decision") or "").strip().upper()
    reviewer_id = str(decision.get("reviewer_id") or "").strip()
    reviewer_role = str(decision.get("reviewer_role") or "").strip()
    rationale = str(decision.get("rationale") or "").strip()
    if value not in DECISIONS:
        raise ValueError(f"unsupported decision for {entry.get('candidate_id')}")
    if reviewer_role not in AUTHORIZED_ROLES:
        raise PermissionError("reviewer role not authorized")
    if not reviewer_id or len(rationale) < 20:
        raise ValueError("reviewer_id and rationale of at least 20 characters are required")
    if value in REVIEW_CLASSES and value == "PROBABLE_REDUNDANCY" and len(rationale) < 60:
        raise ValueError("PROBABLE_REDUNDANCY requires a rationale of at least 60 characters")
    core = {
        "candidate_id": entry["candidate_id"],
        "decision": value,
        "reviewer_id": reviewer_id,
        "reviewer_role": reviewer_role,
        "rationale": rationale,
        "entry_hash": entry["entry_hash"],
        "candidate_payload_hash": entry["candidate_payload_hash"],
        "source_pair_hash": entry["source_pair_hash"],
    }
    core["decision_id"] = "OIF-DEC-" + _sha(core)[:24]
    return core


def _verify_current_sources(root: Path, entry: Mapping[str, Any]) -> None:
    for side in ("left_dossier", "right_dossier"):
        dossier = entry.get(side)
        if not isinstance(dossier, Mapping):
            raise ValueError("source dossier missing")
        relative = str(dossier.get("path") or "")
        expected = dossier.get("current_source_sha256") or dossier.get("inventoried_source_sha256")
        if not relative or not expected:
            raise RuntimeError("source path or baseline hash unavailable")
        path = _within(root / relative, root)
        if not path.is_file() or _sha_file(path) != expected:
            raise RuntimeError(f"source drift detected: {relative}")


def _validate_ledger(records: list[Mapping[str, Any]]) -> str:
    previous = "GENESIS"
    seen = set()
    for record in records:
        decision_id = str(record.get("decision_id") or "")
        if not decision_id or decision_id in seen:
            raise ValueError("duplicate or missing decision_id in ledger")
        seen.add(decision_id)
        if record.get("previous_record_hash") != previous:
            raise ValueError("ledger hash chain broken")
        core = {k: v for k, v in record.items() if k != "record_hash"}
        expected = _sha(core)
        if record.get("record_hash") != expected:
            raise ValueError("ledger record hash mismatch")
        previous = expected
    return previous


def apply(workbook_path: Path, root: Path, confirmation: str) -> dict[str, Any]:
    if confirmation != CONFIRMATION_PHRASE:
        raise PermissionError("confirmation phrase mismatch")
    root = root.resolve()
    workbook_path = workbook_path.expanduser().resolve()
    workbook = _read_json(workbook_path)
    entries = workbook.get("entries")
    if not isinstance(entries, list):
        raise ValueError("workbook entries must be a list")
    for entry in entries:
        _verify_current_sources(root, entry)
    rebuilt = build_workbook(root)
    if workbook.get("workbook_hash") != rebuilt.get("workbook_hash"):
        raise RuntimeError("workbook baseline is obsolete or tampered")
    expected = {e["candidate_id"]: e for e in rebuilt["entries"]}
    if len(entries) != len(expected):
        raise ValueError("workbook candidate set mismatch")
    decisions = []
    for entry in entries:
        candidate_id = str(entry.get("candidate_id") or "")
        baseline = expected.get(candidate_id)
        if not baseline:
            raise ValueError("unknown candidate in workbook")
        if _immutable_entry(entry) != _immutable_entry(baseline) or entry.get("entry_hash") != baseline.get("entry_hash"):
            raise RuntimeError(f"immutable candidate data changed: {candidate_id}")
        decisions.append(validate_decision(entry))
    ledger = root / "oif_review/governed_redundancy_decisions.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    lock_path = ledger.with_suffix(ledger.suffix + ".lock")
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        existing = []
        if ledger.is_file():
            for line in ledger.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    existing.append(json.loads(line))
        previous = _validate_ledger(existing)
        existing_ids = {record["decision_id"] for record in existing}
        appended = 0
        for decision in decisions:
            if decision["decision_id"] in existing_ids:
                continue
            record = {
                **decision,
                "campaign_id": workbook["campaign_id"],
                "previous_record_hash": previous,
                "automatic_change_authorized": False,
                "code_change_performed": False,
                "functional_conclusion_only": True,
                "phenomenology_undetermined": True,
            }
            record["record_hash"] = _sha(record)
            existing.append(record)
            existing_ids.add(decision["decision_id"])
            previous = record["record_hash"]
            appended += 1
        _validate_ledger(existing)
        text = "".join(_canonical(record) + "\n" for record in existing)
        fd, tmp = tempfile.mkstemp(prefix="." + ledger.name + ".", dir=str(ledger.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp, ledger)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    result = {
        "schema_version": SCHEMA_VERSION,
        "status": STATUS_APPLIED,
        "campaign_id": workbook["campaign_id"],
        "decision_count": len(decisions),
        "appended_count": appended,
        "replayed_count": len(decisions) - appended,
        "classification_counts": {
            name: sum(decision["decision"] == name for decision in decisions)
            for name in sorted(DECISIONS)
        },
        "automatic_changes_made": False,
        "code_change_performed": False,
        "registry_write_performed": True,
        "ledger_path": str(ledger),
        "ledger_tail_hash": previous,
        "functional_conclusion_only": True,
        "phenomenology_undetermined": True,
    }
    result["result_hash"] = _sha(result)
    _atomic_json(workbook_path.parent / "governed_redundancy_review_result.json", result)
    return result


@dataclass
class GovernedRedundancyReview:
    root: Path

    def prepare(self, output_root: Path | None = None) -> Path:
        return prepare(self.root, output_root)

    def apply(self, workbook_path: Path, confirmation: str) -> dict[str, Any]:
        return apply(workbook_path, self.root, confirmation)
