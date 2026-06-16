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


class PreventiveGrowthProducerRouting:
    """
    F17.8 — Preventive Growth Producer Routing.

    Preventively routes low-volume but future-growth-capable producer
    directories to SSD-backed destinations. The mechanism is intentionally
    generic: it moves existing local content, creates a reversible local backup,
    replaces the producer directory by a symlink, and verifies controlled writes.

    Functional storage routing only; no phenomenal subjectivity claim.
    """

    primitive = "preventive_growth_producer_routing"
    refinement = "F17.8-R1"

    ROUTES = {
        # Memory / archives
        "civilizational_memory_archive": ("OCE_MEMORY", "preventive_growth/civilizational_memory_archive"),
        "conversation_archives": ("OCE_MEMORY", "preventive_growth/conversation_archives"),
        "dialogue_memory": ("OCE_MEMORY", "preventive_growth/dialogue_memory"),
        "data": ("OCE_MEMORY", "preventive_growth/data"),
        "web_navigation": ("OCE_MEMORY", "preventive_growth/web_navigation"),
        "causal_reasoning": ("OCE_MEMORY", "preventive_growth/causal_reasoning"),

        # Dashboards / metrics
        "web_dashboard_exports": ("OCE_DASHBOARDS", "preventive_growth/web_dashboard_exports"),
        "civilizational_metrics": ("OCE_METRICS", "preventive_growth/civilizational_metrics"),
        "longitudinal_observatory": ("OCE_METRICS", "preventive_growth/longitudinal_observatory"),

        # Governance / self-improvement
        "self_improvement_governance": ("OCE_ARCHIVE", "preventive_growth/self_improvement_governance"),
        "conversational_governance": ("OCE_ARCHIVE", "preventive_growth/conversational_governance"),
        "peer_review_interface": ("OCE_ARCHIVE", "preventive_growth/peer_review_interface"),
        "scientific_community_connector": ("OCE_ARCHIVE", "preventive_growth/scientific_community_connector"),
        "knowledge_acquisition": ("OCE_ARCHIVE", "preventive_growth/knowledge_acquisition"),

        # Runtime / distributed state
        "local_storage_fallback": ("OCE_ARCHIVE", "preventive_growth/local_storage_fallback"),
        "civilizational_state": ("OCE_CIVILIZATIONAL_CONTINUITY", "preventive_growth/civilizational_state"),
        "distributed_state": ("OCE_CIVILIZATIONAL_CONTINUITY", "preventive_growth/distributed_state"),
        "distributed_runtime": ("OCE_CIVILIZATIONAL_CONTINUITY", "preventive_growth/distributed_runtime"),
        "runtime_supervision": ("OCE_CIVILIZATIONAL_CONTINUITY", "preventive_growth/runtime_supervision"),
        "runtime_service": ("OCE_CIVILIZATIONAL_CONTINUITY", "preventive_growth/runtime_service"),
        "runtime_history": ("OCE_CIVILIZATIONAL_CONTINUITY", "preventive_growth/runtime_history"),
        "resource_management": ("OCE_CIVILIZATIONAL_CONTINUITY", "preventive_growth/resource_management"),

        # Node / deployment / embodied interface
        "raspberry_pi_nodes": ("OCE_CIVILIZATIONAL_CONTINUITY", "preventive_growth/raspberry_pi_nodes"),
        "linux_nodes": ("OCE_CIVILIZATIONAL_CONTINUITY", "preventive_growth/linux_nodes"),
        "simulated_multi_node_deployment": ("OCE_CIVILIZATIONAL_CONTINUITY", "preventive_growth/simulated_multi_node_deployment"),
        "internet_resident_agent": ("OCE_EXPERIMENTS", "preventive_growth/internet_resident_agent"),
        "embodied_world_interface": ("OCE_EXPERIMENTS", "preventive_growth/embodied_world_interface"),
        "conversation_initiatives": ("OCE_EXPERIMENTS", "preventive_growth/conversation_initiatives"),
    }

    def __init__(self, root: Optional[Path] = None, ssd_root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.ssd_root = Path(ssd_root) if ssd_root is not None else DEFAULT_SSD_ROOT

    def _ssd_available(self) -> bool:
        return self.ssd_root.exists() and self.ssd_root.is_dir()

    def _report_base(self) -> Path:
        if self._ssd_available():
            return self.ssd_root / "OCE_ARCHIVE" / "storage_migration" / "f17_8_preventive_growth_routing"
        return self.root / "local_storage_fallback" / "archive" / "f17_8_preventive_growth_routing"

    def _under_ssd(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self.ssd_root.resolve())
            return True
        except Exception:
            return str(path.resolve()).startswith(str(self.ssd_root))

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

    def _destination_for(self, directory: str) -> Path:
        top, rel = self.ROUTES[directory]
        return self.ssd_root / top / rel

    def _backup_path_for(self, local_path: Path) -> Path:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        return self.root / f"{local_path.name}.pre_f17_8_local_backup_{stamp}"

    def _copy_tree_contents(self, source: Path, destination: Path) -> None:
        destination.mkdir(parents=True, exist_ok=True)
        if not source.exists():
            return
        if source.is_file():
            shutil.copy2(source, destination / source.name)
            return
        for item in source.iterdir():
            dst = destination / item.name
            if item.is_dir() and not item.is_symlink():
                shutil.copytree(item, dst, dirs_exist_ok=True)
            elif item.is_file() or item.is_symlink():
                dst.parent.mkdir(parents=True, exist_ok=True)
                if dst.exists() or dst.is_symlink():
                    if dst.is_dir() and not dst.is_symlink():
                        shutil.rmtree(dst)
                    else:
                        dst.unlink()
                shutil.copy2(item, dst)

    def _route_one(self, directory: str, dry_run: bool, persist_probe: bool) -> Dict[str, Any]:
        local = self.root / directory
        destination = self._destination_for(directory)
        before = self._count_and_size(local)

        record: Dict[str, Any] = {
            "directory": directory,
            "local_path": str(local),
            "destination": str(destination),
            "exists_before": local.exists(),
            "is_symlink_before": local.is_symlink(),
            "resolved_before": str(local.resolve()) if local.exists() else None,
            "before": before,
            "dry_run": dry_run,
            "status": "planned",
            "backup_path": None,
            "copy_performed": False,
            "symlink_created": False,
            "write_probe_success": False,
            "verified": False,
            "error": None,
        }

        if not self._ssd_available():
            record["status"] = "skipped_ssd_unavailable"
            return record

        if local.exists() and local.is_symlink():
            target_under_ssd = self._under_ssd(local)
            record["status"] = "already_symlinked" if target_under_ssd else "symlink_not_under_ssd"
            if persist_probe and target_under_ssd and not dry_run:
                try:
                    probe = local / f"f17_8_probe_{directory}.json"
                    probe.write_text(json.dumps({
                        "primitive": self.primitive,
                        "refinement": self.refinement,
                        "directory": directory,
                        "timestamp_utc": _utc(),
                    }, ensure_ascii=False, sort_keys=True), encoding="utf-8")
                    record["write_probe_success"] = probe.exists() and self._under_ssd(probe)
                except Exception as exc:
                    record["error"] = repr(exc)
            record["verified"] = target_under_ssd and (not persist_probe or dry_run or record["write_probe_success"])
            return record

        if dry_run:
            record["status"] = "planned_route_to_ssd"
            record["verified"] = False
            return record

        try:
            destination.mkdir(parents=True, exist_ok=True)

            if local.exists():
                self._copy_tree_contents(local, destination)
                record["copy_performed"] = True
                backup = self._backup_path_for(local)
                if backup.exists() or backup.is_symlink():
                    backup = self.root / f"{backup.name}_dup"
                local.rename(backup)
                record["backup_path"] = str(backup)
            else:
                destination.mkdir(parents=True, exist_ok=True)

            os.symlink(destination, local, target_is_directory=True)
            record["symlink_created"] = True

            if persist_probe:
                probe = local / f"f17_8_probe_{directory}.json"
                probe.write_text(json.dumps({
                    "primitive": self.primitive,
                    "refinement": self.refinement,
                    "directory": directory,
                    "timestamp_utc": _utc(),
                    "probe_type": "preventive_growth_routing",
                }, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
                record["write_probe_success"] = probe.exists() and self._under_ssd(probe)

            after_target = self._count_and_size(destination)
            record["after_target"] = after_target
            record["status"] = "routed"
            record["verified"] = (
                local.exists()
                and local.is_symlink()
                and self._under_ssd(local)
                and after_target["file_count"] >= before["file_count"]
                and after_target["size_bytes"] >= before["size_bytes"]
                and (not persist_probe or record["write_probe_success"])
            )

        except Exception as exc:
            record["status"] = "error"
            record["error"] = repr(exc)

        return record

    def _verify_only(self, directory: str, persist_probe: bool = True) -> Dict[str, Any]:
        local = self.root / directory
        destination = self._destination_for(directory)

        record: Dict[str, Any] = {
            "directory": directory,
            "local_path": str(local),
            "destination": str(destination),
            "exists": local.exists(),
            "is_symlink": local.is_symlink(),
            "resolved": str(local.resolve()) if local.exists() else None,
            "resolved_under_ssd": self._under_ssd(local) if local.exists() else False,
            "write_probe_success": False,
            "verified": False,
        }

        if local.exists() and local.is_symlink() and record["resolved_under_ssd"] and persist_probe:
            try:
                probe = local / f"f17_8_verify_{directory}.json"
                probe.write_text(json.dumps({
                    "primitive": self.primitive,
                    "refinement": self.refinement,
                    "directory": directory,
                    "timestamp_utc": _utc(),
                    "probe_type": "verification",
                }, ensure_ascii=False, sort_keys=True), encoding="utf-8")
                record["write_probe_success"] = probe.exists() and self._under_ssd(probe)
            except Exception as exc:
                record["error"] = repr(exc)

        record["verified"] = (
            record["exists"]
            and record["is_symlink"]
            and record["resolved_under_ssd"]
            and (not persist_probe or record["write_probe_success"])
        )
        return record

    def step(self, inputs: Optional[dict] = None) -> Dict[str, Any]:
        inputs = inputs or {}
        dry_run = bool(inputs.get("dry_run", True))
        persist_probe = bool(inputs.get("persist_probe", True))
        verify_only = bool(inputs.get("verify_only", False))

        selected = inputs.get("directories")
        if selected is None:
            directories = list(self.ROUTES.keys())
        else:
            directories = [str(x) for x in selected if str(x) in self.ROUTES]

        if verify_only:
            records = [self._verify_only(d, persist_probe=persist_probe) for d in directories]
        else:
            records = [self._route_one(d, dry_run=dry_run, persist_probe=persist_probe) for d in directories]

        verified_count = sum(1 for r in records if r.get("verified") is True)
        error_count = sum(1 for r in records if r.get("status") == "error" or r.get("error"))
        routed_count = sum(1 for r in records if r.get("status") == "routed")
        planned_count = sum(1 for r in records if r.get("status") in {"planned_route_to_ssd", "planned"})
        already_count = sum(1 for r in records if r.get("status") == "already_symlinked")
        skipped_count = sum(1 for r in records if r.get("status") == "skipped_ssd_unavailable")

        classification = "Preventive Growth Producer Routing Planned"
        if skipped_count:
            classification = "Preventive Growth Producer Routing Degraded SSD Unavailable"
        elif verify_only and verified_count == len(records):
            classification = "Preventive Growth Producer Routing Verified"
        elif not dry_run and error_count == 0 and verified_count == len(records):
            classification = "Preventive Growth Producer Routing Applied"
        elif error_count:
            classification = "Preventive Growth Producer Routing Requires Review"

        payload = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": _utc(),
            "classification": classification,
            "ssd_available": self._ssd_available(),
            "dry_run": dry_run,
            "verify_only": verify_only,
            "persist_probe": persist_probe,
            "directory_count": len(records),
            "verified_count": verified_count,
            "routed_count": routed_count,
            "planned_count": planned_count,
            "already_symlinked_count": already_count,
            "skipped_count": skipped_count,
            "error_count": error_count,
            "records": records,
            "deletion_performed": False,
            "epistemic_boundary": "functional_storage_routing_only_no_phenomenal_subjectivity_claim",
        }

        base = self._report_base()
        base.mkdir(parents=True, exist_ok=True)
        state_path = base / "f17_8_preventive_growth_producer_routing_state.json"
        history_path = base / "f17_8_preventive_growth_producer_routing_history.jsonl"

        state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")

        return {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": payload["timestamp_utc"],
            "classification": classification,
            "ssd_available": payload["ssd_available"],
            "dry_run": dry_run,
            "verify_only": verify_only,
            "directory_count": len(records),
            "verified_count": verified_count,
            "routed_count": routed_count,
            "planned_count": planned_count,
            "already_symlinked_count": already_count,
            "skipped_count": skipped_count,
            "error_count": error_count,
            "state_path": str(state_path),
            "history_path": str(history_path),
            "deletion_performed": False,
            "non_closure_compliant": True,
            "next_step": "F17.9 storage policy enforcement or G interaction physique et multimodale",
        }
