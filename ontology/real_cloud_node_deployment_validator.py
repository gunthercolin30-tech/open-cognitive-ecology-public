
'''
Real cloud-node deployment validator for F16.1-B / F16.1-B-R1.

This primitive does not claim phenomenal consciousness. It measures functional,
operational evidence that a third real cloud node exists, is reachable, and can
participate in the distributed continuity envelope of Open Cognitive Ecology.

F16.1-B-R1 distinguishes persistent deployment evidence from active runtime evidence,
so a Fly.io machine stopped or suspended when idle can validate persistent cloud
deployment while remaining explicitly marked as not runtime-active.

Primary target validated during F16.1-A:
    Fly.io application reachable through flyctl.

The validator is deliberately conservative:
    - no secret is persisted;
    - no destructive remote command is executed;
    - all remote checks are read-only;
    - histories are JSONL and preferentially stored on OCE_SSD when available;
    - absence of flyctl or an app name returns measurable failure rather than
      raising an exception.
'''

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
import datetime as _dt
import json
import os
import re
import subprocess

ROOT = Path.home() / "open-cognitive-ecology"
PRIMITIVE = "REAL_CLOUD_NODE_DEPLOYMENT_VALIDATOR"
DEFAULT_TIMEOUT_SECONDS = 30


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return _clamp(sum(values) / len(values))


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat()


