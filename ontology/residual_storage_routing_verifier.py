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


class ResidualStorageRoutingVerifier:
    """
    F17.5 — Residual Storage Routing Verifier.

    Verifies that F17.4 symlink-based routing is operational:
    - producer directories remain symlinks;
    - symlinks resolve into /Volumes/OCE_SSD;
    - controlled test writes land on SSD;
    - no real local producer directory reappears;
    - reports are persisted on SSD when available.

    No deletion is performed. Functional storage validation only.
    """

    primitive = "residual_storage_routing_verifier"
    refinement = "F17.5-R1"

    PRODUCER_DIRS = [
        "terminal_conversation_runtime",
        "distributed_identity_state",
        "distributed_attention_state",
        "external_collaboration_execution",
        "runtime_experiments",
        "metrics",
        "grafana",
        "civilizational_mutation",
        "distributed_nodes",
        "community_nodes",
        "external_collaboration",
        "external_memory",
        "collaboration_history_repository_archive",
        "secrets",
    ]

    WRITE_PROBES = {
        "terminal_conversation_runtime": "f17_5_terminal_probe.jsonl",
        "distributed_identity_state": "f17_5_identity_probe.json",
        "distributed_attention_state": "f17_5_attention_probe.json",
        "external_collaboration_execution": "f17_5_external_execution_probe.json",
        "runtime_experiments": "f17_5_runtime_experiment_probe.json",
        "metrics": "f17_5_metrics_probe.jsonl",
        "grafana": "f17_5_grafana_probe.json",
        "civilizational_mutation": "f17_5_mutation_probe.json",
        "distributed_nodes": "f17_5_distributed_node_probe.json",
        "community_nodes": "f17_5_community_node_probe.json",
        "external_collaboration": "f17_5_external_collaboration_probe.json",
        "external_memory": "f17_5_external_memory_probe.json",
        "collaboration_history_repository_archive": "f17_5_collaboration_archive_probe.json",
        "secrets": "f17_5_credential_audit_probe.json",
    }

    def __init__(self, root: Optional[Path] = None, ssd_root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.ssd_root = Path(ssd_root) if ssd_root is not None else DEFAULT_SSD_ROOT

    def _ssd_available(self) -> bool:
        return self.ssd_root.exists() and self.ssd_root.is_dir()

    def _report_base(self) -> Path:
        if self._ssd_available():
            return self.ssd_root / "OCE_ARCHIVE" / "storage_migration" / "f17_5_routing_verifier"
        return self.root / "local_storage_fallback" / "archive" / "f17_5_routing_verifier"

    def _is_under_ssd(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self.ssd_root.resolve())
            return True
        except Exception:
            return False

    def _write_probe(self, producer_dir: str, persist_probe: bool) -> Dict[str, Any]:
        local_dir = self.root / producer_dir
        rel_probe = self.WRITE_PROBES[producer_dir]
        probe_path = local_dir / rel_probe

        payload = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "producer_dir": producer_dir,
            "timestamp_utc": _utc(),
            "probe_type": "controlled_storage_routing_probe",
        }

        record: Dict[str, Any] = {
            "producer_dir": producer_dir,
            "probe_relative_path": rel_probe,
            "probe_path": str(probe_path),
            "persist_probe": persist_probe,
            "write_attempted": False,
            "write_success": False,
            "probe_resolves_under_ssd": False,
            "local_dir_is_symlink": local_dir.is_symlink(),
            "local_dir_exists": local_dir.exists(),
        }

        if not local_dir.exists():
            record["status"] = "producer_dir_missing"
            return record

        if persist_probe:
            try:
                if rel_probe.endswith(".jsonl"):
                    with probe_path.open("a", encoding="utf-8") as f:
                        f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")
                else:
                    probe_path.write_text(
                        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
                        encoding="utf-8",
                    )
                record["write_attempted"] = True
                record["write_success"] = True
            except Exception as exc:
                record["write_attempted"] = True
                record["write_success"] = False
                record["error"] = repr(exc)

        record["probe_exists"] = probe_path.exists()
        if probe_path.exists():
            record["probe_resolved_path"] = str(probe_path.resolve())
            record["probe_resolves_under_ssd"] = self._is_under_ssd(probe_path)
            try:
                record["probe_size_bytes"] = probe_path.stat().st_size
            except Exception:
                record["probe_size_bytes"] = None

        if record["local_dir_is_symlink"] and record["probe_resolves_under_ssd"]:
            record["status"] = "verified_ssd_routed"
        elif record["local_dir_is_symlink"]:
            record["status"] = "symlink_present_probe_not_under_ssd"
        else:
            record["status"] = "local_real_directory_or_missing_symlink"

        return record

    def _verify_dir(self, producer_dir: str, persist_probe: bool) -> Dict[str, Any]:
        local_dir = self.root / producer_dir
        record: Dict[str, Any] = {
            "producer_dir": producer_dir,
            "local_path": str(local_dir),
            "exists": local_dir.exists(),
            "is_symlink": local_dir.is_symlink(),
            "resolved": str(local_dir.resolve()) if local_dir.exists() else None,
            "resolved_under_ssd": self._is_under_ssd(local_dir) if local_dir.exists() else False,
            "timestamp_utc": _utc(),
        }

        record["probe"] = self._write_probe(producer_dir, persist_probe=persist_probe)

        record["verified"] = (
            record["exists"]
            and record["is_symlink"]
            and record["resolved_under_ssd"]
            and record["probe"].get("probe_resolves_under_ssd") is True
            and (not persist_probe or record["probe"].get("write_success") is True)
        )

        return record

    def _backup_summary(self) -> List[Dict[str, Any]]:
        backups = []
        for p in self.root.glob("*.pre_f17_4_local_backup_*"):
            item = {"path": str(p.relative_to(self.root)), "exists": p.exists(), "is_dir": p.is_dir()}
            if p.is_dir():
                count = 0
                size = 0
                for f in p.rglob("*"):
                    if f.is_file():
                        count += 1
                        try:
                            size += f.stat().st_size
                        except Exception:
                            pass
                item["file_count"] = count
                item["size_bytes"] = size
            elif p.exists():
                item["file_count"] = 1
                item["size_bytes"] = p.stat().st_size
            backups.append(item)
        return sorted(backups, key=lambda x: x["path"])

    def step(self, inputs: Optional[dict] = None) -> Dict[str, Any]:
        inputs = inputs or {}
        persist_probe = bool(inputs.get("persist_probe", True))
        selected = inputs.get("producer_dirs")
        if selected is None:
            producer_dirs = list(self.PRODUCER_DIRS)
        else:
            producer_dirs = [str(x) for x in selected if str(x) in self.PRODUCER_DIRS]

        records = [self._verify_dir(d, persist_probe=persist_probe) for d in producer_dirs]
        verified_count = sum(1 for r in records if r.get("verified") is True)
        failed = [r for r in records if r.get("verified") is not True]

        real_local_reappearance = [
            r["producer_dir"]
            for r in records
            if r.get("exists") and not r.get("is_symlink")
        ]

        backups = self._backup_summary()

        classification = (
            "Residual Storage Routing Verified"
            if verified_count == len(records) and not real_local_reappearance
            else "Residual Storage Routing Requires Review"
        )

        payload = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": _utc(),
            "classification": classification,
            "ssd_available": self._ssd_available(),
            "producer_count": len(records),
            "verified_count": verified_count,
            "failed_count": len(failed),
            "real_local_reappearance_count": len(real_local_reappearance),
            "real_local_reappearance": real_local_reappearance,
            "persist_probe": persist_probe,
            "records": records,
            "local_backups_preserved": backups,
            "deletion_performed": False,
            "epistemic_boundary": "functional_storage_routing_verification_only_no_phenomenal_subjectivity_claim",
        }

        base = self._report_base()
        base.mkdir(parents=True, exist_ok=True)
        state_path = base / "f17_5_residual_storage_routing_verification_state.json"
        history_path = base / "f17_5_residual_storage_routing_verification_history.jsonl"

        state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")

        return {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": payload["timestamp_utc"],
            "classification": classification,
            "ssd_available": self._ssd_available(),
            "producer_count": len(records),
            "verified_count": verified_count,
            "failed_count": len(failed),
            "real_local_reappearance_count": len(real_local_reappearance),
            "real_local_reappearance": real_local_reappearance,
            "state_path": str(state_path),
            "history_path": str(history_path),
            "deletion_performed": False,
            "local_backups_preserved_count": len(backups),
            "non_closure_compliant": True,
            "next_step": "F17.6 controlled cleanup of verified local backups or F17.6 residual MOVE_TO_SSD treatment",
        }
