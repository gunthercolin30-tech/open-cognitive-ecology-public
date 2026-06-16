from __future__ import annotations

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path.home() / "open-cognitive-ecology"
DEFAULT_SSD_ROOT = Path(os.environ.get("OCE_SSD_ROOT", "/Volumes/OCE_SSD"))


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class CivilizationalBackupCleanupCertifier:
    """
    F17.6 — Civilizational Backup Cleanup Certifier.

    Certifies and optionally deletes local .pre_f17_4_local_backup_* folders
    after F17.4/F17.5 have proven that producer directories are symlink-routed
    to the SSD. It never touches symlinks or SSD targets.

    Functional storage cleanup certification only; no phenomenal subjectivity claim.
    """

    primitive = "civilizational_backup_cleanup_certifier"
    refinement = "F17.6-R1"

    def __init__(self, root: Optional[Path] = None, ssd_root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.ssd_root = Path(ssd_root) if ssd_root is not None else DEFAULT_SSD_ROOT

    def _ssd_available(self) -> bool:
        return self.ssd_root.exists() and self.ssd_root.is_dir()

    def _count_and_size(self, path: Path) -> Dict[str, int]:
        if not path.exists():
            return {"file_count": 0, "size_bytes": 0}
        if path.is_file():
            return {"file_count": 1, "size_bytes": path.stat().st_size}
        count = 0
        size = 0
        for f in path.rglob("*"):
            if f.is_file():
                count += 1
                try:
                    size += f.stat().st_size
                except Exception:
                    pass
        return {"file_count": count, "size_bytes": size}

    def _backup_items(self) -> List[Path]:
        return sorted(self.root.glob("*.pre_f17_4_local_backup_*"), key=lambda p: p.name)

    def _report_base(self) -> Path:
        if self._ssd_available():
            return self.ssd_root / "OCE_ARCHIVE" / "storage_migration" / "f17_6_backup_cleanup"
        return self.root / "local_storage_fallback" / "archive" / "f17_6_backup_cleanup"

    def _certify_one(self, backup: Path) -> Dict[str, Any]:
        original_name = backup.name.split(".pre_f17_4_local_backup_", 1)[0]
        link = self.root / original_name

        link_exists = link.exists()
        link_is_symlink = link.is_symlink()
        resolved = link.resolve() if link_exists else None
        target_under_ssd = False
        if resolved is not None:
            try:
                resolved.relative_to(self.ssd_root)
                target_under_ssd = True
            except Exception:
                target_under_ssd = str(resolved).startswith(str(self.ssd_root))

        backup_stats = self._count_and_size(backup)
        target_stats = self._count_and_size(resolved) if resolved and resolved.exists() else {"file_count": 0, "size_bytes": 0}

        certified = (
            backup.exists()
            and link_exists
            and link_is_symlink
            and target_under_ssd
            and target_stats["file_count"] >= backup_stats["file_count"]
            and target_stats["size_bytes"] >= backup_stats["size_bytes"]
        )

        return {
            "backup_path": str(backup),
            "backup_name": backup.name,
            "original_name": original_name,
            "current_link": str(link),
            "current_link_exists": link_exists,
            "current_link_is_symlink": link_is_symlink,
            "current_link_resolved": str(resolved) if resolved else None,
            "target_under_ssd": target_under_ssd,
            "backup": backup_stats,
            "current_target": target_stats,
            "cleanup_certified": certified,
            "reason": (
                "ssd_target_contains_at_least_backup_file_count_and_bytes"
                if certified
                else "manual_review_required_before_cleanup"
            ),
        }

    def step(self, inputs: Optional[dict] = None) -> Dict[str, Any]:
        inputs = inputs or {}
        dry_run = bool(inputs.get("dry_run", True))
        delete_verified_backups = bool(inputs.get("delete_verified_backups", False))

        backups = self._backup_items()
        records = [self._certify_one(b) for b in backups]

        certified = [r for r in records if r["cleanup_certified"] is True]
        uncertified = [r for r in records if r["cleanup_certified"] is not True]

        deleted = []
        deletion_errors = []

        if not dry_run and delete_verified_backups:
            for r in certified:
                p = Path(r["backup_path"])
                try:
                    if p.exists():
                        if p.is_dir():
                            shutil.rmtree(p)
                        else:
                            p.unlink()
                    deleted.append(r["backup_name"])
                except Exception as exc:
                    deletion_errors.append({
                        "backup_name": r["backup_name"],
                        "backup_path": r["backup_path"],
                        "error": repr(exc),
                    })

        remaining_after = [p.name for p in self._backup_items()]

        total_backup_files = sum(int(r["backup"]["file_count"]) for r in records)
        total_backup_bytes = sum(int(r["backup"]["size_bytes"]) for r in records)

        classification = "Civilizational Backup Cleanup Certified"
        if uncertified:
            classification = "Civilizational Backup Cleanup Requires Review"
        if deleted and not deletion_errors:
            classification = "Civilizational Backup Cleanup Applied"
        if deletion_errors:
            classification = "Civilizational Backup Cleanup Partial"

        payload = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": _utc(),
            "classification": classification,
            "dry_run": dry_run,
            "delete_verified_backups": delete_verified_backups,
            "ssd_available": self._ssd_available(),
            "backup_count": len(records),
            "certified_count": len(certified),
            "uncertified_count": len(uncertified),
            "deleted_count": len(deleted),
            "deletion_error_count": len(deletion_errors),
            "remaining_backup_count_after": len(remaining_after),
            "remaining_backups_after": remaining_after,
            "total_backup_files": total_backup_files,
            "total_backup_bytes": total_backup_bytes,
            "records": records,
            "deleted": deleted,
            "deletion_errors": deletion_errors,
            "symlink_deletion_performed": False,
            "ssd_target_deletion_performed": False,
            "epistemic_boundary": "functional_storage_cleanup_certification_only_no_phenomenal_subjectivity_claim",
        }

        base = self._report_base()
        base.mkdir(parents=True, exist_ok=True)
        state_path = base / "f17_6_civilizational_backup_cleanup_state.json"
        history_path = base / "f17_6_civilizational_backup_cleanup_history.jsonl"

        state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")

        return {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": payload["timestamp_utc"],
            "classification": classification,
            "dry_run": dry_run,
            "delete_verified_backups": delete_verified_backups,
            "ssd_available": self._ssd_available(),
            "backup_count": len(records),
            "certified_count": len(certified),
            "uncertified_count": len(uncertified),
            "deleted_count": len(deleted),
            "deletion_error_count": len(deletion_errors),
            "remaining_backup_count_after": len(remaining_after),
            "total_backup_files": total_backup_files,
            "total_backup_bytes": total_backup_bytes,
            "state_path": str(state_path),
            "history_path": str(history_path),
            "symlink_deletion_performed": False,
            "ssd_target_deletion_performed": False,
            "non_closure_compliant": True,
            "next_step": "F17 storage stabilization closure or G interaction physique et multimodale",
        }
