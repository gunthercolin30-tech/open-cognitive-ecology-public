from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


ROOT = Path.home() / "open-cognitive-ecology"
DEFAULT_SSD_ROOT = Path(os.environ.get("OCE_SSD_ROOT", "/Volumes/OCE_SSD"))


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk_size)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


@dataclass(frozen=True)
class StorageRoute:
    destination_root: str
    reason: str


class CivilizationalStorageMigration:
    """
    F17.1 — Civilizational Storage Migration.

    Migrates existing local runtime artifacts from ~/open-cognitive-ecology
    to /Volumes/OCE_SSD with manifest, checksums and explicit deletion guard.

    Functional-only validation: this module does not claim phenomenal
    subjectivity. It improves storage independence, traceability and
    portability of the civilizational runtime.
    """

    primitive = "civilizational_storage_migration"
    refinement = "F17.1"

    EXCLUDED_TOP_LEVEL = {
        ".git",
        ".venv",
        "__pycache__",
        "ontology",
        "validation",
        "docs",
        "archive",
    }

    EXCLUDED_SUFFIXES = {
        ".py",
        ".pyc",
        ".bak",
        ".zip",
        ".DS_Store",
    }

    CANDIDATE_SUFFIXES = {
        ".jsonl",
        ".json",
        ".html",
        ".prom",
        ".db",
        ".sqlite",
        ".csv",
        ".txt",
        ".md",
    }

    EXCLUDED_NAMES = {
        "ontology_inventory.txt",
        "ontology_integration_report.txt",
        "dependency_registry.py",
        "README.md",
    }

    def __init__(self, root: Path = ROOT, ssd_root: Path = DEFAULT_SSD_ROOT):
        self.root = Path(root)
        self.ssd_root = Path(ssd_root)

    def _ssd_available(self) -> bool:
        return self.ssd_root.exists() and self.ssd_root.is_dir()

    def _route(self, rel: Path) -> StorageRoute:
        name = rel.name.lower()
        rel_s = str(rel).lower()

        if name.endswith(".prom"):
            return StorageRoute("OCE_METRICS/prometheus", "prometheus_export")

        if "metric" in rel_s or rel.parts[:1] == ("metrics",):
            return StorageRoute("OCE_METRICS/local_migrated", "metrics_history")

        if "dashboard" in rel_s or name.endswith(".html"):
            return StorageRoute("OCE_DASHBOARDS/local_migrated", "dashboard_or_html")

        if (
            "memory" in rel_s
            or "knowledge" in rel_s
            or "semantic" in rel_s
            or name.endswith(".db")
            or name.endswith(".sqlite")
        ):
            return StorageRoute("OCE_MEMORY/local_migrated", "memory_or_knowledge")

        if (
            "experiment" in rel_s
            or "runtime_experiment" in rel_s
            or "stability" in rel_s
        ):
            return StorageRoute("OCE_EXPERIMENTS/local_migrated", "experiment_or_stability")

        if (
            "continuity" in rel_s
            or "recovery" in rel_s
            or "replication" in rel_s
            or "migration" in rel_s
            or "distributed" in rel_s
            or "node" in rel_s
        ):
            return StorageRoute("OCE_CIVILIZATIONAL_CONTINUITY/local_migrated", "distributed_continuity")

        if (
            "archive" in rel_s
            or "history" in rel_s
            or "queue" in rel_s
            or "collaboration" in rel_s
            or "governance" in rel_s
            or "identity" in rel_s
            or "external" in rel_s
        ):
            return StorageRoute("OCE_ARCHIVE/local_migrated", "archive_history_or_external")

        return StorageRoute("OCE_ARCHIVE/local_migrated/misc", "misc_runtime_artifact")

    def _is_candidate(self, path: Path) -> bool:
        if not path.is_file():
            return False

        try:
            rel = path.relative_to(self.root)
        except Exception:
            return False

        if not rel.parts:
            return False

        if rel.parts[0] in self.EXCLUDED_TOP_LEVEL:
            return False

        if path.name in self.EXCLUDED_NAMES:
            return False

        if path.suffix in self.EXCLUDED_SUFFIXES:
            return False

        rel_s = str(rel).lower()

        if rel.name.startswith("refine_"):
            return False

        if rel.name.startswith("F17_") and rel.suffix in {".json", ".txt", ".zip"}:
            return False

        if path.suffix not in self.CANDIDATE_SUFFIXES:
            return False

        signals = [
            "history",
            "metric",
            "archive",
            "queue",
            "memory",
            "state",
            "dashboard",
            "collaboration",
            "governance",
            "identity",
            "external",
            "continuity",
            "recovery",
            "replication",
            "migration",
            "distributed",
            "experiment",
            "semantic",
            "knowledge",
            "prometheus",
            "grafana",
        ]

        return any(s in rel_s for s in signals) or path.suffix in {".db", ".sqlite", ".prom"}

    def discover_candidates(self) -> List[Path]:
        return sorted(
            (p for p in self.root.rglob("*") if self._is_candidate(p)),
            key=lambda p: str(p.relative_to(self.root)),
        )

    def _manifest_paths(self) -> Dict[str, Path]:
        base = self.ssd_root / "OCE_ARCHIVE" / "storage_migration"
        return {
            "base": base,
            "manifest": base / "civilizational_storage_migration_manifest.jsonl",
            "state": base / "civilizational_storage_migration_state.json",
        }

    def step(self, inputs: Optional[dict] = None) -> dict:
        inputs = inputs or {}

        dry_run = bool(inputs.get("dry_run", True))
        delete_local_after_verified_copy = bool(
            inputs.get("delete_local_after_verified_copy", False)
        )
        max_files = inputs.get("max_files")
        if max_files is not None:
            max_files = int(max_files)

        candidates = self.discover_candidates()
        if max_files is not None:
            candidates = candidates[:max_files]

        ssd_available = self._ssd_available()

        migrated = []
        skipped = []
        errors = []
        total_bytes = 0
        copied_bytes = 0
        deleted_local_count = 0

        for src in candidates:
            rel = src.relative_to(self.root)
            route = self._route(rel)
            dest = self.ssd_root / route.destination_root / rel

            try:
                size = src.stat().st_size
                total_bytes += size
                record = {
                    "timestamp_utc": _utc_now(),
                    "source": str(src),
                    "relative_path": str(rel),
                    "destination": str(dest),
                    "route": route.destination_root,
                    "reason": route.reason,
                    "size_bytes": size,
                    "dry_run": dry_run,
                    "ssd_available": ssd_available,
                    "delete_local_after_verified_copy": delete_local_after_verified_copy,
                }

                if not ssd_available:
                    record["status"] = "skipped_ssd_unavailable"
                    skipped.append(record)
                    continue

                if dry_run:
                    record["status"] = "planned"
                    migrated.append(record)
                    continue

                dest.parent.mkdir(parents=True, exist_ok=True)
                src_hash = _sha256(src)
                shutil.copy2(src, dest)
                dest_hash = _sha256(dest)
                record["source_sha256"] = src_hash
                record["destination_sha256"] = dest_hash
                record["checksum_verified"] = src_hash == dest_hash

                if not record["checksum_verified"]:
                    record["status"] = "copy_failed_checksum_mismatch"
                    errors.append(record)
                    continue

                copied_bytes += size

                if delete_local_after_verified_copy:
                    src.unlink()
                    deleted_local_count += 1
                    record["local_deleted"] = True
                    record["status"] = "migrated_and_local_deleted"
                else:
                    record["local_deleted"] = False
                    record["status"] = "copied_verified_local_retained"

                migrated.append(record)

            except Exception as exc:
                errors.append({
                    "timestamp_utc": _utc_now(),
                    "source": str(src),
                    "relative_path": str(rel),
                    "destination": str(dest),
                    "route": route.destination_root,
                    "reason": route.reason,
                    "error": repr(exc),
                    "status": "error",
                })

        manifest_info = self._manifest_paths()
        manifest_path = manifest_info["manifest"]
        state_path = manifest_info["state"]

        history_recorded = False
        state_recorded = False

        if ssd_available and not dry_run:
            manifest_info["base"].mkdir(parents=True, exist_ok=True)

            with manifest_path.open("a", encoding="utf-8") as f:
                for rec in migrated + skipped + errors:
                    f.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")
            history_recorded = True

            state = {
                "primitive": self.primitive,
                "refinement": self.refinement,
                "timestamp_utc": _utc_now(),
                "dry_run": dry_run,
                "candidate_count": len(candidates),
                "migrated_or_planned_count": len(migrated),
                "skipped_count": len(skipped),
                "error_count": len(errors),
                "total_candidate_bytes": total_bytes,
                "copied_bytes": copied_bytes,
                "deleted_local_count": deleted_local_count,
                "ssd_root": str(self.ssd_root),
                "manifest_path": str(manifest_path),
                "epistemic_boundary": "functional_storage_migration_only_no_phenomenal_subjectivity_claim",
            }
            state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
            state_recorded = True

        classification = "Civilizational Storage Migration Planned"
        if not ssd_available:
            classification = "Civilizational Storage Migration Degraded SSD Unavailable"
        elif not dry_run and not errors:
            classification = "Civilizational Storage Migration Verified"
        elif errors:
            classification = "Civilizational Storage Migration Partial"

        return {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": _utc_now(),
            "classification": classification,
            "dry_run": dry_run,
            "ssd_available": ssd_available,
            "candidate_count": len(candidates),
            "migrated_or_planned_count": len(migrated),
            "skipped_count": len(skipped),
            "error_count": len(errors),
            "total_candidate_bytes": total_bytes,
            "copied_bytes": copied_bytes,
            "deleted_local_count": deleted_local_count,
            "history_recorded": history_recorded,
            "state_recorded": state_recorded,
            "manifest_path": str(manifest_path),
            "state_path": str(state_path),
            "sample_records": migrated[:10],
            "sample_errors": errors[:5],
            "non_closure_compliant": True,
            "reversible": not delete_local_after_verified_copy,
            "future_step": "F17.2 civilizational_storage_router",
            "epistemic_boundary": "functional_storage_migration_only_no_phenomenal_subjectivity_claim",
        }
