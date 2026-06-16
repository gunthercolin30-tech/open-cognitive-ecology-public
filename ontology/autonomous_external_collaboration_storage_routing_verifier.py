from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


ROOT = Path.home() / "open-cognitive-ecology"
DEFAULT_SSD_ROOT = Path(os.environ.get("OCE_SSD_ROOT", "/Volumes/OCE_SSD"))


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class AutonomousExternalCollaborationStorageRoutingVerifier:
    primitive = "autonomous_external_collaboration_storage_routing_verifier"
    refinement = "F17.7-R1"

    def __init__(self, root: Optional[Path] = None, ssd_root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.ssd_root = Path(ssd_root) if ssd_root is not None else DEFAULT_SSD_ROOT

    def _ssd_available(self) -> bool:
        return self.ssd_root.exists() and self.ssd_root.is_dir()

    def _report_base(self) -> Path:
        if self._ssd_available():
            return self.ssd_root / "OCE_ARCHIVE" / "storage_migration" / "f17_7_autonomous_external_collaboration"
        return self.root / "local_storage_fallback" / "archive" / "f17_7_autonomous_external_collaboration"

    def _route_history_path(self) -> Path:
        try:
            from ontology.civilizational_storage_router import CivilizationalStorageRouter
            return CivilizationalStorageRouter(root=self.root, ssd_root=self.ssd_root).route_path(
                "autonomous_external_collaboration_history.jsonl",
                category="archive",
            )
        except Exception:
            return self.root / "autonomous_external_collaboration_history.jsonl"

    def _local_status(self) -> Dict[str, Any]:
        p = self.root / "autonomous_external_collaboration_history.jsonl"
        return {
            "local_path": str(p),
            "exists": p.exists(),
            "is_file": p.is_file(),
            "is_symlink": p.is_symlink(),
            "size_bytes": p.stat().st_size if p.exists() and p.is_file() else 0,
        }

    def step(self, inputs: Optional[dict] = None) -> Dict[str, Any]:
        inputs = inputs or {}
        persist_probe = bool(inputs.get("persist_probe", True))

        local_before = self._local_status()
        routed_path = self._route_history_path()

        probe_record = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": _utc(),
            "event": "F17_7_STORAGE_ROUTING_PROBE",
        }

        write_success = False
        write_error = None

        if persist_probe:
            try:
                routed_path.parent.mkdir(parents=True, exist_ok=True)
                with routed_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(probe_record, ensure_ascii=False, sort_keys=True) + "\n")
                write_success = True
            except Exception as exc:
                write_error = repr(exc)

        local_after = self._local_status()

        routed_exists = routed_path.exists()
        routed_resolved = routed_path.resolve() if routed_exists else routed_path
        routed_under_ssd = str(routed_resolved).startswith(str(self.ssd_root)) if routed_exists else False

        local_path = Path(local_after["local_path"])
        local_real_file_reappeared = (
            local_after["exists"]
            and local_after["is_file"]
            and not local_after["is_symlink"]
            and str(local_path.resolve()) != str(routed_resolved)
        )

        verified = (
            self._ssd_available()
            and routed_exists
            and routed_under_ssd
            and (not persist_probe or write_success)
            and not local_real_file_reappeared
        )

        classification = (
            "Autonomous External Collaboration Storage Routing Verified"
            if verified
            else "Autonomous External Collaboration Storage Routing Requires Review"
        )

        payload = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": _utc(),
            "classification": classification,
            "ssd_available": self._ssd_available(),
            "routed_path": str(routed_path),
            "routed_exists": routed_exists,
            "routed_under_ssd": routed_under_ssd,
            "persist_probe": persist_probe,
            "write_success": write_success,
            "write_error": write_error,
            "local_before": local_before,
            "local_after": local_after,
            "local_real_file_reappeared": local_real_file_reappeared,
            "verified": verified,
            "deletion_performed": False,
            "epistemic_boundary": "functional_storage_routing_verification_only_no_phenomenal_subjectivity_claim",
        }

        base = self._report_base()
        base.mkdir(parents=True, exist_ok=True)
        state_path = base / "f17_7_autonomous_external_collaboration_storage_routing_state.json"
        history_path = base / "f17_7_autonomous_external_collaboration_storage_routing_history.jsonl"

        state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        with history_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")

        return {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "timestamp_utc": payload["timestamp_utc"],
            "classification": classification,
            "ssd_available": self._ssd_available(),
            "routed_path": str(routed_path),
            "routed_under_ssd": routed_under_ssd,
            "write_success": write_success,
            "local_real_file_reappeared": local_real_file_reappeared,
            "verified": verified,
            "state_path": str(state_path),
            "history_path": str(history_path),
            "deletion_performed": False,
            "non_closure_compliant": True,
            "next_step": "F17 closure verification or G interaction physique et multimodale",
        }
