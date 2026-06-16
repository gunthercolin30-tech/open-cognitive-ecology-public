from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import glob
import json
import os
import platform
import shutil
import socket
import subprocess

PRIMITIVE = "embodied_world_interface"
REFINEMENT = "G1-R1"

DEPENDENCIES = [
    "embodiment",
    "embodied_sensorimotor_ecology",
    "embodied_planning_engine",
    "autonomous_capability_discovery",
    "node_capability_registry",
    "distributed_runtime_coordination",
    "metrics_history_recorder",
    "civilizational_storage_router",
    "preventive_growth_producer_routing",
    "constraint_monitoring_system",
    "governance_consistency_checker",
    "constitutional_alert_system",
    "openness_preservation_supervisor",
    "anti_closure_metaconstraint",
]

INTERFACE_KINDS = [
    "camera",
    "microphone",
    "speakers",
    "gpio",
    "usb",
    "network",
    "physical_api",
]


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = default
    if number != number or number in (float("inf"), float("-inf")):
        return default
    return max(0.0, min(1.0, number))


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _command_output(command: List[str], timeout: float = 2.0) -> str:
    try:
        completed = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
        )
        return completed.stdout or ""
    except Exception:
        return ""


class EmbodiedWorldInterface:
    """
    G1 — Embodied World Interface Foundation.

    Discovers physical and quasi-physical interfaces available to the local
    civilizational node without requiring privileged access or mandatory third
    party libraries. Detection is passive by default: it observes capabilities,
    records traceable evidence, and does not actuate the physical world.
    """

    primitive = PRIMITIVE
    refinement = REFINEMENT
    dependencies = DEPENDENCIES

    def __init__(self, root: Optional[str | Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "embodied_world_interface"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.state_dir / "embodied_world_state.json"
        self.history_path = self.state_dir / "interface_discovery_history.jsonl"

    def _load_state(self) -> Dict[str, Any]:
        if self.state_path.exists():
            try:
                data = json.loads(self.state_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        return {
            "interaction_cycles": 0,
            "sensor_observations": 0,
            "actions_executed": 0,
            "environment_updates": 0,
            "physical_interfaces_detected_total": 0,
            "physical_interfaces_active_total": 0,
            "interface_discovery_cycles": 0,
        }

    def _save_state(self, state: Dict[str, Any]) -> None:
        self.state_path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )

    def _append_history(self, record: Dict[str, Any]) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def _detect_camera(self) -> Dict[str, Any]:
        evidence: List[str] = []
        system = platform.system().lower()
        if system == "linux":
            devices = sorted(glob.glob("/dev/video*"))
            evidence.extend(devices[:10])
        elif system == "darwin":
            out = _command_output(["system_profiler", "SPCameraDataType"], timeout=3.0)
            if out.strip() and "No video capture devices" not in out:
                lines = [line.strip() for line in out.splitlines() if line.strip()]
                evidence.extend(lines[:8])
        env_hint = os.environ.get("OCE_CAMERA_DEVICE")
        if env_hint:
            evidence.append(f"env:OCE_CAMERA_DEVICE={env_hint}")
        return self._interface_record("camera", evidence, active=bool(evidence), confidence=0.75 if evidence else 0.25)

    def _detect_audio(self) -> Dict[str, Dict[str, Any]]:
        microphone_evidence: List[str] = []
        speaker_evidence: List[str] = []
        system = platform.system().lower()
        if system == "darwin":
            out = _command_output(["system_profiler", "SPAudioDataType"], timeout=3.0)
            lowered = out.lower()
            if "input" in lowered or "microphone" in lowered:
                microphone_evidence.extend([line.strip() for line in out.splitlines() if line.strip()][:8])
            if "output" in lowered or "speaker" in lowered:
                speaker_evidence.extend([line.strip() for line in out.splitlines() if line.strip()][:8])
        elif system == "linux":
            if Path("/proc/asound").exists():
                cards = sorted(glob.glob("/proc/asound/card*"))
                if cards:
                    microphone_evidence.extend(cards[:8])
                    speaker_evidence.extend(cards[:8])
            if shutil.which("arecord"):
                microphone_evidence.append("command:arecord")
            if shutil.which("aplay"):
                speaker_evidence.append("command:aplay")
        if os.environ.get("OCE_MICROPHONE_DEVICE"):
            microphone_evidence.append("env:OCE_MICROPHONE_DEVICE")
        if os.environ.get("OCE_SPEAKER_DEVICE"):
            speaker_evidence.append("env:OCE_SPEAKER_DEVICE")
        return {
            "microphone": self._interface_record("microphone", microphone_evidence, bool(microphone_evidence), 0.75 if microphone_evidence else 0.25),
            "speakers": self._interface_record("speakers", speaker_evidence, bool(speaker_evidence), 0.75 if speaker_evidence else 0.25),
        }

    def _detect_gpio(self) -> Dict[str, Any]:
        evidence: List[str] = []
        candidates = [Path("/sys/class/gpio"), Path("/dev/gpiomem")]
        evidence.extend(str(path) for path in candidates if path.exists())
        model_path = Path("/proc/device-tree/model")
        if model_path.exists():
            try:
                model = model_path.read_text(encoding="utf-8", errors="ignore").strip("\x00\n ")
                if "raspberry" in model.lower() or "gpio" in model.lower():
                    evidence.append(f"device_tree:{model}")
            except Exception:
                pass
        if os.environ.get("OCE_GPIO_ENABLED") in {"1", "true", "TRUE", "yes", "YES"}:
            evidence.append("env:OCE_GPIO_ENABLED")
        return self._interface_record("gpio", evidence, active=bool(evidence), confidence=0.8 if evidence else 0.2)

    def _detect_usb(self) -> Dict[str, Any]:
        evidence: List[str] = []
        system = platform.system().lower()
        if system == "linux":
            paths = sorted(glob.glob("/dev/bus/usb/*/*"))
            evidence.extend(paths[:12])
            if shutil.which("lsusb"):
                out = _command_output(["lsusb"], timeout=2.0)
                evidence.extend([line.strip() for line in out.splitlines() if line.strip()][:8])
        elif system == "darwin":
            out = _command_output(["system_profiler", "SPUSBDataType"], timeout=4.0)
            lines = [line.strip() for line in out.splitlines() if line.strip()]
            evidence.extend(lines[:12])
        return self._interface_record("usb", evidence, active=bool(evidence), confidence=0.75 if evidence else 0.25)

    def _detect_network(self) -> Dict[str, Any]:
        evidence: List[str] = []
        try:
            hostname = socket.gethostname()
            evidence.append(f"hostname:{hostname}")
            addresses = socket.getaddrinfo(hostname, None)
            ips = sorted({item[4][0] for item in addresses if item and item[4]})
            evidence.extend([f"ip:{ip}" for ip in ips[:8]])
        except Exception:
            pass
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.settimeout(0.25)
                sock.connect(("8.8.8.8", 80))
                evidence.append(f"default_route_ip:{sock.getsockname()[0]}")
        except Exception:
            pass
        return self._interface_record("network", evidence, active=bool(evidence), confidence=0.9 if evidence else 0.3)

    def _detect_physical_api(self) -> Dict[str, Any]:
        evidence: List[str] = []
        for key in sorted(os.environ):
            if key.startswith("OCE_PHYSICAL_API_") or key in {"OCE_RASPBERRY_PI_ENDPOINT", "OCE_SENSOR_GATEWAY_URL"}:
                evidence.append(f"env:{key}")
        api_registry = self.state_dir / "physical_api_registry.json"
        if api_registry.exists():
            evidence.append(str(api_registry))
        return self._interface_record("physical_api", evidence, active=bool(evidence), confidence=0.85 if evidence else 0.2)

    def _interface_record(self, kind: str, evidence: Iterable[str], active: bool, confidence: float) -> Dict[str, Any]:
        items = [str(item) for item in evidence if str(item).strip()]
        return {
            "kind": kind,
            "detected": bool(items),
            "active": bool(active and items),
            "evidence_count": len(items),
            "evidence_sample": items[:10],
            "confidence": _bounded(confidence),
        }

    def _merge_simulated_interfaces(self, interfaces: Dict[str, Dict[str, Any]], simulated: Any) -> None:
        if not isinstance(simulated, dict):
            return
        for kind in INTERFACE_KINDS:
            raw = simulated.get(kind)
            if isinstance(raw, dict):
                detected = bool(raw.get("detected", raw.get("active", False)))
                active = bool(raw.get("active", detected))
                evidence = raw.get("evidence", ["simulated_input"] if detected else [])
                confidence = _bounded(raw.get("confidence", 0.6 if detected else 0.2))
            else:
                detected = bool(raw)
                active = bool(raw)
                evidence = ["simulated_input"] if detected else []
                confidence = 0.6 if detected else 0.2
            if detected:
                previous = interfaces.get(kind, self._interface_record(kind, [], False, 0.0))
                merged_evidence = list(previous.get("evidence_sample", [])) + [str(x) for x in evidence]
                interfaces[kind] = self._interface_record(
                    kind=kind,
                    evidence=merged_evidence,
                    active=previous.get("active", False) or active,
                    confidence=max(float(previous.get("confidence", 0.0)), confidence),
                )

    def discover_interfaces(self, simulated_interfaces: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        interfaces: Dict[str, Dict[str, Any]] = {}
        interfaces["camera"] = self._detect_camera()
        interfaces.update(self._detect_audio())
        interfaces["gpio"] = self._detect_gpio()
        interfaces["usb"] = self._detect_usb()
        interfaces["network"] = self._detect_network()
        interfaces["physical_api"] = self._detect_physical_api()
        self._merge_simulated_interfaces(interfaces, simulated_interfaces)

        detected = [kind for kind, data in interfaces.items() if data.get("detected")]
        active = [kind for kind, data in interfaces.items() if data.get("active")]
        confidence_values = [float(data.get("confidence", 0.0)) for data in interfaces.values()]
        detection_coverage = len(detected) / len(INTERFACE_KINDS)
        activation_coverage = len(active) / len(INTERFACE_KINDS)
        interface_confidence_index = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0

        return {
            "timestamp_utc": _utc(),
            "interfaces": interfaces,
            "physical_interfaces_detected": len(detected),
            "physical_interfaces_active": len(active),
            "detected_interface_kinds": detected,
            "active_interface_kinds": active,
            "detection_coverage": round(detection_coverage, 6),
            "activation_coverage": round(activation_coverage, 6),
            "interface_confidence_index": round(interface_confidence_index, 6),
            "sensor_diversity_index": round(detection_coverage, 6),
            "discovery_mode": "passive_plus_optional_simulation" if simulated_interfaces else "passive_local_discovery",
        }

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        inputs = inputs or {}
        state = self._load_state()
        state["interaction_cycles"] = _safe_int(state.get("interaction_cycles")) + 1
        state["interface_discovery_cycles"] = _safe_int(state.get("interface_discovery_cycles")) + 1

        discovery = self.discover_interfaces(inputs.get("simulated_interfaces"))
        physical_interfaces_detected = int(discovery["physical_interfaces_detected"])
        physical_interfaces_active = int(discovery["physical_interfaces_active"])

        sensor_observations = max(0, _safe_int(inputs.get("sensor_observations", physical_interfaces_detected)))
        actions_executed = max(0, _safe_int(inputs.get("actions_executed", 0)))
        environment_updates = max(0, _safe_int(inputs.get("environment_updates", 1 if physical_interfaces_detected else 0)))

        state["sensor_observations"] = _safe_int(state.get("sensor_observations")) + sensor_observations
        state["actions_executed"] = _safe_int(state.get("actions_executed")) + actions_executed
        state["environment_updates"] = _safe_int(state.get("environment_updates")) + environment_updates
        state["physical_interfaces_detected_total"] = _safe_int(state.get("physical_interfaces_detected_total")) + physical_interfaces_detected
        state["physical_interfaces_active_total"] = _safe_int(state.get("physical_interfaces_active_total")) + physical_interfaces_active
        state["last_execution_utc"] = discovery["timestamp_utc"]
        state["latest_detected_interface_kinds"] = discovery["detected_interface_kinds"]
        state["latest_active_interface_kinds"] = discovery["active_interface_kinds"]

        sensor_reliability = _bounded(inputs.get("sensor_reliability", 0.96))
        actuator_precision = _bounded(inputs.get("actuator_precision", 0.95 if actions_executed else 0.80))
        environmental_awareness = _bounded(inputs.get("environmental_awareness", discovery["detection_coverage"]))
        safety_compliance = _bounded(inputs.get("safety_compliance", 0.99))
        feedback_quality = _bounded(inputs.get("feedback_quality", discovery["interface_confidence_index"]))

        embodied_operational_index = _bounded(
            0.20 * sensor_reliability
            + 0.15 * actuator_precision
            + 0.25 * environmental_awareness
            + 0.25 * safety_compliance
            + 0.15 * feedback_quality
        )
        physical_interface_readiness = _bounded(
            0.50 * discovery["detection_coverage"]
            + 0.30 * discovery["activation_coverage"]
            + 0.20 * discovery["interface_confidence_index"]
        )
        operational = embodied_operational_index >= 0.70 and physical_interfaces_detected > 0

        record = {
            "primitive": PRIMITIVE,
            "refinement": REFINEMENT,
            "timestamp_utc": discovery["timestamp_utc"],
            "physical_interfaces_detected": physical_interfaces_detected,
            "physical_interfaces_active": physical_interfaces_active,
            "detected_interface_kinds": discovery["detected_interface_kinds"],
            "active_interface_kinds": discovery["active_interface_kinds"],
            "physical_interface_readiness": round(physical_interface_readiness, 6),
            "embodied_operational_index": round(embodied_operational_index, 6),
            "operational": operational,
        }

        self._save_state(state)
        self._append_history(record)

        return {
            "primitive": "EMBODIED_WORLD_INTERFACE",
            "refinement": REFINEMENT,
            "interaction_cycles": state["interaction_cycles"],
            "interface_discovery_cycles": state["interface_discovery_cycles"],
            "sensor_observations": state["sensor_observations"],
            "actions_executed": state["actions_executed"],
            "environment_updates": state["environment_updates"],
            "physical_interfaces_detected": physical_interfaces_detected,
            "physical_interfaces_active": physical_interfaces_active,
            "detected_interface_kinds": discovery["detected_interface_kinds"],
            "active_interface_kinds": discovery["active_interface_kinds"],
            "interface_summary": discovery["interfaces"],
            "detection_coverage": discovery["detection_coverage"],
            "activation_coverage": discovery["activation_coverage"],
            "sensor_diversity_index": discovery["sensor_diversity_index"],
            "interface_confidence_index": discovery["interface_confidence_index"],
            "sensor_reliability": sensor_reliability,
            "actuator_precision": actuator_precision,
            "environmental_awareness": environmental_awareness,
            "safety_compliance": safety_compliance,
            "feedback_quality": feedback_quality,
            "physical_interface_readiness": round(physical_interface_readiness, 6),
            "embodied_operational_index": round(embodied_operational_index, 6),
            "operational": operational,
            "discovery_mode": discovery["discovery_mode"],
            "state_path": str(self.state_path),
            "history_path": str(self.history_path),
            "dependencies": DEPENDENCIES,
            "diagnostics": {
                "subjectivity_claim": "none",
                "validation_scope": "functional_physical_interface_discovery",
                "passive_detection_only": True,
                "non_closure_compliant": True,
                "traceable": True,
                "reversible": True,
            },
        }
