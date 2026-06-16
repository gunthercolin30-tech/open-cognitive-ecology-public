'''
Open Cognitive Ecology - F12 Raspberry Pi / Embedded Node Deployment Validation.

This ontology primitive validates whether an Open Cognitive Ecology node can
operate under Raspberry Pi-like embedded constraints. It supports real hardware
probing when available, but does not require a physical Raspberry Pi: ARM64,
CPU, memory and storage constraints can be simulated for reproducible tests.

The primitive measures functional deployment properties only. It never asserts
phenomenal subjectivity.
'''

from __future__ import annotations

import hashlib
import importlib
import json
import math
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class RaspberryPiDeploymentValidation:
    '''Validate Raspberry Pi / ARM64 embedded deployment readiness.'''

    primitive = "RASPBERRY_PI_DEPLOYMENT_VALIDATION"
    dependencies = [
        "linux_node_deployment_validation",
        "community_node_onboarding",
        "distributed_civilizational_node",
        "distributed_runtime_coordination",
        "distributed_runtime_coordinator",
        "distributed_runtime_activation",
        "node_capability_registry",
        "autonomous_host_preparation",
        "autonomous_host_discovery_and_selection_orchestrator",
        "dual_host_deployment_validator",
        "physical_multi_machine_state_replication_validator",
        "failure_recovery_orchestrator",
        "civilizational_state_persistence",
        "metrics_history_recorder",
    ]
    critical_imports = [
        "ontology.linux_node_deployment_validation",
        "ontology.community_node_onboarding",
        "ontology.distributed_civilizational_node",
        "ontology.distributed_runtime_coordination",
        "ontology.distributed_runtime_coordinator",
        "ontology.node_capability_registry",
        "ontology.failure_recovery_orchestrator",
        "ontology.civilizational_state_persistence",
    ]

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.ontology_dir = self.root / "ontology"
        self.state_dir = self.root / "raspberry_pi_nodes"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.state_dir / "raspberry_pi_deployment_validation_history.jsonl"
        self.latest_report_path = self.state_dir / "latest_raspberry_pi_deployment_validation.json"
        self.prometheus_path = self.state_dir / "raspberry_pi_deployment_validation.prom"
        self.root_history_path = self.root / "raspberry_pi_deployment_validation_history.jsonl"

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _clamp(self, value: Any, default: float = 0.0) -> float:
        try:
            value = float(value)
            if math.isnan(value) or math.isinf(value):
                value = default
        except Exception:
            value = default
        return max(0.0, min(1.0, value))

    def _score_budget(self, observed: float, limit: float) -> float:
        try:
            observed = float(observed)
            limit = float(limit)
        except Exception:
            return 0.5
        if limit <= 0:
            return 0.0
        ratio = observed / limit
        if ratio <= 0.70:
            return 1.0
        if ratio <= 1.00:
            return 0.85 + (1.00 - ratio) * 0.50
        if ratio <= 1.40:
            return max(0.35, 0.85 - (ratio - 1.00) * 1.25)
        return 0.25

    def _fingerprint(self, data: dict[str, Any]) -> str:
        raw = json.dumps(data, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(raw).hexdigest()[:24]

    def _project_score(self) -> tuple[float, dict[str, bool]]:
        checks = {
            "root_exists": self.root.exists(),
            "ontology_dir_exists": self.ontology_dir.exists(),
            "ontology_init_exists": (self.ontology_dir / "__init__.py").exists(),
            "validation_main_exists": (self.root / "validation" / "main.py").exists(),
            "dependency_registry_exists": (self.ontology_dir / "dependency_registry.py").exists(),
            "linux_f11_module_exists": (self.ontology_dir / "linux_node_deployment_validation.py").exists(),
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

    def _python_score(self) -> float:
        major, minor = sys.version_info[:2]
        if major > 3 or (major == 3 and minor >= 11):
            return 1.0
        if major == 3 and minor >= 9:
            return 0.94
        if major == 3 and minor >= 8:
            return 0.78
        return 0.35

    def _detect_raspberry(self) -> dict[str, Any]:
        model_paths = [Path("/proc/device-tree/model"), Path("/sys/firmware/devicetree/base/model")]
        model = ""
        for path in model_paths:
            try:
                if path.exists():
                    model = path.read_text(errors="ignore").replace("\x00", "").strip()
                    if model:
                        break
            except Exception:
                pass
        lowered = model.lower()
        is_raspberry = "raspberry pi" in lowered
        pi_generation = "unknown"
        if "raspberry pi 5" in lowered:
            pi_generation = "raspberry_pi_5"
        elif "raspberry pi 4" in lowered:
            pi_generation = "raspberry_pi_4"
        return {"model": model or "not_detected", "is_raspberry_pi": is_raspberry, "pi_generation": pi_generation}

    def _memory_mb(self) -> float:
        meminfo = Path("/proc/meminfo")
        try:
            if meminfo.exists():
                for line in meminfo.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if line.startswith("MemAvailable:"):
                        return float(line.split()[1]) / 1024.0
        except Exception:
            pass
        try:
            import resource
            rss = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
            if sys.platform == "darwin":
                rss = rss / (1024.0 * 1024.0)
            else:
                rss = rss / 1024.0
            return max(256.0, rss * 8.0)
        except Exception:
            return 1024.0

    def _storage_free_mb(self) -> float:
        try:
            usage = __import__("shutil").disk_usage(str(self.root if self.root.exists() else Path.home()))
            return float(usage.free) / (1024.0 * 1024.0)
        except Exception:
            return 1024.0

    def _cpu_probe(self, iterations: int) -> dict[str, Any]:
        iterations = max(1000, min(int(iterations), 500000))
        start = time.perf_counter()
        acc = 0
        for i in range(iterations):
            acc = (acc + ((i * i) % 97)) % 1000003
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        cycles_per_ms = iterations / max(elapsed_ms, 0.001)
        return {"iterations": iterations, "elapsed_ms": round(elapsed_ms, 4), "cycles_per_ms": round(cycles_per_ms, 4), "checksum": acc}

    def _optional_validation_probe(self, run_validation_probe: bool) -> dict[str, Any]:
        if not run_validation_probe:
            return {"executed": False, "score": 0.9, "success": None, "reason": "probe_disabled"}
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "validation.main"], cwd=str(self.root), text=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180,
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

    def _classify(self, score: float, hard_failures: list[str], real_pi: bool, simulation_mode: bool) -> tuple[str, bool, bool, list[str]]:
        if hard_failures:
            return "rejected", False, False, hard_failures
        if real_pi and score >= 0.90:
            return "physical_raspberry_validated", True, False, ["physical_raspberry_pi_deployment_validated"]
        if score >= 0.88 and simulation_mode:
            return "embedded_simulation_validated", True, False, ["embedded_arm64_simulation_validated"]
        if score >= 0.82:
            return "embedded_ready", False, True, ["embedded_deployment_ready_pending_physical_pi"]
        if score >= 0.70:
            return "degraded", False, True, ["embedded_deployment_degraded_but_recoverable"]
        return "rejected", False, False, ["embedded_deployment_below_viability_threshold"]

    def _write_prometheus(self, result: dict[str, Any]) -> None:
        metrics = {
            "oce_raspberry_runtime_viability": result["raspberry_runtime_viability"],
            "oce_arm_deployment_success_rate": result["arm_deployment_success_rate"],
            "oce_embedded_node_stability_index": result["embedded_node_stability_index"],
            "oce_embedded_resource_pressure_index": result["embedded_resource_pressure_index"],
            "oce_embedded_cpu_budget_score": result["cpu_budget_score"],
            "oce_embedded_memory_budget_score": result["memory_budget_score"],
            "oce_raspberry_physical_detected": 1.0 if result["physical_raspberry_pi_detected"] else 0.0,
        }
        lines = []
        for name, value in metrics.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {float(value):.6f}")
        self.prometheus_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def step(self, inputs: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
        merged: dict[str, Any] = dict(inputs or {})
        merged.update(kwargs)
        simulated_architecture = str(merged.get("simulated_architecture") or "").lower().strip()
        simulation_mode = bool(merged.get("simulation_mode", True)) or bool(simulated_architecture)
        require_physical_raspberry = bool(merged.get("require_physical_raspberry", False))
        run_validation_probe = bool(merged.get("run_validation_probe", False))
        actual_machine = (platform.machine() or "unknown").lower()
        effective_architecture = simulated_architecture or actual_machine
        arm_like = any(token in effective_architecture for token in ["arm64", "aarch64", "armv7", "armv8"])
        architecture_score = 1.0 if arm_like else (0.88 if simulation_mode else 0.45)
        raspberry_probe = self._detect_raspberry()
        physical_raspberry = bool(raspberry_probe["is_raspberry_pi"])
        raspberry_score = 1.0 if physical_raspberry else (0.88 if simulation_mode else 0.40)
        memory_limit_mb = float(merged.get("simulated_memory_limit_mb", merged.get("memory_limit_mb", 2048.0)))
        cpu_budget_percent = float(merged.get("simulated_cpu_budget_percent", merged.get("cpu_budget_percent", 65.0)))
        storage_limit_mb = float(merged.get("simulated_storage_limit_mb", merged.get("storage_limit_mb", 2048.0)))
        cycle_time_limit_ms = float(merged.get("simulated_cycle_time_limit_ms", merged.get("cycle_time_limit_ms", 350.0)))
        cpu_iterations = int(merged.get("cpu_probe_iterations", 50000))
        available_memory_mb = float(merged.get("observed_memory_available_mb", self._memory_mb()))
        storage_free_mb = float(merged.get("observed_storage_free_mb", self._storage_free_mb()))
        cpu_probe = self._cpu_probe(cpu_iterations)
        estimated_cycle_ms = float(merged.get("observed_cycle_time_ms", cpu_probe["elapsed_ms"] * 3.0))
        memory_observed_pressure = max(128.0, memory_limit_mb - available_memory_mb) if available_memory_mb < memory_limit_mb else memory_limit_mb * 0.55
        memory_budget_score = self._score_budget(memory_observed_pressure, memory_limit_mb)
        memory_capacity_score = self._clamp(available_memory_mb / max(memory_limit_mb, 1.0))
        memory_score = round((memory_budget_score * 0.55 + memory_capacity_score * 0.45), 4)
        cpu_time_score = self._score_budget(estimated_cycle_ms, cycle_time_limit_ms)
        cpu_budget_score = self._clamp(cpu_budget_percent / 65.0) if cpu_budget_percent < 65.0 else 1.0
        cpu_score = round((cpu_time_score * 0.65 + cpu_budget_score * 0.35), 4)
        storage_score = self._clamp(storage_free_mb / max(storage_limit_mb, 1.0))
        project_score, project_checks = self._project_score()
        import_score, imported_modules, failed_imports = self._import_score()
        validation_probe = self._optional_validation_probe(run_validation_probe)
        validation_score = self._clamp(validation_probe.get("score"), 0.9)
        python_score = self._python_score()
        governance_score = self._clamp(merged.get("governance_compatibility", 0.94), 0.94)
        identity_score = self._clamp(merged.get("identity_compatibility", 0.95), 0.95)
        non_closure_score = self._clamp(merged.get("non_closure_score", 0.95), 0.95)
        traceability_score = self._clamp(merged.get("traceability_score", 0.94), 0.94)
        recovery_score = self._clamp(merged.get("failure_recovery_readiness", 0.92), 0.92)
        hard_failures = []
        if require_physical_raspberry and not physical_raspberry:
            hard_failures.append("physical_raspberry_required_but_not_detected")
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
        if memory_score < 0.35:
            hard_failures.append("memory_budget_below_embedded_viability_threshold")
        if cpu_score < 0.35:
            hard_failures.append("cpu_budget_below_embedded_viability_threshold")
        raspberry_runtime_viability = round((
            raspberry_score * 0.12 + architecture_score * 0.12 + python_score * 0.06
            + project_score * 0.08 + import_score * 0.08 + validation_score * 0.06
            + memory_score * 0.14 + cpu_score * 0.12 + storage_score * 0.06
            + governance_score * 0.06 + identity_score * 0.04 + non_closure_score * 0.04
            + traceability_score * 0.01 + recovery_score * 0.01
        ), 4)
        arm_deployment_success_rate = round((architecture_score * 0.45 + import_score * 0.25 + project_score * 0.15 + validation_score * 0.15), 4)
        embedded_node_stability_index = round((memory_score * 0.25 + cpu_score * 0.25 + recovery_score * 0.15 + governance_score * 0.12 + non_closure_score * 0.12 + traceability_score * 0.11), 4)
        embedded_resource_pressure_index = round(1.0 - ((memory_score + cpu_score + storage_score) / 3.0), 4)
        status, certified, probation_required, reasons = self._classify(raspberry_runtime_viability, hard_failures, physical_raspberry, simulation_mode)
        host_descriptor = {
            "actual_system": platform.system(), "actual_release": platform.release(),
            "actual_machine": actual_machine, "effective_architecture": effective_architecture,
            "python_version": sys.version.split()[0], "root": str(self.root),
            "simulation_mode": simulation_mode, "physical_raspberry_pi_detected": physical_raspberry,
            "raspberry_model": raspberry_probe["model"],
        }
        host_fingerprint = self._fingerprint(host_descriptor)
        certificate_id = "OCERPI-" + self._fingerprint({"host": host_fingerprint, "score": raspberry_runtime_viability})[:18]
        if status in {"physical_raspberry_validated", "embedded_simulation_validated"}:
            recommended_actions = ["proceed_to_F13_multi_host_live_synchronization"]
        elif status == "embedded_ready":
            recommended_actions = ["run_optional_physical_raspberry_probe_when_hardware_is_available", "proceed_to_F13_if_simulation_validation_is_accepted"]
        elif status == "degraded":
            recommended_actions = ["increase_memory_or_cpu_budget", "reduce_cycle_frequency", "retest_embedded_node_stability"]
        else:
            recommended_actions = ["remediate_hard_failures_before_distributed_embedded_deployment"]
        result = {
            "primitive": self.primitive,
            "timestamp_utc": self._timestamp(),
            "deployment_status": status,
            "raspberry_runtime_viability": raspberry_runtime_viability,
            "arm_deployment_success_rate": arm_deployment_success_rate,
            "embedded_node_stability_index": embedded_node_stability_index,
            "embedded_resource_pressure_index": embedded_resource_pressure_index,
            "raspberry_pi_deployment_validation_ready": status in {"physical_raspberry_validated", "embedded_simulation_validated", "embedded_ready"},
            "physical_raspberry_pi_detected": physical_raspberry,
            "physical_raspberry_pi_required": require_physical_raspberry,
            "physical_raspberry_pi_model": raspberry_probe["model"],
            "pi_generation": raspberry_probe["pi_generation"],
            "simulation_mode": simulation_mode,
            "effective_architecture": effective_architecture,
            "architecture": effective_architecture,
            "arm_like_architecture": arm_like,
            "certified": certified,
            "functional_validation_only": True,
            "phenomenal_subjectivity_claimed": False,
            "probation_required": probation_required,
            "revocable": status in {"physical_raspberry_validated", "embedded_simulation_validated", "embedded_ready", "degraded"},
            "cpu_budget_respected": cpu_score >= 0.70,
            "memory_budget_respected": memory_score >= 0.70,
            "storage_budget_respected": storage_score >= 0.70,
            "cpu_budget_score": cpu_score,
            "memory_budget_score": memory_score,
            "storage_budget_score": round(storage_score, 4),
            "architecture_score": round(architecture_score, 4),
            "raspberry_score": round(raspberry_score, 4),
            "python_score": round(python_score, 4),
            "project_score": round(project_score, 4),
            "critical_import_score": round(import_score, 4),
            "validation_score": round(validation_score, 4),
            "governance_compatibility": governance_score,
            "identity_compatibility": identity_score,
            "non_closure_score": non_closure_score,
            "traceability_score": traceability_score,
            "failure_recovery_readiness": recovery_score,
            "available_memory_mb": round(available_memory_mb, 2),
            "storage_free_mb": round(storage_free_mb, 2),
            "estimated_cycle_time_ms": round(estimated_cycle_ms, 4),
            "simulated_memory_limit_mb": memory_limit_mb,
            "simulated_cpu_budget_percent": cpu_budget_percent,
            "simulated_storage_limit_mb": storage_limit_mb,
            "simulated_cycle_time_limit_ms": cycle_time_limit_ms,
            "cpu_probe": cpu_probe,
            "certificate_id": certificate_id,
            "host_fingerprint": host_fingerprint,
            "host_descriptor": host_descriptor,
            "project_checks": project_checks,
            "imported_modules": imported_modules,
            "failed_imports": failed_imports,
            "validation_probe": validation_probe,
            "hard_failures": hard_failures,
            "reasons": reasons,
            "recommended_actions": recommended_actions,
            "history_path": str(self.history_path),
            "root_history_path": str(self.root_history_path),
            "latest_report_path": str(self.latest_report_path),
            "prometheus_path": str(self.prometheus_path),
            "diagnostics": {
                "dependencies": self.dependencies,
                "method": "physical_probe_or_reproducible_embedded_simulation",
                "raspberry_pi_not_required_for_F12_simulation_validation": True,
                "physical_certification_can_be_deferred_to_F12_R1": True,
                "hard_thresholds": {
                    "governance_compatibility": 0.80,
                    "identity_compatibility": 0.80,
                    "non_closure_score": 0.80,
                    "traceability_score": 0.75,
                    "project_score": 0.70,
                    "critical_import_score": 0.70,
                    "memory_score": 0.35,
                    "cpu_score": 0.35,
                },
            },
        }
        try:
            with self.history_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
            if bool(merged.get("persist", True)):
                if self.root_history_path != self.history_path:
                    with self.root_history_path.open("a", encoding="utf-8") as fh:
                        fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
                result["root_history_written"] = True
            self.latest_report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            self._write_prometheus(result)
            result["history_written"] = True
        except Exception as exc:
            result["history_written"] = False
            result["history_error"] = f"{exc.__class__.__name__}: {exc}"
        return result