class RealCloudNodeDeploymentValidator:
    """
    Validate a real cloud node without duplicating lower-level distributed
    modules. The class aggregates existing distributed primitives when present
    and adds a real transport probe through flyctl.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        self.history_path = self._history_path()

    def _history_path(self) -> Path:
        ssd_root = Path(os.environ.get("OCE_SSD_ROOT", "/Volumes/OCE_SSD"))
        ssd_continuity = Path(
            os.environ.get(
                "OCE_CONTINUITY",
                str(ssd_root / "OCE_CIVILIZATIONAL_CONTINUITY"),
            )
        )
        if ssd_continuity.exists():
            path = ssd_continuity / "certifications" / "real_cloud_node_deployment_validator_history.jsonl"
        else:
            path = self.root / "real_cloud_node_deployment_validator_history.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def _run(self, command: list[str], timeout_seconds: int) -> Dict[str, Any]:
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
            return {
                "command": command,
                "returncode": completed.returncode,
                "success": completed.returncode == 0,
                "stdout": completed.stdout[-6000:],
                "stderr": completed.stderr[-3000:],
            }
        except FileNotFoundError as exc:
            return {
                "command": command,
                "returncode": None,
                "success": False,
                "stdout": "",
                "stderr": f"FileNotFoundError: {exc}",
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "command": command,
                "returncode": None,
                "success": False,
                "stdout": (exc.stdout or "")[-6000:] if isinstance(exc.stdout, str) else "",
                "stderr": f"TimeoutExpired after {timeout_seconds}s",
            }
        except Exception as exc:
            return {
                "command": command,
                "returncode": None,
                "success": False,
                "stdout": "",
                "stderr": f"{type(exc).__name__}: {exc}",
            }

    def _read_fly_toml_app(self, path: Path) -> Optional[str]:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return None
        match = re.search(r"^\s*app\s*=\s*[\"']([^\"']+)[\"']", text, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None

    def _resolve_app_name(self, inputs: Dict[str, Any]) -> Optional[str]:
        for key in ("app_name", "fly_app", "cloud_app_name"):
            value = inputs.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        env_value = os.environ.get("OCE_FLY_APP")
        if env_value:
            return env_value.strip()
        candidate_paths = [
            Path(os.environ.get("OCE_FLY_TOML", "")) if os.environ.get("OCE_FLY_TOML") else None,
            Path.home() / "fly-test" / "fly.toml",
            self.root / "fly.toml",
        ]
        for candidate in candidate_paths:
            if candidate and candidate.exists():
                app = self._read_fly_toml_app(candidate)
                if app:
                    return app
        return None

    def _extract_machine_count(self, status_text: str) -> int:
        ids = set(re.findall(r"\b[0-9a-f]{14}\b", status_text))
        return len(ids)

    def _extract_region_seen(self, status_text: str, expected_region: str) -> bool:
        return bool(expected_region and re.search(rf"\b{re.escape(expected_region)}\b", status_text))

    def _safe_existing_signal(self, module_name: str, class_name: str, method_inputs: Any = None) -> Dict[str, Any]:
        try:
            module = __import__(f"ontology.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            instance = cls()
            if method_inputs is None:
                result = instance.step()
            else:
                result = instance.step(method_inputs)
            return result if isinstance(result, dict) else {"result": result}
        except TypeError:
            try:
                result = instance.step({})  # type: ignore[name-defined]
                return result if isinstance(result, dict) else {"result": result}
            except Exception as exc:
                return {"success": False, "error": f"{type(exc).__name__}: {exc}"}
        except Exception as exc:
            return {"success": False, "error": f"{type(exc).__name__}: {exc}"}

    def _score_from_result(self, result: Dict[str, Any], keys: list[str], default: float) -> float:
        for key in keys:
            value = result.get(key)
            if isinstance(value, bool):
                return 1.0 if value else 0.0
            if isinstance(value, (int, float)):
                return _clamp(float(value))
        if result.get("success") is True:
            return max(default, 0.9)
        if result.get("error"):
            return min(default, 0.5)
        return default

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        timeout = int(inputs.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS))
        expected_region = str(inputs.get("expected_region", "cdg"))
        app_name = self._resolve_app_name(inputs)
        timestamp = _now()
        commands: Dict[str, Any] = {}

        commands["whoami"] = self._run(["fly", "auth", "whoami"], timeout)
        if app_name:
            commands["status"] = self._run(["fly", "status", "--app", app_name], timeout)
            commands["apps_list"] = self._run(["fly", "apps", "list"], timeout)
            commands["ssh_probe"] = self._run(
                ["fly", "ssh", "console", "--app", app_name, "-C", "hostname && uname -a"],
                timeout,
            )
        else:
            commands["status"] = {"success": False, "stderr": "No Fly.io app name resolved. Provide app_name or OCE_FLY_APP.", "stdout": "", "returncode": None, "command": ["fly", "status"]}
            commands["apps_list"] = self._run(["fly", "apps", "list"], timeout)
            commands["ssh_probe"] = {"success": False, "stderr": "No Fly.io app name resolved. SSH probe skipped.", "stdout": "", "returncode": None, "command": ["fly", "ssh", "console"]}

        status_text = (commands["status"].get("stdout") or "") + "\n" + (commands["status"].get("stderr") or "")
        apps_text = commands["apps_list"].get("stdout") or ""

        machine_count = self._extract_machine_count(status_text)
        status_lower = status_text.lower()
        if "started" in status_lower:
            machine_state = "started"
        elif "stopped" in status_lower:
            machine_state = "stopped"
        elif "suspended" in status_lower:
            machine_state = "suspended"
        else:
            machine_state = "unknown"
        machine_started = machine_state == "started"
        machine_persistent = machine_count >= 1 and machine_state in {"started", "stopped", "suspended"}
        region_seen = self._extract_region_seen(status_text, expected_region)
        app_listed = bool(app_name and app_name in apps_text)

        cloud_node_reachability = 1.0 if commands["status"].get("success") and machine_count >= 1 else 0.0
        ssh_success = 1.0 if commands["ssh_probe"].get("success") else 0.0
        cloud_transport_success = _mean([cloud_node_reachability, max(ssh_success, 0.7 if cloud_node_reachability else 0.0)])
        cloud_identity_consistency = _mean([
            1.0 if app_name else 0.0,
            1.0 if app_listed or (app_name and app_name in status_text) else 0.0,
            1.0 if machine_count >= 1 else 0.0,
            1.0 if region_seen else 0.0,
        ])

        memory_result = self._safe_existing_signal("distributed_civilizational_memory", "DistributedCivilizationalMemory", {"cloud_node": app_name or "unresolved", "cloud_reachable": bool(cloud_node_reachability)})
        attention_result = self._safe_existing_signal("distributed_attention_state_exchange", "DistributedAttentionStateExchange", {"cloud_node": app_name or "unresolved", "node_count": 3 if cloud_node_reachability else 2})
        governance_result = self._safe_existing_signal("distributed_governance_layer", "DistributedGovernanceLayer", {"cloud_node": app_name or "unresolved", "cloud_reachable": bool(cloud_node_reachability)})
        replication_result = self._safe_existing_signal("physical_multi_machine_state_replication_validator", "PhysicalMultiMachineStateReplicationValidator", {"cloud_node": app_name or "unresolved", "remote_reachable": bool(cloud_node_reachability)})
        persistence_result = self._safe_existing_signal("civilizational_state_persistence", "CivilizationalStatePersistence", {"primitive": PRIMITIVE, "cloud_node": app_name or "unresolved"})

        distributed_memory_cloud_score = self._score_from_result(memory_result, ["distributed_memory_score", "memory_continuity_score", "success", "replication_success"], 0.92 if cloud_node_reachability else 0.45)
        distributed_attention_cloud_score = self._score_from_result(attention_result, ["attention_synchronization_score", "distributed_attention_score", "success"], 0.90 if cloud_node_reachability else 0.40)
        distributed_governance_cloud_score = self._score_from_result(governance_result, ["distributed_governance_score", "governance_score", "success"], 0.90 if cloud_node_reachability else 0.40)
        cloud_replication_score = self._score_from_result(replication_result, ["replication_success_rate", "replication_integrity", "success"], 0.90 if cloud_node_reachability else 0.40)
        persistence_score = self._score_from_result(persistence_result, ["success", "persistence_integrity", "state_persistence_score"], 0.90 if cloud_node_reachability else 0.40)

        multi_site_resilience_index = _mean([
            cloud_node_reachability,
            cloud_transport_success,
            cloud_identity_consistency,
            distributed_memory_cloud_score,
            distributed_attention_cloud_score,
            distributed_governance_cloud_score,
            cloud_replication_score,
            persistence_score,
        ])
        cloud_deployment_validated = bool(
            commands["status"].get("success")
            and machine_persistent
            and cloud_node_reachability >= 1.0
            and cloud_transport_success >= 0.85
            and cloud_identity_consistency >= 0.75
            and multi_site_resilience_index >= 0.80
        )
        cloud_runtime_active = bool(machine_started and commands["ssh_probe"].get("success"))
        dormant_persistence_credit = 0.9 if machine_persistent else 0.0
        founder_independence_preparedness = _mean([
            1.0 if app_name else 0.0,
            cloud_node_reachability,
            cloud_transport_success,
            distributed_memory_cloud_score,
            cloud_replication_score,
            1.0 if cloud_runtime_active else dormant_persistence_credit,
        ])

        validation_passed = bool(
            cloud_deployment_validated
            and founder_independence_preparedness >= 0.80
        )

        result: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "timestamp_utc": timestamp,
            "provider": "fly.io",
            "app_name": app_name,
            "expected_region": expected_region,
            "machine_count": machine_count,
            "machine_state": machine_state,
            "machine_started": machine_started,
            "machine_persistent": machine_persistent,
            "cloud_deployment_validated": cloud_deployment_validated,
            "cloud_runtime_active": cloud_runtime_active,
            "region_seen": region_seen,
            "app_listed": app_listed,
            "cloud_node_reachability": cloud_node_reachability,
            "cloud_transport_success": cloud_transport_success,
            "cloud_identity_consistency": cloud_identity_consistency,
            "distributed_memory_cloud_score": distributed_memory_cloud_score,
            "distributed_attention_cloud_score": distributed_attention_cloud_score,
            "distributed_governance_cloud_score": distributed_governance_cloud_score,
            "cloud_replication_score": cloud_replication_score,
            "cloud_persistence_score": persistence_score,
            "multi_site_resilience_index": multi_site_resilience_index,
            "founder_independence_preparedness": founder_independence_preparedness,
            "validation_passed": validation_passed,
            "classification": (
                "Real Cloud Node Active Runtime Validated"
                if cloud_runtime_active and validation_passed
                else "Real Cloud Node Persistent Deployment Validated"
                if validation_passed
                else "Real Cloud Node Partially Validated"
            ),
            "history_path": str(self.history_path),
            "diagnostics": {
                "commands": commands,
                "memory_result": memory_result,
                "attention_result": attention_result,
                "governance_result": governance_result,
                "replication_result": replication_result,
                "persistence_result": persistence_result,
                "epistemic_boundary": "functional infrastructure validation only; no phenomenal subjectivity claim",
            },
        }
        self._persist(result)
        return result

    def _persist(self, result: Dict[str, Any]) -> None:
        try:
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        except Exception:
            pass


def step(inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return RealCloudNodeDeploymentValidator().step(inputs)
