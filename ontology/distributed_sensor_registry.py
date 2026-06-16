from __future__ import annotations

import hashlib
import json
import math
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping


class DistributedSensorRegistry:
    primitive = "distributed_sensor_registry"
    refinement = "G5-R1-FIX1"

    SENSOR_ALIASES = {
        "temp": "temperature",
        "temperature_c": "temperature",
        "hum": "humidity",
        "lux": "light",
        "illumination": "light",
        "gpio_pin": "gpio",
        "button_pressed": "button",
        "relay_state": "relay",
    }

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.registry_dir = self.root / "physical_sensors"
        self.registry_path = self.registry_dir / "distributed_sensor_registry.json"
        self.history_path = self.registry_dir / "distributed_sensor_registry_history.jsonl"
        self.latest_path = self.registry_dir / "latest_distributed_sensor_registry.json"

    @staticmethod
    def _utc() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _bounded(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        if math.isnan(value) or math.isinf(value):
            return lo
        return max(lo, min(hi, float(value)))

    @classmethod
    def _normalize_kind(cls, kind: str) -> str:
        k = str(kind).strip().lower().replace(" ", "_").replace("-", "_")
        return cls.SENSOR_ALIASES.get(k, k)

    @classmethod
    def normalize_sensors(cls, sensors: Any) -> Dict[str, Any]:
        if sensors is None:
            return {}
        if isinstance(sensors, Mapping):
            out: Dict[str, Any] = {}
            for key, value in sensors.items():
                out[cls._normalize_kind(str(key))] = value
            return out
        if isinstance(sensors, list):
            out = {}
            for item in sensors:
                if isinstance(item, Mapping):
                    kind = item.get("kind") or item.get("name") or item.get("sensor")
                    if kind:
                        out[cls._normalize_kind(str(kind))] = item.get("value", item.get("active", True))
            return out
        return {}

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

    @staticmethod
    def _node_fingerprint(node_id: str, sensors: Mapping[str, Any]) -> str:
        payload = json.dumps({"node_id": node_id, "sensors": sorted(map(str, sensors.keys()))}, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]

    def _load_registry(self) -> Dict[str, Any]:
        if not self.registry_path.exists():
            return {"nodes": {}, "schema_version": "G5.distributed_sensor_registry.v1"}
        try:
            data = json.loads(self.registry_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return {"nodes": {}, "schema_version": "G5.distributed_sensor_registry.v1"}
            data.setdefault("nodes", {})
            return data
        except Exception:
            return {"nodes": {}, "schema_version": "G5.distributed_sensor_registry.v1", "recovered_from_invalid_json": True}

    def step(self, payload: Any = None, persist: bool = True, **kwargs: Any) -> Dict[str, Any]:
        if payload is None:
            payload = {}
        if not isinstance(payload, Mapping):
            payload = {"sensors": payload}
        data = dict(payload)
        data.update(kwargs)

        node_id = str(data.get("node_id") or data.get("host_id") or socket.gethostname() or "local-node")
        node_name = str(data.get("node_name") or node_id)
        sensors = self.normalize_sensors(data.get("sensors") or data.get("simulated_sensors") or data.get("readings"))
        sensor_count = len(sensors)
        active_sensor_kinds = sorted([k for k, v in sensors.items() if self._is_active(v)])
        active_sensor_count = len(active_sensor_kinds)
        canonical_slots = {"temperature", "humidity", "light", "button", "relay", "gpio"}
        sensor_diversity_index = self._bounded(len(set(sensors) & canonical_slots) / len(canonical_slots))

        registry = self._load_registry()
        registry["updated_at_utc"] = self._utc()
        registry.setdefault("nodes", {})[node_id] = {
            "node_id": node_id,
            "node_name": node_name,
            "sensor_count": sensor_count,
            "active_sensor_count": active_sensor_count,
            "active_sensor_kinds": active_sensor_kinds,
            "sensor_kinds": sorted(sensors.keys()),
            "sensor_diversity_index": sensor_diversity_index,
            "last_seen_utc": self._utc(),
            "fingerprint": self._node_fingerprint(node_id, sensors),
            "revocable": True,
            "functional_validation_only": True,
        }

        distributed_sensor_node_count = len(registry.get("nodes", {}))
        total_sensor_count = sum(int(n.get("sensor_count", 0)) for n in registry.get("nodes", {}).values())
        total_active_sensor_count = sum(int(n.get("active_sensor_count", 0)) for n in registry.get("nodes", {}).values())

        result = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "success": True,
            "node_id": node_id,
            "node_name": node_name,
            "sensor_count": sensor_count,
            "active_sensor_count": active_sensor_count,
            "active_sensor_kinds": active_sensor_kinds,
            "sensor_diversity_index": sensor_diversity_index,
            "distributed_sensor_node_count": distributed_sensor_node_count,
            "distributed_total_sensor_count": total_sensor_count,
            "distributed_active_sensor_count": total_active_sensor_count,
            "registry_path": str(self.registry_path),
            "history_path": str(self.history_path),
            "latest_path": str(self.latest_path),
            "revocable": True,
            "phenomenal_subjectivity_claimed": False,
            "timestamp_utc": self._utc(),
        }

        if persist:
            self.registry_dir.mkdir(parents=True, exist_ok=True)
            self.registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            self.latest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
            result["history_written"] = True
        else:
            result["history_written"] = False

        return result


if __name__ == "__main__":
    print(json.dumps(DistributedSensorRegistry().step({"sensors": {"temperature": 21.0, "light": 0.7}}, persist=False), ensure_ascii=False, indent=2))
