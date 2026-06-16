from __future__ import annotations

import json
import math
import os
import platform
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


class RaspberrySensorGateway:
    primitive = "raspberry_sensor_gateway"
    refinement = "G5-R1-FIX1"

    CANONICAL_SENSOR_KINDS = ["temperature", "humidity", "light", "button", "relay", "gpio"]

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.data_dir = self.root / "physical_sensors" / "raspberry_gateway"
        self.history_path = self.data_dir / "raspberry_sensor_gateway_history.jsonl"
        self.latest_path = self.data_dir / "latest_raspberry_sensor_gateway.json"

    @staticmethod
    def _utc() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _bounded(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        if math.isnan(value) or math.isinf(value):
            return lo
        return max(lo, min(hi, float(value)))

    @staticmethod
    def _is_active(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, Mapping):
            return bool(value.get("active", True))
        return True

    @classmethod
    def _normalize_sensors(cls, sensors: Any) -> Dict[str, Any]:
        aliases = {
            "temp": "temperature",
            "temperature_c": "temperature",
            "hum": "humidity",
            "lux": "light",
            "illumination": "light",
            "button_pressed": "button",
            "relay_state": "relay",
            "gpio_pin": "gpio",
        }
        if sensors is None:
            return {}
        if isinstance(sensors, Mapping):
            out: Dict[str, Any] = {}
            for key, value in sensors.items():
                k = str(key).strip().lower().replace(" ", "_").replace("-", "_")
                out[aliases.get(k, k)] = value
            return out
        if isinstance(sensors, list):
            out = {}
            for item in sensors:
                if isinstance(item, Mapping):
                    kind = item.get("kind") or item.get("name") or item.get("sensor")
                    if kind:
                        k = str(kind).strip().lower().replace(" ", "_").replace("-", "_")
                        out[aliases.get(k, k)] = item.get("value", item.get("active", True))
            return out
        return {}

    def _detect_hardware(self) -> Dict[str, Any]:
        dev = Path("/dev")
        entries = []
        if dev.exists():
            for pattern in ("gpio*", "i2c*", "spi*"):
                entries.extend([p.name for p in dev.glob(pattern)])
        machine = platform.machine().lower()
        system = platform.system().lower()
        is_arm = "arm" in machine or "aarch64" in machine
        return {
            "system": system,
            "machine": machine,
            "hostname": socket.gethostname(),
            "is_arm_like": is_arm,
            "gpio_like_devices": sorted(set(entries)),
            "gpio_device_count": len(set(entries)),
            "raspberry_candidate": is_arm and system == "linux",
            "hardware_detection_non_blocking": True,
        }

    def _publish_registry(self, node_id: str, node_name: str, sensors: Mapping[str, Any], persist: bool) -> Dict[str, Any]:
        try:
            from ontology.distributed_sensor_registry import DistributedSensorRegistry
            return DistributedSensorRegistry(self.root).step({"node_id": node_id, "node_name": node_name, "sensors": dict(sensors)}, persist=persist)
        except Exception as exc:
            return {"success": False, "error": repr(exc), "primitive": "distributed_sensor_registry"}

    def _publish_multimodal(self, sensors: Mapping[str, Any], persist: bool) -> Dict[str, Any]:
        try:
            from ontology.multimodal_perception_engine import MultimodalPerceptionEngine
            return MultimodalPerceptionEngine(self.root).step({"sensor": dict(sensors)}, persist=persist)
        except Exception as exc:
            return {"success": False, "error": repr(exc), "primitive": "multimodal_perception_engine"}

    def step(self, payload: Any = None, persist: bool = True, **kwargs: Any) -> Dict[str, Any]:
        if payload is None:
            payload = {}
        if not isinstance(payload, Mapping):
            payload = {"simulated_sensors": payload}
        data = dict(payload)
        data.update(kwargs)

        node_id = str(data.get("node_id") or socket.gethostname() or "raspberry-node")
        node_name = str(data.get("node_name") or node_id)
        hardware = self._detect_hardware()
        sensors = self._normalize_sensors(data.get("simulated_sensors") or data.get("sensors") or data.get("readings"))

        if data.get("detect_gpio_presence", True) and hardware["gpio_device_count"] > 0 and "gpio" not in sensors:
            sensors["gpio"] = True

        sensor_count = len(sensors)
        active_sensor_kinds = sorted([k for k, v in sensors.items() if self._is_active(v)])
        active_sensor_count = len(active_sensor_kinds)
        sensor_diversity_index = self._bounded(len(set(sensors) & set(self.CANONICAL_SENSOR_KINDS)) / len(self.CANONICAL_SENSOR_KINDS))
        gateway_operational_score = self._bounded((0.35 if hardware["raspberry_candidate"] else 0.15) + 0.65 * sensor_diversity_index)
        registry_publish = self._publish_registry(node_id, node_name, sensors, persist=persist)
        multimodal_publish = {"success": False, "skipped": True}
        if data.get("publish_to_multimodal", True):
            multimodal_publish = self._publish_multimodal(sensors, persist=persist)

        result = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "success": True,
            "node_id": node_id,
            "node_name": node_name,
            "sensor_count": sensor_count,
            "active_sensor_count": active_sensor_count,
            "active_sensor_kinds": active_sensor_kinds,
            "sensor_readings": sensors,
            "sensor_diversity_index": sensor_diversity_index,
            "gateway_operational_score": gateway_operational_score,
            "hardware_detection": hardware,
            "registry_publish": registry_publish,
            "multimodal_publish": multimodal_publish,
            "history_path": str(self.history_path),
            "latest_path": str(self.latest_path),
            "functional_validation_only": True,
            "phenomenal_subjectivity_claimed": False,
            "timestamp_utc": self._utc(),
        }

        if persist:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.latest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
            result["history_written"] = True
        else:
            result["history_written"] = False

        return result


if __name__ == "__main__":
    print(json.dumps(RaspberrySensorGateway().step({"simulated_sensors": {"temperature": 21.0, "light": 0.7}}, persist=False), ensure_ascii=False, indent=2))
