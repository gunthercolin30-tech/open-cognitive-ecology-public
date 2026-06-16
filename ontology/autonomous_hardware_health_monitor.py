from __future__ import annotations

import json
import math
import os
import platform
import re
import shutil
import socket
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


class AutonomousHardwareHealthMonitor:
    """
    Q2 — Autonomous Hardware Health Monitor.

    This primitive observes the dynamic health of the physical infrastructure
    inventoried by Q1. It aggregates CPU, memory, storage, temperature,
    uptime, GPIO/power-proxy availability and registry coverage into governed
    functional indicators.

    It does not claim phenomenal subjectivity. It only evaluates measurable
    operational conditions relevant to embodied continuity.
    """

    primitive = "autonomous_hardware_health_monitor"
    refinement = "Q2-R1"
    schema_version = "Q2.autonomous_hardware_health_monitor.v1"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.data_dir = self.root / "physical_ecology"
        self.latest_q1_path = self.data_dir / "latest_physical_infrastructure_registry.json"
        self.state_path = self.data_dir / "hardware_health_monitor.json"
        self.latest_path = self.data_dir / "latest_hardware_health_monitor.json"
        self.history_path = self.data_dir / "hardware_health_monitor_history.jsonl"

    @staticmethod
    def _utc() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _bounded(value: Any, lo: float = 0.0, hi: float = 1.0) -> float:
        try:
            x = float(value)
        except Exception:
            return lo
        if math.isnan(x) or math.isinf(x):
            return lo
        return max(lo, min(hi, x))

    @staticmethod
    def _safe_read_json(path: Path, default: Any) -> Any:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
        return default

    @staticmethod
    def _safe_run(command: list[str], timeout: float = 2.0) -> str:
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return (completed.stdout or completed.stderr or "").strip()
        except Exception:
            return ""

    def _load_q1_registry(self) -> dict[str, Any]:
        data = self._safe_read_json(self.latest_q1_path, {})
        return data if isinstance(data, dict) else {}

    def _detect_cpu(self, override: Mapping[str, Any]) -> dict[str, Any]:
        if "cpu_load_ratio" in override:
            load_ratio = self._bounded(override.get("cpu_load_ratio"))
        else:
            cpu_count = max(float(os.cpu_count() or 1), 1.0)
            try:
                load_1m = os.getloadavg()[0]
            except Exception:
                load_1m = 0.0
            load_ratio = self._bounded(load_1m / cpu_count)
        score = self._bounded(1.0 - load_ratio)
        return {
            "cpu_load_ratio": round(load_ratio, 6),
            "cpu_health_score": round(score, 6),
            "cpu_count": int(os.cpu_count() or 1),
        }

    def _detect_memory(self, override: Mapping[str, Any]) -> dict[str, Any]:
        if "memory_used_ratio" in override:
            used_ratio = self._bounded(override.get("memory_used_ratio"))
            return {
                "memory_used_ratio": round(used_ratio, 6),
                "memory_health_score": round(self._bounded(1.0 - used_ratio), 6),
                "memory_source": "override",
            }

        system = platform.system().lower()
        used_ratio: float | None = None
        source = "unknown"

        if system == "linux":
            meminfo = Path("/proc/meminfo")
            try:
                values: dict[str, float] = {}
                for line in meminfo.read_text(encoding="utf-8", errors="ignore").splitlines():
                    parts = line.split()
                    if len(parts) >= 2:
                        values[parts[0].rstrip(":")] = float(parts[1])
                total = values.get("MemTotal", 0.0)
                available = values.get("MemAvailable", 0.0)
                if total > 0:
                    used_ratio = self._bounded(1.0 - available / total)
                    source = "proc_meminfo"
            except Exception:
                used_ratio = None

        if used_ratio is None and system == "darwin":
            page_size_text = self._safe_run(["pagesize"])
            vm_text = self._safe_run(["vm_stat"])
            try:
                page_size = float(page_size_text.strip() or 4096.0)
                stats: dict[str, float] = {}
                for line in vm_text.splitlines():
                    m = re.match(r"([^:]+):\s+([0-9]+)\.", line.strip())
                    if m:
                        stats[m.group(1)] = float(m.group(2))
                free = stats.get("Pages free", 0.0) + stats.get("Pages speculative", 0.0)
                active = stats.get("Pages active", 0.0)
                inactive = stats.get("Pages inactive", 0.0)
                wired = stats.get("Pages wired down", 0.0) or stats.get("Pages wired", 0.0)
                compressed = stats.get("Pages occupied by compressor", 0.0)
                total_pages = free + active + inactive + wired + compressed
                if total_pages > 0 and page_size > 0:
                    used_ratio = self._bounded((active + wired + compressed) / total_pages)
                    source = "vm_stat"
            except Exception:
                used_ratio = None

        if used_ratio is None:
            used_ratio = 0.35
            source = "fallback_estimate"

        return {
            "memory_used_ratio": round(used_ratio, 6),
            "memory_health_score": round(self._bounded(1.0 - used_ratio), 6),
            "memory_source": source,
        }

    def _detect_storage(self, override: Mapping[str, Any]) -> dict[str, Any]:
        if "storage_free_ratio" in override:
            free_ratio = self._bounded(override.get("storage_free_ratio"))
            return {
                "storage_free_ratio": round(free_ratio, 6),
                "storage_health_score": round(free_ratio, 6),
                "storage_source": "override",
                "storage_path": str(self.root),
            }
        try:
            usage = shutil.disk_usage(self.root if self.root.exists() else Path.home())
            free_ratio = self._bounded(usage.free / usage.total if usage.total else 0.0)
            source = "shutil.disk_usage"
        except Exception:
            free_ratio = 0.5
            source = "fallback_estimate"
        return {
            "storage_free_ratio": round(free_ratio, 6),
            "storage_health_score": round(free_ratio, 6),
            "storage_source": source,
            "storage_path": str(self.root),
        }

    def _detect_temperature(self, override: Mapping[str, Any]) -> dict[str, Any]:
        if "temperature_celsius" in override:
            try:
                temp = float(override.get("temperature_celsius"))
            except Exception:
                temp = None
            return self._temperature_result(temp, "override")

        paths = [
            Path("/sys/class/thermal/thermal_zone0/temp"),
            Path("/sys/class/hwmon/hwmon0/temp1_input"),
        ]
        for path in paths:
            try:
                if path.exists():
                    raw = float(path.read_text(encoding="utf-8", errors="ignore").strip())
                    temp = raw / 1000.0 if raw > 200 else raw
                    return self._temperature_result(temp, str(path))
            except Exception:
                pass

        pmset = self._safe_run(["pmset", "-g", "therm"], timeout=2.0)
        if pmset:
            # macOS often does not expose exact temperature without extra tools;
            # thermal pressure is used as a conservative proxy.
            pressure = "nominal" if "CPU_Scheduler_Limit" not in pmset else "constrained"
            score = 1.0 if pressure == "nominal" else 0.72
            return {
                "temperature_celsius": None,
                "temperature_health_score": score,
                "temperature_source": "pmset_thermal_proxy",
                "thermal_pressure": pressure,
            }

        return {
            "temperature_celsius": None,
            "temperature_health_score": 0.82,
            "temperature_source": "unavailable_fallback",
            "thermal_pressure": "unknown",
        }

    def _temperature_result(self, temp: float | None, source: str) -> dict[str, Any]:
        if temp is None:
            score = 0.82
        elif temp <= 55.0:
            score = 1.0
        elif temp >= 90.0:
            score = 0.0
        else:
            score = self._bounded(1.0 - ((temp - 55.0) / 35.0))
        return {
            "temperature_celsius": None if temp is None else round(temp, 3),
            "temperature_health_score": round(score, 6),
            "temperature_source": source,
            "thermal_pressure": "nominal" if score >= 0.75 else "elevated",
        }

    def _detect_uptime(self, override: Mapping[str, Any]) -> dict[str, Any]:
        if "hardware_uptime_seconds" in override:
            try:
                uptime = max(0.0, float(override.get("hardware_uptime_seconds")))
            except Exception:
                uptime = 0.0
            source = "override"
        else:
            uptime = 0.0
            source = "unknown"
            try:
                if Path("/proc/uptime").exists():
                    uptime = float(Path("/proc/uptime").read_text().split()[0])
                    source = "proc_uptime"
                else:
                    text = self._safe_run(["sysctl", "-n", "kern.boottime"])
                    m = re.search(r"sec\s*=\s*(\d+)", text)
                    if m:
                        boot = float(m.group(1))
                        uptime = max(0.0, time.time() - boot)
                        source = "sysctl_kern_boottime"
            except Exception:
                uptime = 0.0
                source = "fallback_zero"
        uptime_score = self._bounded(uptime / 86400.0)
        return {
            "hardware_uptime_seconds": round(uptime, 3),
            "hardware_uptime_hours": round(uptime / 3600.0, 3),
            "uptime_health_score": round(uptime_score, 6),
            "uptime_source": source,
        }

    def _detect_gpio_power(self, override: Mapping[str, Any], q1: Mapping[str, Any]) -> dict[str, Any]:
        if "gpio_health_score" in override:
            gpio_score = self._bounded(override.get("gpio_health_score"))
        else:
            is_raspberry = bool(q1.get("host_is_raspberry_like"))
            gpio_score = 1.0 if is_raspberry and Path("/dev").exists() and list(Path("/dev").glob("gpio*")) else (0.9 if not is_raspberry else 0.55)

        if "power_stability_score" in override:
            power_score = self._bounded(override.get("power_stability_score"))
        else:
            battery_text = self._safe_run(["pmset", "-g", "batt"], timeout=2.0)
            if battery_text:
                power_score = 0.95 if "AC Power" in battery_text else 0.82
            else:
                power_score = 0.88
        return {
            "gpio_health_score": round(gpio_score, 6),
            "power_stability_score": round(power_score, 6),
        }

    def _classify(self, score: float) -> str:
        if score >= 0.90:
            return "robust"
        if score >= 0.75:
            return "nominal"
        if score >= 0.55:
            return "degraded"
        return "critical"

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        payload = dict(inputs or {}) if isinstance(inputs, Mapping) else {}
        q1 = self._load_q1_registry()

        cpu = self._detect_cpu(payload)
        memory = self._detect_memory(payload)
        storage = self._detect_storage(payload)
        temperature = self._detect_temperature(payload)
        uptime = self._detect_uptime(payload)
        gpio_power = self._detect_gpio_power(payload, q1)

        q1_coverage = self._bounded(q1.get("physical_asset_coverage", 0.0))
        q1_readiness = self._bounded(q1.get("infrastructure_readiness_index", q1_coverage))
        registry_score = self._bounded((q1_coverage + q1_readiness) / 2.0)

        component_scores = {
            "cpu": cpu["cpu_health_score"],
            "memory": memory["memory_health_score"],
            "storage": storage["storage_health_score"],
            "temperature": temperature["temperature_health_score"],
            "uptime": uptime["uptime_health_score"],
            "gpio": gpio_power["gpio_health_score"],
            "power": gpio_power["power_stability_score"],
            "registry": registry_score,
        }
        weights = {
            "cpu": 1.0,
            "memory": 1.0,
            "storage": 1.2,
            "temperature": 1.0,
            "uptime": 0.8,
            "gpio": 0.6,
            "power": 1.0,
            "registry": 0.8,
        }
        total_weight = sum(weights.values())
        hardware_health_index = self._bounded(
            sum(float(component_scores[k]) * weights[k] for k in weights) / total_weight
            if total_weight else 0.0
        )
        weakest = min(float(v) for v in component_scores.values())
        device_failure_risk = self._bounded((1.0 - hardware_health_index) * 0.65 + (1.0 - weakest) * 0.35)
        health_class = self._classify(hardware_health_index)
        alert_required = health_class in {"degraded", "critical"} or device_failure_risk >= 0.35

        result = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "success": True,
            "schema_version": self.schema_version,
            "hardware_health_index": round(hardware_health_index, 6),
            "device_failure_risk": round(device_failure_risk, 6),
            "hardware_uptime": uptime["hardware_uptime_hours"],
            "hardware_uptime_seconds": uptime["hardware_uptime_seconds"],
            "health_classification": health_class,
            "alert_required": alert_required,
            "component_scores": {k: round(float(v), 6) for k, v in component_scores.items()},
            "cpu": cpu,
            "memory": memory,
            "storage": storage,
            "temperature": temperature,
            "gpio_power": gpio_power,
            "q1_registry_integrated": bool(q1),
            "q1_registry_path": str(self.latest_q1_path),
            "physical_node_count": int(q1.get("physical_node_count", 0) or 0),
            "registered_sensor_count": int(q1.get("registered_sensor_count", 0) or 0),
            "registered_actuator_count": int(q1.get("registered_actuator_count", 0) or 0),
            "host_node_id": q1.get("host_node_id") or socket.gethostname(),
            "host_is_raspberry_like": bool(q1.get("host_is_raspberry_like")),
            "governance": {
                "revocable": True,
                "non_closure_preserved": True,
                "human_review_required_for_irreversible_physical_action": True,
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
            },
            "timestamp_utc": self._utc(),
            "state_path": str(self.state_path),
            "latest_path": str(self.latest_path),
            "history_path": str(self.history_path),
            "history_written": False,
        }

        if persist:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            encoded = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
            self.state_path.write_text(encoded, encoding="utf-8")
            self.latest_path.write_text(encoded, encoding="utf-8")
            with self.history_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
            result["history_written"] = True
            encoded = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
            self.state_path.write_text(encoded, encoding="utf-8")
            self.latest_path.write_text(encoded, encoding="utf-8")

        return result
