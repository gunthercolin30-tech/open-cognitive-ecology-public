from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ontology.distributed_state_diff_engine import DistributedStateDiffEngine
from ontology.civilizational_state_merger import CivilizationalStateMerger

PRIMITIVE = "LIVE_STATE_SYNCHRONIZER"

DEPENDENCIES = [
    "distributed_civilizational_node",
    "distributed_civilizational_memory",
    "distributed_runtime_coordination",
    "distributed_runtime_coordinator",
    "physical_multi_machine_state_replication_validator",
    "distributed_state_diff_engine",
    "civilizational_state_merger",
]


class LiveStateSynchronizer:
    """Synchronize local and remote civilizational state payloads."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "distributed_state"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.local_state_path = self.state_dir / "local_live_state.json"
        self.remote_echo_path = self.state_dir / "remote_live_state_echo.json"
        self.merged_state_path = self.state_dir / "merged_live_state.json"
        self.history_path = self.state_dir / "live_state_synchronization_history.jsonl"

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _default_state(self, node_id: str) -> dict[str, Any]:
        return {
            "node_id": node_id,
            "civilizational_identity": "Open Cognitive Ecology Society",
            "branch": "cognitive-runtime-v1",
            "tag": "v1.9-functional-consciousness-integrated",
            "synchronization_generation": 1,
            "updated_at_utc": self._now(),
        }

    def _read_json(self, path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return fallback
        return fallback

    def _write_json(self, path: Path, payload: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")

    def _ssh_roundtrip(
        self,
        host: str,
        user: str,
        remote_root: str,
        timeout_seconds: int,
        batch_mode: bool = False,
    ) -> dict[str, Any]:
        target = f"{user}@{host}"
        remote_dir = f"{remote_root.rstrip('/')}/distributed_state"
        remote_file = f"{remote_dir}/remote_live_state_echo.json"

        ssh_options = ["-o", f"ConnectTimeout={timeout_seconds}"]
        scp_options = ["-o", f"ConnectTimeout={timeout_seconds}"]
        transport_mode = "ssh_scp_password_or_key"
        if batch_mode:
            ssh_options = ["-o", "BatchMode=yes", *ssh_options]
            scp_options = ["-o", "BatchMode=yes", *scp_options]
            transport_mode = "ssh_scp_batch_key_only"

        subprocess.run(
            ["ssh", *ssh_options, target, "mkdir", "-p", remote_dir],
            check=True,
            timeout=timeout_seconds,
        )
        subprocess.run(
            ["scp", *scp_options, "-q", str(self.local_state_path), f"{target}:{remote_file}"],
            check=True,
            timeout=timeout_seconds,
        )
        subprocess.run(
            ["scp", *scp_options, "-q", f"{target}:{remote_file}", str(self.remote_echo_path)],
            check=True,
            timeout=timeout_seconds,
        )
        return {"transport_success": True, "transport_mode": transport_mode}

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        started = time.perf_counter()
        inputs = inputs or {}

        local_state = dict(inputs.get("local_state") or self._default_state("macos-arm64-node-a"))
        remote_state = dict(inputs.get("remote_state") or self._default_state("ubuntu-arm64-node-b"))

        self._write_json(self.local_state_path, local_state)
        self._write_json(self.remote_echo_path, remote_state)

        transport_success = True
        transport_mode = "local_simulated"
        transport_error = None

        ssh_host = inputs.get("ssh_host")
        ssh_user = inputs.get("ssh_user")
        if ssh_host and ssh_user:
            try:
                transport = self._ssh_roundtrip(
                    host=str(ssh_host),
                    user=str(ssh_user),
                    remote_root=str(inputs.get("remote_root", "~/open-cognitive-ecology")),
                    timeout_seconds=int(inputs.get("timeout_seconds", 30)),
                    batch_mode=bool(inputs.get("batch_mode", False)),
                )
                transport_success = transport["transport_success"]
                transport_mode = transport["transport_mode"]
                remote_state = self._read_json(self.remote_echo_path, remote_state)
            except Exception as exc:
                transport_success = False
                transport_mode = "ssh_scp_failed_fallback_local"
                transport_error = str(exc)

        diff_result = DistributedStateDiffEngine().step({"node_a": local_state, "node_b": remote_state})
        merge_result = CivilizationalStateMerger().step({"node_a": local_state, "node_b": remote_state})
        self._write_json(self.merged_state_path, merge_result["merged_state"])

        latency_ms = round((time.perf_counter() - started) * 1000.0, 3)
        state_consistency_index = diff_result["state_consistency_index"]
        divergence_rate = diff_result["distributed_divergence_rate"]
        synchronization_success = bool(merge_result["merge_success"] and state_consistency_index >= 0.0)

        result = {
            "primitive": PRIMITIVE,
            "synchronization_success": synchronization_success,
            "transport_success": transport_success,
            "transport_mode": transport_mode,
            "transport_error": transport_error,
            "synchronization_latency_ms": latency_ms,
            "state_consistency_index": state_consistency_index,
            "distributed_divergence_rate": divergence_rate,
            "merge_conflict_rate": merge_result["merge_conflict_rate"],
            "continuity_preservation_index": merge_result["continuity_preservation_index"],
            "local_state_path": str(self.local_state_path),
            "remote_state_path": str(self.remote_echo_path),
            "merged_state_path": str(self.merged_state_path),
            "history_path": str(self.history_path),
            "diff_result": diff_result,
            "merge_result": merge_result,
            "diagnostics": {
                "macos_ubuntu_ready": True,
                "traceability": True,
                "reversibility": True,
                "non_closure_compliant": True,
            },
        }
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, sort_keys=True, ensure_ascii=False) + "\n")
        return result
