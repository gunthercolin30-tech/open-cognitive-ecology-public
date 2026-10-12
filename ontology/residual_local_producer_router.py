from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path.home() / "open-cognitive-ecology"
DEFAULT_SSD_ROOT = Path(os.environ.get("OCE_SSD_ROOT", "/Volumes/OCE_SSD"))


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class ResidualLocalProducerRouter:
    """
    F17.4 — Residual Local Producer Router.

    Routes known residual producer directories to the SSD through stable
    symlink-based redirection. It does not delete data. Existing local
    directories are moved to backup folders before symlink creation.

    Functional storage routing only; no phenomenal subjectivity claim.
    """

    primitive = "residual_local_producer_router"
    refinement = "F17.4-R1"

    PRODUCER_ROUTES = {
        "terminal_conversation_runtime": ("OCE_ARCHIVE", "terminal_conversation_runtime"),
        "distributed_identity_state": ("OCE_CIVILIZATIONAL_CONTINUITY", "distributed_identity_state"),
        "distributed_attention_state": ("OCE_CIVILIZATIONAL_CONTINUITY", "distributed_attention_state"),
        "external_collaboration_execution": ("OCE_ARCHIVE", "external_collaboration_execution"),
        "runtime_experiments": ("OCE_EXPERIMENTS", "runtime_experiments"),
        "metrics": ("OCE_METRICS", "legacy_metrics"),
        "grafana": ("OCE_DASHBOARDS", "legacy_grafana"),
        "civilizational_mutation": ("OCE_EXPERIMENTS", "civilizational_mutation"),
        "distributed_nodes": ("OCE_CIVILIZATIONAL_CONTINUITY", "distributed_nodes"),
        "community_nodes": ("OCE_CIVILIZATIONAL_CONTINUITY", "community_nodes"),
        "external_collaboration": ("OCE_ARCHIVE", "external_collaboration"),
        "external_memory": ("OCE_MEMORY", "legacy_external_memory"),
        "collaboration_history_repository_archive": ("OCE_ARCHIVE", "collaboration_history_repository_archive"),
        "secrets": ("OCE_ARCHIVE", "credential_audit_and_secrets_metadata"),
    }

    # local_storage_fallback is intentionally excluded from symlink routing:
    # it must remain available for SSD-absent degradation tests.

    def __init__(self, root: Optional[Path] = None, ssd_root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.ssd_root = Path(ssd_root) if ssd_root is not None else DEFAULT_SSD_ROOT

    def _ssd_available(self) -> bool:
        return self.ssd_root.exists() and self.ssd_root.is_dir()

    def _route_target(self, producer_dir: str) -> Path:
        ssd_category, target_name = self.PRODUCER_ROUTES[producer_dir]
        return self.ssd_root / ssd_category / "routed_producers" / target_name

    def _count_files(self, path: Path) -> int:
        if not path.exists():
            return 0
        if path.is_file():
            return 1
        try:
            return sum(1 for p in path.rglob("*") if p.is_file())
        except Exception:
            return 0

    def _size_bytes(self, path: Path) -> int:
        if not path.exists():
            return 0
        if path.is_file():
            try:
                return path.stat().st_size
            except Exception:
                return 0
        total = 0
        try:
            for p in path.rglob("*"):
                if p.is_file():
                    try:
                        total += p.stat().st_size
                    except Exception:
                        pass
        except Exception:
            pass
        return total

    def _merge_copy(self, source: Path, target: Path, *, target_fs_context=None) -> int:
        if not source.exists():
            return 0
        if target_fs_context is None:
            raise PermissionError("producer copy requires preissued target filesystem effect context")
        copied = self._count_files(source)
        target_fs_context.execute_dual_path(
            "producer_merge_copy",
            "FS_COPY_TREE_MERGE",
            str(target_fs_context.source_root_id),
            target_fs_context.source_root_path,
            source,
            target,
        )
        return copied

    def _backup_path(self, source: Path) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return source.with_name(source.name + f".pre_f17_4_local_backup_{stamp}")

    def _route_one(
        self,
        producer_dir: str,
        dry_run: bool = True,
        force: bool = False,
        *,
        target_fs_context=None,
        local_fs_context=None,
        backup_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        source = self.root / producer_dir
        target = self._route_target(producer_dir)

        record: Dict[str, Any] = {
            "producer_dir": producer_dir,
            "source": str(source),
            "target": str(target),
            "source_exists": source.exists(),
            "source_is_symlink": source.is_symlink(),
            "target_exists": target.exists(),
            "source_file_count": self._count_files(source) if source.exists() and not source.is_symlink() else 0,
            "source_size_bytes": self._size_bytes(source) if source.exists() and not source.is_symlink() else 0,
            "dry_run": dry_run,
            "force": force,
            "status": "planned",
            "timestamp_utc": _utc(),
        }

        if not self._ssd_available():
            record["status"] = "skipped_ssd_unavailable"
            return record

        if source.is_symlink():
            try:
                current = source.resolve()
            except Exception:
                current = Path(os.readlink(source))
            record["resolved_symlink"] = str(current)
            if str(current) == str(target):
                record["status"] = "already_routed"
            else:
                record["status"] = "symlink_points_elsewhere_manual_review"
            return record

        if dry_run:
            return record

        if target_fs_context is None or local_fs_context is None:
            raise PermissionError("producer routing requires preissued target and local filesystem effect contexts")
        if not target_fs_context.source_root_id or target_fs_context.source_root_path is None:
            raise RuntimeError("target filesystem effect context requires local source-root binding")
        if source.exists():
            if backup_path is None:
                raise PermissionError("existing producer routing requires caller-preauthorized backup_path")
            backup = Path(backup_path)
            expected_prefix = source.name + ".pre_f17_4_local_backup_"
            if backup.parent != source.parent or not backup.name.startswith(expected_prefix):
                raise ValueError("backup_path violates residual producer backup naming contract")
            if backup.exists() or backup.is_symlink():
                raise FileExistsError("preauthorized backup_path already exists")
        else:
            backup = None

        target_fs_context.execute_path("producer_target_create", "FS_CREATE_DIRS", target)

        copied_count = 0
        if source.exists():
            copied_count = self._merge_copy(source, target, target_fs_context=target_fs_context)
            local_fs_context.execute_dual_path(
                "producer_backup_move",
                "FS_MOVE_PATH",
                str(local_fs_context.root_id),
                local_fs_context.root_path,
                source,
                backup,
            )

        local_fs_context.execute_dual_path(
            "producer_symlink_create",
            "FS_CREATE_SYMLINK",
            str(target_fs_context.root_id),
            target_fs_context.root_path,
            target,
            source,
        )

        record.update({
            "status": "routed",
            "copied_count": copied_count,
            "backup_path": str(backup) if backup else None,
            "target_file_count_after": self._count_files(target),
            "target_size_bytes_after": self._size_bytes(target),
            "source_is_symlink_after": source.is_symlink(),
            "source_resolves_to": str(source.resolve()) if source.exists() else None,
        })

        return record

    def _report_paths(self) -> Dict[str, Path]:
        if self._ssd_available():
            base = self.ssd_root / "OCE_ARCHIVE" / "storage_migration" / "f17_4_residual_producer_router"
        else:
            base = self.root / "local_storage_fallback" / "archive" / "f17_4_residual_producer_router"
        return {
            "base": base,
            "state": base / "f17_4_residual_local_producer_routing_state.json",
            "history": base / "f17_4_residual_local_producer_routing_history.jsonl",
        }

    def step(self, inputs: Optional[dict] = None, *, target_fs_context=None, local_fs_context=None, report_fs_context=None) -> Dict[str, Any]:
        inputs = inputs or {}
        if report_fs_context is None:
            raise PermissionError("producer routing report persistence requires preissued filesystem effect context")
        report_fs_context.begin()
        dry_run = bool(inputs.get("dry_run", True))
        force = bool(inputs.get("force", False))
        selected = inputs.get("producer_dirs")
        backup_paths = inputs.get("backup_paths") or {}

        if selected is None:
            producer_dirs = list(self.PRODUCER_ROUTES.keys())
        else:
            producer_dirs = [str(x) for x in selected if str(x) in self.PRODUCER_ROUTES]

        records = [
            self._route_one(
                p,
                dry_run=dry_run,
                force=force,
                target_fs_context=target_fs_context,
                local_fs_context=local_fs_context,
                backup_path=Path(backup_paths[p]) if p in backup_paths else None,
            )
            for p in producer_dirs
        ]

        summary: Dict[str, int] = {}
        for r in records:
            summary[r["status"]] = summary.get(r["status"], 0) + 1

        paths = self._report_paths()

        payload = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": _utc(),
            "dry_run": dry_run,
            "ssd_available": self._ssd_available(),
            "producer_count": len(records),
            "summary": summary,
            "records": records,
            "deletion_performed": False,
            "local_backups_created": not dry_run,
            "epistemic_boundary": "functional_storage_routing_only_no_phenomenal_subjectivity_claim",
        }

        report_fs_context.execute_path("producer_report_dir_create", "FS_CREATE_DIRS", paths["base"])
        report_fs_context.execute_path("producer_report_state_replace", "FS_WRITE_REPLACE_BYTES", paths["state"], json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8"))
        report_fs_context.execute_path("producer_report_history_append", "FS_APPEND_BYTES", paths["history"], (json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))

        return {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": payload["timestamp_utc"],
            "classification": "Residual Local Producer Routing Planned" if dry_run else "Residual Local Producer Routing Applied",
            "dry_run": dry_run,
            "ssd_available": self._ssd_available(),
            "producer_count": len(records),
            "summary": summary,
            "state_path": str(paths["state"]),
            "history_path": str(paths["history"]),
            "deletion_performed": False,
            "local_backups_created": not dry_run,
            "non_closure_compliant": True,
            "next_step": "F17.5 verify no local producer reappearance, then residual MOVE_TO_SSD treatment",
        }
