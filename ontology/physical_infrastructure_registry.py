from __future__ import annotations

import json
import math
import os
import platform
import shutil
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


class PhysicalInfrastructureRegistry:
    """
    Q1 — Physical Infrastructure Registry.

    This primitive builds a governed, persistent inventory of the embodied
    physical infrastructure supporting Open Cognitive Ecology: host nodes,
    Raspberry-like devices, sensors, actuators, storage assets, cloud nodes
    and maintenance-relevant hardware state.

    It does not claim phenomenal subjectivity. It only records functional,
    measurable indicators of physical anchoring and infrastructure coverage.
    """

    primitive = "physical_infrastructure_registry"
    refinement = "Q1-R1"
    schema_version = "Q1.physical_infrastructure_registry.v1"

    SENSOR_KEYS = {
        "temperature", "humidity", "light", "button", "relay", "gpio",
        "camera", "microphone", "pressure", "motion", "distance", "voltage",
    }
    ACTUATOR_KEYS = {
        "relay", "led", "motor", "servo", "pump", "fan", "speaker",
        "gpio_output", "switch", "display",
    }

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.data_dir = self.root / "physical_ecology"
        self.registry_path = self.data_dir / "physical_infrastructure_registry.json"
        self.latest_path = self.data_dir / "latest_physical_infrastructure_registry.json"
        self.history_path = self.data_dir / "physical_infrastructure_registry_history.jsonl"

    @staticmethod
    def _utc() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _bounded(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        try:
            value = float(value)
        except Exception:
            return lo
        if math.isnan(value) or math.isinf(value):
            return lo
        return max(lo, min(hi, value))

    @staticmethod
    def _safe_read_json(path: Path, default: Any) -> Any:
        try:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return default
        return default

    @staticmethod
    def _normalize_mapping(value: Any) -> Dict[str, Any]:
        if isinstance(value, Mapping):
            return {str(k): v for k, v in value.items()}
        return {}

    @staticmethod
    def _normalize_list(value: Any) -> list[Dict[str, Any]]:
        if not isinstance(value, list):
            return []
        out: list[Dict[str, Any]] = []
        for item in value:
            if isinstance(item, Mapping):
                out.append({str(k): v for k, v in item.items()})
            else:
                out.append({"id": str(item), "kind": "unspecified"})
        return out

    @staticmethod
    def _run_text(command: list[str], timeout: float = 2.0) -> str:
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

    def _detect_host(self) -> Dict[str, Any]:
        machine = platform.machine().lower()
        system = platform.system().lower()
        release = platform.release()
        hostname = socket.gethostname() or "local-node"
        processor = platform.processor()
        is_arm_like = "arm" in machine or "aarch64" in machine
        is_raspberry_like = False
        model_text = ""
        model_path = Path("/proc/device-tree/model")
        try:
            if model_path.exists():
                model_text = model_path.read_text(errors="ignore").strip("\x00\n ")
                is_raspberry_like = "raspberry" in model_text.lower()
        except Exception:
            model_text = ""
        if not is_raspberry_like:
            is_raspberry_like = is_arm_like and system == "linux"

        cpu_count = os.cpu_count() or 1
        load_1m = 0.0
        try:
            load_1m = os.getloadavg()[0]
        except Exception:
            load_1m = 0.0
        cpu_headroom = self._bounded(1.0 - (load_1m / max(float(cpu_count), 1.0)))

        return {
            "node_id": hostname,
            "hostname": hostname,
            "system": system,
            "release": release,
            "machine": machine,
            "processor": processor,
            "cpu_count": cpu_count,
            "load_1m": round(load_1m, 4),
            "cpu_headroom": round(cpu_headroom, 6),
            "is_arm_like": is_arm_like,
            "is_raspberry_like": is_raspberry_like,
            "hardware_model": model_text,
            "detected_at_utc": self._utc(),
        }

    def _detect_storage(self) -> list[Dict[str, Any]]:
        candidates = [self.root, Path.home(), Path("/Volumes")]
        assets: list[Dict[str, Any]] = []
        seen: set[str] = set()
        for path in candidates:
            try:
                if not path.exists():
                    continue
                target = path if path.is_dir() else path.parent
                usage = shutil.disk_usage(target)
                key = str(target.resolve())
                if key in seen:
                    continue
                seen.add(key)
                total = int(usage.total)
                free = int(usage.free)
                used = int(usage.used)
                free_ratio = self._bounded(free / total if total else 0.0)
                assets.append({
                    "asset_id": key,
                    "kind": "storage",
                    "path": str(target),
                    "total_bytes": total,
                    "used_bytes": used,
                    "free_bytes": free,
                    "free_ratio": round(free_ratio, 6),
                    "available": True,
                    "external_candidate": str(target).startswith("/Volumes"),
                })
            except Exception as exc:
                assets.append({
                    "asset_id": str(path),
                    "kind": "storage",
                    "path": str(path),
                    "available": False,
                    "error": repr(exc),
                })
        return assets

    def _detect_gpio_devices(self) -> list[Dict[str, Any]]:
        dev = Path("/dev")
        out: list[Dict[str, Any]] = []
        if not dev.exists():
            return out
        for pattern in ("gpio*", "i2c*", "spi*"):
            for item in dev.glob(pattern):
                out.append({
                    "asset_id": str(item),
                    "kind": "gpio_bus" if item.name.startswith("gpio") else "hardware_bus",
                    "name": item.name,
                    "path": str(item),
                    "available": True,
                })
        return sorted(out, key=lambda x: x["asset_id"])

    def _load_distributed_sensor_registry(self) -> Dict[str, Any]:
        path = self.root / "physical_sensors" / "distributed_sensor_registry.json"
        return self._safe_read_json(path, {"nodes": {}})

    def _assets_from_sensor_registry(self) -> tuple[list[Dict[str, Any]], list[Dict[str, Any]]]:
        registry = self._load_distributed_sensor_registry()
        nodes = self._normalize_mapping(registry.get("nodes"))
        node_assets: list[Dict[str, Any]] = []
        sensor_assets: list[Dict[str, Any]] = []
        for node_id, node in nodes.items():
            node_map = self._normalize_mapping(node)
            node_assets.append({
                "asset_id": f"sensor-node:{node_id}",
                "kind": "physical_node",
                "node_id": str(node_id),
                "node_name": node_map.get("node_name", node_id),
                "available": True,
                "source": "distributed_sensor_registry",
                "last_seen_utc": node_map.get("last_seen_utc"),
            })
            kinds = node_map.get("sensor_kinds") or node_map.get("active_sensor_kinds") or []
            if isinstance(kinds, list):
                for kind in kinds:
                    k = str(kind)
                    sensor_assets.append({
                        "asset_id": f"sensor:{node_id}:{k}",
                        "kind": "sensor",
                        "sensor_kind": k,
                        "node_id": str(node_id),
                        "available": True,
                        "active": k in set(map(str, node_map.get("active_sensor_kinds", []))),
                        "source": "distributed_sensor_registry",
                    })
        return node_assets, sensor_assets

    def _classify_payload_assets(self, payload: Mapping[str, Any]) -> tuple[list[Dict[str, Any]], list[Dict[str, Any]], list[Dict[str, Any]], list[Dict[str, Any]]]:
        physical_nodes = self._normalize_list(payload.get("physical_nodes") or payload.get("nodes"))
        sensors = self._normalize_list(payload.get("sensors"))
        actuators = self._normalize_list(payload.get("actuators"))
        cloud_nodes = self._normalize_list(payload.get("cloud_nodes") or payload.get("cloud"))

        for i, node in enumerate(physical_nodes):
            node.setdefault("asset_id", str(node.get("node_id") or node.get("id") or f"payload-node-{i+1}"))
            node.setdefault("kind", "physical_node")
            node.setdefault("available", True)
            node.setdefault("source", "payload")
        for i, sensor in enumerate(sensors):
            sensor.setdefault("asset_id", str(sensor.get("sensor_id") or sensor.get("id") or f"payload-sensor-{i+1}"))
            sensor.setdefault("kind", "sensor")
            sensor.setdefault("available", True)
            sensor.setdefault("source", "payload")
        for i, actuator in enumerate(actuators):
            actuator.setdefault("asset_id", str(actuator.get("actuator_id") or actuator.get("id") or f"payload-actuator-{i+1}"))
            actuator.setdefault("kind", "actuator")
            actuator.setdefault("available", True)
            actuator.setdefault("source", "payload")
        for i, node in enumerate(cloud_nodes):
            node.setdefault("asset_id", str(node.get("node_id") or node.get("id") or f"payload-cloud-{i+1}"))
            node.setdefault("kind", "cloud_node")
            node.setdefault("available", True)
            node.setdefault("source", "payload")
        return physical_nodes, sensors, actuators, cloud_nodes

    def _load_registry(self) -> Dict[str, Any]:
        default = {"schema_version": self.schema_version, "assets": {}, "snapshots": []}
        data = self._safe_read_json(self.registry_path, default)
        if not isinstance(data, dict):
            return default
        data.setdefault("schema_version", self.schema_version)
        data.setdefault("assets", {})
        data.setdefault("snapshots", [])
        if not isinstance(data["assets"], dict):
            data["assets"] = {}
        if not isinstance(data["snapshots"], list):
            data["snapshots"] = []
        return data

    def _upsert_assets(self, registry: Dict[str, Any], assets: Iterable[Mapping[str, Any]]) -> None:
        now = self._utc()
        table = registry.setdefault("assets", {})
        for asset in assets:
            data = {str(k): v for k, v in dict(asset).items()}
            asset_id = str(data.get("asset_id") or data.get("id") or data.get("path") or data.get("name") or "unknown")
            data["asset_id"] = asset_id
            data.setdefault("available", True)
            previous = table.get(asset_id, {}) if isinstance(table.get(asset_id), dict) else {}
            first_seen = previous.get("first_seen_utc", now)
            data["first_seen_utc"] = first_seen
            data["last_seen_utc"] = now
            data["revocable"] = True
            data["functional_validation_only"] = True
            table[asset_id] = data

    def _metrics(self, registry: Mapping[str, Any]) -> Dict[str, Any]:
        assets = [a for a in self._normalize_mapping(registry.get("assets")).values() if isinstance(a, Mapping)]
        available = [a for a in assets if bool(a.get("available", True))]
        physical_nodes = [a for a in available if a.get("kind") in {"physical_node", "local_host", "gpio_bus", "hardware_bus"}]
        raspberry_nodes = [a for a in available if bool(a.get("is_raspberry_like")) or "raspberry" in str(a.get("hardware_model", "")).lower()]
        sensors = [a for a in available if a.get("kind") == "sensor" or str(a.get("sensor_kind", "")).lower() in self.SENSOR_KEYS]
        actuators = [a for a in available if a.get("kind") == "actuator" or str(a.get("actuator_kind", "")).lower() in self.ACTUATOR_KEYS]
        storage = [a for a in available if a.get("kind") == "storage"]
        cloud = [a for a in available if a.get("kind") == "cloud_node"]

        categories_present = sum(bool(x) for x in [physical_nodes, sensors, actuators, storage, cloud])
        physical_asset_coverage = self._bounded(categories_present / 5.0)
        infrastructure_readiness = self._bounded(
            0.30 * min(len(physical_nodes), 3) / 3.0
            + 0.20 * min(len(sensors), 6) / 6.0
            + 0.15 * min(len(actuators), 4) / 4.0
            + 0.20 * min(len(storage), 2) / 2.0
            + 0.15 * min(len(cloud), 2) / 2.0
        )
        return {
            "physical_node_count": len(physical_nodes),
            "raspberry_node_count": len(raspberry_nodes),
            "registered_sensor_count": len(sensors),
            "registered_actuator_count": len(actuators),
            "storage_asset_count": len(storage),
            "cloud_node_count": len(cloud),
            "physical_asset_count": len(available),
            "physical_asset_coverage": round(physical_asset_coverage, 6),
            "infrastructure_readiness_index": round(infrastructure_readiness, 6),
        }

    def step(self, payload: Any = None, persist: bool = True, **kwargs: Any) -> Dict[str, Any]:
        if payload is None:
            payload = {}
        if not isinstance(payload, Mapping):
            payload = {"assets": payload}
        data: Dict[str, Any] = dict(payload)
        data.update(kwargs)

        registry = self._load_registry()
        host = self._detect_host()
        host_asset = {
            "asset_id": f"host:{host['node_id']}",
            "kind": "local_host",
            "available": True,
            **host,
        }
        storage_assets = self._detect_storage()
        gpio_assets = self._detect_gpio_devices()
        sensor_nodes, registry_sensors = self._assets_from_sensor_registry()
        payload_nodes, payload_sensors, payload_actuators, payload_cloud = self._classify_payload_assets(data)

        explicit_assets = self._normalize_list(data.get("assets"))
        for i, asset in enumerate(explicit_assets):
            asset.setdefault("asset_id", str(asset.get("id") or asset.get("name") or f"payload-asset-{i+1}"))
            asset.setdefault("kind", "physical_asset")
            asset.setdefault("available", True)
            asset.setdefault("source", "payload")

        all_assets = [host_asset]
        all_assets.extend(storage_assets)
        all_assets.extend(gpio_assets)
        all_assets.extend(sensor_nodes)
        all_assets.extend(registry_sensors)
        all_assets.extend(payload_nodes)
        all_assets.extend(payload_sensors)
        all_assets.extend(payload_actuators)
        all_assets.extend(payload_cloud)
        all_assets.extend(explicit_assets)

        self._upsert_assets(registry, all_assets)
        metrics = self._metrics(registry)
        snapshot = {
            "timestamp_utc": self._utc(),
            "metrics": metrics,
            "asset_ids": sorted(self._normalize_mapping(registry.get("assets")).keys()),
        }
        registry["updated_at_utc"] = snapshot["timestamp_utc"]
        registry.setdefault("snapshots", []).append(snapshot)
        registry["snapshots"] = registry["snapshots"][-100:]

        result = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "success": True,
            "schema_version": self.schema_version,
            **metrics,
            "registry_path": str(self.registry_path),
            "latest_path": str(self.latest_path),
            "history_path": str(self.history_path),
            "registered_asset_ids": snapshot["asset_ids"],
            "host_node_id": host["node_id"],
            "host_is_raspberry_like": host["is_raspberry_like"],
            "governance": {
                "revocable": True,
                "non_closure_preserved": True,
                "human_review_required_for_irreversible_physical_action": True,
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
            },
            "timestamp_utc": snapshot["timestamp_utc"],
        }

        if persist:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            self.registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            self.latest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
            result["history_written"] = True
        else:
            result["history_written"] = False
        return result


if __name__ == "__main__":
    print(json.dumps(PhysicalInfrastructureRegistry().step(persist=False), ensure_ascii=False, indent=2))
