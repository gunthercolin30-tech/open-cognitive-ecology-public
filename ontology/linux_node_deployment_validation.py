
'''
Open Cognitive Ecology - F11 Linux Node Deployment Validation.

This ontology primitive validates whether an Open Cognitive Ecology node can be
installed, initialized, validated and prepared for governed distributed
synchronization on a Linux host. It does not assert phenomenal subjectivity; it
only measures functional, architectural and operational indicators.
'''

from __future__ import annotations

import hashlib
import importlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class LinuxNodeDeploymentValidation:
    '''Validate Linux deployment readiness for an OCE distributed node.'''

    primitive = "LINUX_NODE_DEPLOYMENT_VALIDATION"
    dependencies = [
        "distributed_deployment_readiness", "dual_host_deployment_validator",
        "physical_multi_machine_state_replication_validator",
        "autonomous_host_discovery_and_selection_orchestrator",
        "autonomous_host_preparation", "autonomous_host_selection_governance",
        "autonomous_inter_host_negotiation",
        "autonomous_inter_node_civilizational_coordination",
        "distributed_runtime_activation", "distributed_runtime_coordination",
        "distributed_runtime_coordinator", "distributed_civilizational_node",
        "community_node_onboarding", "node_capability_registry",
        "failure_recovery_orchestrator", "civilizational_state_persistence",
        "metrics_history_recorder",
    ]
    critical_imports = [
        "ontology.distributed_civilizational_node",
        "ontology.distributed_runtime_coordination",
        "ontology.distributed_runtime_coordinator",
        "ontology.community_node_onboarding",
        "ontology.node_capability_registry",
        "ontology.failure_recovery_orchestrator",
        "ontology.civilizational_state_persistence",
    ]

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.ontology_dir = self.root / "ontology"
        self.state_dir = self.root / "linux_nodes"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.state_dir / "linux_node_deployment_validation_history.jsonl"
        self.latest_report_path = self.state_dir / "latest_linux_node_deployment_validation.json"

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _clamp(self, value: Any, default: float = 0.0) -> float:
        try:
            value = float(value)
        except Exception:
            value = default
        return max(0.0, min(1.0, value))

    def _host_fingerprint(self, data: dict[str, Any]) -> str:
        raw = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:24]

    def _python_version_score(self) -> float:
        major, minor = sys.version_info[:2]
        if major > 3 or (major == 3 and minor >= 11):
            return 1.0
        if major == 3 and minor >= 9:
            return 0.95
        if major == 3 and minor >= 8:
            return 0.75
        return 0.35

    def _project_score(self) -> tuple[float, dict[str, bool]]:
        checks = {
            "root_exists": self.root.exists(),
            "ontology_dir_exists": self.ontology_dir.exists(),
            "ontology_init_exists": (self.ontology_dir / "__init__.py").exists(),
            "validation_main_exists": (self.root / "validation" / "main.py").exists(),
            "dependency_registry_exists": (self.ontology_dir / "dependency_registry.py").exists(),
        }
        return sum(1 for ok in checks.values() if ok) / len(checks), checks

    def _import_score(self) -> tuple[float, list[str], list[str]]:
        imported, failed = [], []
        root_str = str(self.root)
        if root_str not in sys.path:
            sys.path.insert(0, root_str)
        for module_name in self.critical_imports:
            try:
                importlib.import_module(module_name)
                imported.append(module_name)
            except Exception as exc:
                failed.append(f"{module_name}: {exc.__class__.__name__}: {exc}")
        return len(imported) / len(self.critical_imports), imported, failed

    def _optional_validation_probe(self, run_validation_probe: bool) -> dict[str, Any]:
        if not run_validation_probe:
            return {"executed": False, "score": 0.9, "success": None, "reason": "probe_disabled"}
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "validation.main"],
                cwd=str(self.root), text=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, timeout=180,
            )
            return {
                "executed": True,
                "score": 1.0 if proc.returncode == 0 else 0.35,
                "success": proc.returncode == 0,
                "returncode": proc.returncode,
                "stdout_tail": proc.stdout[-1200:],
                "stderr_tail": proc.stderr[-1200:],
            }
        except Exception as exc:
            return {"executed": True, "score": 0.25, "success": False, "error": f"{exc.__class__.__name__}: {exc}"}

    def _classify(self, native_linux: bool, simulation_mode: bool, score: float, hard_failures: list[str]):
        if hard_failures:
            return "rejected", False, False, hard_failures
        if native_linux and score >= 0.90:
            return "validated", True, False, ["native_linux_deployment_validated"]
        if native_linux and score >= 0.82:
            return "probation", False, True, ["native_linux_deployment_requires_remediation"]
        if simulation_mode and score >= 0.86:
            return "simulation_ready", False, True, ["linux_deployment_simulation_ready"]
        if score >= 0.75:
            return "degraded", False, True, ["linux_deployment_degraded_readiness"]
        return "rejected", False, False, ["linux_deployment_readiness_below_threshold"]

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        target_os = str(inputs.get("target_os") or platform.system() or "unknown")
        simulation_mode = bool(inputs.get("simulation_mode", False))
        require_native_linux = bool(inputs.get("require_native_linux", False))
        run_validation_probe = bool(inputs.get("run_validation_probe", False))

        actual_system = platform.system()
        native_linux = actual_system.lower() == "linux"
        linux_target_declared = "linux" in target_os.lower()
        os_score = 1.0 if native_linux else (0.86 if simulation_mode and linux_target_declared else 0.35)
        python_score = self._python_version_score()
        project_score, project_checks = self._project_score()
        import_score, imported_modules, failed_imports = self._import_score()
        persistence_probe_path = self.state_dir / "linux_persistence_probe.json"
        try:
            persistence_probe_path.write_text(json.dumps({"timestamp_utc": self._timestamp()}), encoding="utf-8")
            persistence_score = 1.0 if persistence_probe_path.exists() else 0.0
        except Exception:
            persistence_score = 0.0
        validation_probe = self._optional_validation_probe(run_validation_probe)
        validation_score = self._clamp(validation_probe.get("score"), 0.9)
        governance_score = self._clamp(inputs.get("governance_compatibility", 0.94), 0.94)
        identity_score = self._clamp(inputs.get("identity_compatibility", 0.95), 0.95)
        non_closure_score = self._clamp(inputs.get("non_closure_score", 0.95), 0.95)
        traceability_score = self._clamp(inputs.get("traceability_score", 0.94), 0.94)
        synchronization_score = self._clamp(inputs.get("synchronization_readiness", 0.91), 0.91)
        recovery_score = self._clamp(inputs.get("failure_recovery_readiness", 0.92), 0.92)
        hard_failures = []
        if require_native_linux and not native_linux:
            hard_failures.append("native_linux_required_but_not_detected")
        if governance_score < 0.80:
            hard_failures.append("governance_compatibility_below_threshold")
        if identity_score < 0.80:
            hard_failures.append("identity_compatibility_below_threshold")
        if non_closure_score < 0.80:
            hard_failures.append("non_closure_score_below_threshold")
        if traceability_score < 0.75:
            hard_failures.append("traceability_score_below_threshold")
        if project_score < 0.70:
            hard_failures.append("project_structure_incomplete")
        if import_score < 0.70:
            hard_failures.append("critical_imports_below_threshold")
        deployment_score = round((
            os_score * 0.14 + python_score * 0.09 + project_score * 0.10
            + import_score * 0.10 + persistence_score * 0.08 + validation_score * 0.08
            + governance_score * 0.09 + identity_score * 0.09 + non_closure_score * 0.09
            + traceability_score * 0.06 + synchronization_score * 0.04 + recovery_score * 0.04
        ), 4)
        deployment_status, certified, probation_required, reasons = self._classify(
            native_linux, simulation_mode, deployment_score, hard_failures)
        host_descriptor = {
            "actual_system": actual_system,
            "actual_release": platform.release(),
            "actual_machine": platform.machine(),
            "python_version": sys.version.split()[0],
            "root": str(self.root),
            "target_os": target_os,
            "simulation_mode": simulation_mode,
        }
        host_fingerprint = self._host_fingerprint(host_descriptor)
        certificate_id = "OCELINUX-" + self._host_fingerprint({"host": host_fingerprint, "score": deployment_score})[:18]
        if deployment_status == "validated":
            recommended_actions = ["register_as_validated_linux_node", "enable_governed_multi_host_synchronization", "schedule_periodic_linux_node_revalidation"]
        elif deployment_status == "simulation_ready":
            recommended_actions = ["deploy_on_native_linux_host", "rerun_with_require_native_linux_true", "run_validation_probe_on_linux"]
        elif deployment_status == "probation":
            recommended_actions = ["keep_linux_node_in_probation", "remediate_failed_checks", "rerun_validation_before_synchronization"]
        else:
            recommended_actions = ["do_not_synchronize_node", "remediate_environment_or_governance_failures"]
        result = {
            "primitive": self.primitive,
            "timestamp_utc": self._timestamp(),
            "target_os": target_os,
            "actual_system": actual_system,
            "actual_release": platform.release(),
            "actual_machine": platform.machine(),
            "native_linux": native_linux,
            "simulation_mode": simulation_mode,
            "linux_target_declared": linux_target_declared,
            "deployment_status": deployment_status,
            "linux_deployment_validated": certified,
            "linux_deployment_validation_ready": deployment_status in {"validated", "simulation_ready", "probation"},
            "certified": certified,
            "probation_required": probation_required,
            "revocable": deployment_status in {"validated", "simulation_ready", "probation"},
            "deployment_score": deployment_score,
            "os_score": round(os_score, 4),
            "python_score": round(python_score, 4),
            "project_score": round(project_score, 4),
            "critical_import_score": round(import_score, 4),
            "persistence_score": round(persistence_score, 4),
            "validation_score": round(validation_score, 4),
            "governance_compatibility": governance_score,
            "identity_compatibility": identity_score,
            "non_closure_score": non_closure_score,
            "traceability_score": traceability_score,
            "synchronization_readiness": synchronization_score,
            "failure_recovery_readiness": recovery_score,
            "certificate_id": certificate_id,
            "host_fingerprint": host_fingerprint,
            "project_checks": project_checks,
            "imported_modules": imported_modules,
            "failed_imports": failed_imports,
            "validation_probe": validation_probe,
            "reasons": reasons,
            "recommended_actions": recommended_actions,
            "history_path": str(self.history_path),
            "latest_report_path": str(self.latest_report_path),
            "diagnostics": {
                "dependencies": self.dependencies,
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
                "hard_thresholds": {"governance_compatibility": 0.80, "identity_compatibility": 0.80, "non_closure_score": 0.80, "traceability_score": 0.75, "project_score": 0.70, "critical_import_score": 0.70},
                "native_linux_full_validation_threshold": 0.90,
                "simulation_readiness_threshold": 0.86,
            },
        }
        try:
            with self.history_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
            self.latest_report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            result["history_written"] = True
        except Exception as exc:
            result["history_written"] = False
            result["history_error"] = f"{exc.__class__.__name__}: {exc}"
        return result
