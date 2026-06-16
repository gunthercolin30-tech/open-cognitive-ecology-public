from __future__ import annotations

import json
import math
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping


class DistributedSensorExpansionManager:
    """
    Q3 — Distributed Sensor Expansion Manager.

    This primitive governs the expansion layer above the distributed sensor
    registry. It does not merely store sensors; it discovers, qualifies,
    onboards and measures the growth and coverage of the physical sensor
    network while preserving traceability, revocability and non-closure.

    It makes only functional claims: no phenomenal subjectivity is asserted.
    """

    primitive = "distributed_sensor_expansion_manager"
    refinement = "Q3-R1"
    schema_version = "Q3.distributed_sensor_expansion_manager.v1"

    CANONICAL_SENSOR_TYPES = {
        "temperature",
        "humidity",
        "light",
        "button",
        "relay",
        "gpio",
        "camera",
        "microphone",
        "pressure",
        "motion",
        "distance",
        "voltage",
    }

    SENSOR_ALIASES = {
        "temp": "temperature",
        "temperature_c": "temperature",
        "hum": "humidity",
        "lux": "light",
        "illumination": "light",
        "gpio_pin": "gpio",
        "mic": "microphone",
        "cam": "camera",
        "pir": "motion",
    }

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.sensor_dir = self.root / "physical_sensors"
        self.ecology_dir = self.root / "physical_ecology"
        self.state_path = self.sensor_dir / "distributed_sensor_expansion_manager.json"
        self.latest_path = self.sensor_dir / "latest_distributed_sensor_expansion_manager.json"
        self.history_path = self.sensor_dir / "distributed_sensor_expansion_manager_history.jsonl"
        self.registry_path = self.sensor_dir / "distributed_sensor_registry.json"
        self.latest_registry_path = self.sensor_dir / "latest_distributed_sensor_registry.json"
        self.q1_path = self.ecology_dir / "latest_physical_infrastructure_registry.json"
        self.q2_path = self.ecology_dir / "latest_hardware_health_monitor.json"

    @staticmethod
    def _utc() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _bounded(value: Any, lo: float = 0.0, hi: float = 1.0) -> float:
        try:
            value = float(value)
        except Exception:
            return lo
        if math.isnan(value) or math.isinf(value):
            return lo
        return max(lo, min(hi, value))

    @staticmethod
    def _safe_json(path: Path, default: Any) -> Any:
        try:
            if path.exists():
                data = json.loads(path.read_text(encoding="utf-8"))
                return data if data is not None else default
        except Exception:
            return default
        return default

    @classmethod
    def _sensor_type(cls, value: Any) -> str:
        raw = str(value or "unspecified").strip().lower().replace(" ", "_").replace("-", "_")
        return cls.SENSOR_ALIASES.get(raw, raw)

    @classmethod
    def _normalize_sensor_map(cls, value: Any) -> Dict[str, Any]:
        if isinstance(value, Mapping):
            return {cls._sensor_type(k): v for k, v in value.items()}
        if isinstance(value, list):
            out: Dict[str, Any] = {}
            for item in value:
                if isinstance(item, Mapping):
                    kind = item.get("kind") or item.get("type") or item.get("name") or item.get("sensor")
                    if kind:
                        out[cls._sensor_type(kind)] = item.get("value", item.get("active", True))
                else:
                    out[cls._sensor_type(item)] = True
            return out
        return {}

    def _load_registry(self) -> Dict[str, Any]:
        data = self._safe_json(self.registry_path, {})
        if not isinstance(data, dict):
            return {"nodes": {}}
        nodes = data.get("nodes")
        if not isinstance(nodes, dict):
            data["nodes"] = {}
        return data

    def _existing_sensor_profile(self, registry: Mapping[str, Any]) -> Dict[str, Any]:
        nodes = registry.get("nodes", {}) if isinstance(registry, Mapping) else {}
        if not isinstance(nodes, Mapping):
            nodes = {}
        types: set[str] = set()
        active_types: set[str] = set()
        total = 0
        active_total = 0
        for node in nodes.values():
            if not isinstance(node, Mapping):
                continue
            sensor_kinds = node.get("sensor_kinds") or node.get("active_sensor_kinds") or []
            if isinstance(sensor_kinds, list):
                for kind in sensor_kinds:
                    types.add(self._sensor_type(kind))
            active_kinds = node.get("active_sensor_kinds") or []
            if isinstance(active_kinds, list):
                for kind in active_kinds:
                    active_types.add(self._sensor_type(kind))
            try:
                total += int(node.get("sensor_count", len(sensor_kinds) if isinstance(sensor_kinds, list) else 0))
            except Exception:
                pass
            try:
                active_total += int(node.get("active_sensor_count", len(active_kinds) if isinstance(active_kinds, list) else 0))
            except Exception:
                pass
        return {
            "node_count": len(nodes),
            "sensor_count": total,
            "active_sensor_count": active_total,
            "sensor_types": sorted(types),
            "active_sensor_types": sorted(active_types),
        }

    def _default_candidates(self, profile: Mapping[str, Any]) -> list[Dict[str, Any]]:
        current = set(profile.get("sensor_types", [])) if isinstance(profile.get("sensor_types"), list) else set()
        missing = sorted(self.CANONICAL_SENSOR_TYPES - current)
        preferred = missing[:3]
        if not preferred:
            preferred = ["temperature", "light"]
        host = socket.gethostname() or "local-node"
        return [
            {
                "candidate_id": f"auto:{host}:{kind}",
                "node_id": f"sensor-expansion:{host}",
                "kind": kind,
                "value": True,
                "confidence": 0.72 if kind in self.CANONICAL_SENSOR_TYPES else 0.5,
                "source": "gap_analysis",
                "revocable": True,
            }
            for kind in preferred
        ]

    def _normalize_candidates(self, payload: Any, profile: Mapping[str, Any]) -> list[Dict[str, Any]]:
        if not isinstance(payload, Mapping):
            return self._default_candidates(profile)
        raw = payload.get("discovery_candidates") or payload.get("candidate_sensors") or payload.get("new_sensors")
        candidates: list[Dict[str, Any]] = []
        if isinstance(raw, list):
            for idx, item in enumerate(raw):
                if isinstance(item, Mapping):
                    kind = self._sensor_type(item.get("kind") or item.get("type") or item.get("name") or item.get("sensor") or f"candidate_{idx}")
                    node_id = str(item.get("node_id") or item.get("host_id") or f"candidate-node-{idx}")
                    confidence = self._bounded(item.get("confidence", item.get("reliability", 0.7)))
                    candidates.append({
                        "candidate_id": str(item.get("candidate_id") or f"candidate:{node_id}:{kind}"),
                        "node_id": node_id,
                        "kind": kind,
                        "value": item.get("value", item.get("active", True)),
                        "confidence": confidence,
                        "source": str(item.get("source") or "payload"),
                        "revocable": bool(item.get("revocable", True)),
                    })
                else:
                    kind = self._sensor_type(item)
                    candidates.append({
                        "candidate_id": f"candidate:payload:{idx}:{kind}",
                        "node_id": f"candidate-node-{idx}",
                        "kind": kind,
                        "value": True,
                        "confidence": 0.65,
                        "source": "payload",
                        "revocable": True,
                    })
        elif isinstance(raw, Mapping):
            for idx, (kind_raw, value) in enumerate(raw.items()):
                kind = self._sensor_type(kind_raw)
                candidates.append({
                    "candidate_id": f"candidate:payload:{idx}:{kind}",
                    "node_id": str(payload.get("node_id") or payload.get("host_id") or "candidate-node"),
                    "kind": kind,
                    "value": value,
                    "confidence": 0.7,
                    "source": "payload",
                    "revocable": True,
                })
        if not candidates:
            sensors = self._normalize_sensor_map(payload.get("sensors") or payload.get("readings"))
            for idx, (kind, value) in enumerate(sensors.items()):
                candidates.append({
                    "candidate_id": f"candidate:sensors:{idx}:{kind}",
                    "node_id": str(payload.get("node_id") or payload.get("host_id") or "candidate-node"),
                    "kind": kind,
                    "value": value,
                    "confidence": 0.7,
                    "source": "payload_sensors",
                    "revocable": True,
                })
        return candidates or self._default_candidates(profile)

    def _qualify_candidates(self, candidates: Iterable[Mapping[str, Any]], profile: Mapping[str, Any], q2: Mapping[str, Any]) -> list[Dict[str, Any]]:
        existing_types = set(profile.get("sensor_types", [])) if isinstance(profile.get("sensor_types"), list) else set()
        hardware_health = self._bounded(q2.get("hardware_health_index", 0.75)) if isinstance(q2, Mapping) else 0.75
        qualified: list[Dict[str, Any]] = []
        for candidate in candidates:
            kind = self._sensor_type(candidate.get("kind"))
            confidence = self._bounded(candidate.get("confidence", 0.5))
            novelty = 0.35 if kind in existing_types else 1.0
            canonical = 1.0 if kind in self.CANONICAL_SENSOR_TYPES else 0.55
            revocable = bool(candidate.get("revocable", True))
            governance_score = 1.0 if revocable else 0.45
            qualification_score = self._bounded(
                0.30 * confidence
                + 0.25 * novelty
                + 0.20 * canonical
                + 0.15 * hardware_health
                + 0.10 * governance_score
            )
            qualified.append({
                "candidate_id": str(candidate.get("candidate_id") or f"candidate:{kind}"),
                "node_id": str(candidate.get("node_id") or "candidate-node"),
                "kind": kind,
                "value": candidate.get("value", True),
                "source": str(candidate.get("source") or "unknown"),
                "confidence": confidence,
                "novel_sensor_type": kind not in existing_types,
                "canonical_sensor_type": kind in self.CANONICAL_SENSOR_TYPES,
                "revocable": revocable,
                "qualification_score": round(qualification_score, 6),
                "approved_for_onboarding": qualification_score >= 0.55 and revocable,
            })
        return qualified

    def _onboard(self, qualified: Iterable[Mapping[str, Any]], persist: bool) -> Dict[str, Any]:
        approved = [q for q in qualified if q.get("approved_for_onboarding")]
        if not approved:
            return {"onboarded_sensor_count": 0, "onboarded_node_count": 0, "registry_update_success": True}
        grouped: Dict[str, Dict[str, Any]] = {}
        for item in approved:
            node_id = str(item.get("node_id") or "candidate-node")
            grouped.setdefault(node_id, {})[str(item.get("kind"))] = item.get("value", True)
        try:
            from ontology.distributed_sensor_registry import DistributedSensorRegistry
            registry = DistributedSensorRegistry(root=self.root)
            for node_id, sensors in grouped.items():
                registry.step({"node_id": node_id, "node_name": node_id, "sensors": sensors}, persist=persist)
            return {
                "onboarded_sensor_count": sum(len(v) for v in grouped.values()),
                "onboarded_node_count": len(grouped),
                "registry_update_success": True,
            }
        except Exception as exc:
            return {
                "onboarded_sensor_count": 0,
                "onboarded_node_count": 0,
                "registry_update_success": False,
                "registry_update_error": str(exc),
            }

    def _append_history(self, result: Mapping[str, Any]) -> bool:
        try:
            self.sensor_dir.mkdir(parents=True, exist_ok=True)
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(dict(result), ensure_ascii=False, sort_keys=True) + chr(10))
            return True
        except Exception:
            return False

    def step(self, payload: Any = None, persist: bool = True, **kwargs: Any) -> Dict[str, Any]:
        if payload is None:
            payload = {}
        if not isinstance(payload, Mapping):
            payload = {"discovery_candidates": payload}
        data = dict(payload)
        data.update(kwargs)

        registry_before = self._load_registry()
        profile_before = self._existing_sensor_profile(registry_before)
        q1 = self._safe_json(self.q1_path, {})
        q2 = self._safe_json(self.q2_path, {})

        candidates = self._normalize_candidates(data, profile_before)
        qualified = self._qualify_candidates(candidates, profile_before, q2 if isinstance(q2, Mapping) else {})
        onboarding = self._onboard(qualified, persist=persist)

        registry_after = self._load_registry() if persist else registry_before
        profile_after = self._existing_sensor_profile(registry_after)
        before_count = int(profile_before.get("sensor_count", 0))
        after_count = int(profile_after.get("sensor_count", before_count))
        approved_count = sum(1 for q in qualified if q.get("approved_for_onboarding"))
        onboarded_count = int(onboarding.get("onboarded_sensor_count", 0))

        projected_after_count = max(after_count, before_count + (onboarded_count if persist else approved_count))
        sensor_growth_rate = self._bounded((projected_after_count - before_count) / max(1, before_count))

        types_after = set(profile_after.get("sensor_types", [])) if isinstance(profile_after.get("sensor_types"), list) else set()
        if not persist:
            types_after = set(profile_before.get("sensor_types", [])) if isinstance(profile_before.get("sensor_types"), list) else set()
            types_after.update(str(q.get("kind")) for q in qualified if q.get("approved_for_onboarding"))

        type_coverage = self._bounded(len(types_after & self.CANONICAL_SENSOR_TYPES) / len(self.CANONICAL_SENSOR_TYPES))
        q1_coverage = self._bounded(q1.get("physical_asset_coverage", 0.5)) if isinstance(q1, Mapping) else 0.5
        q2_health = self._bounded(q2.get("hardware_health_index", 0.75)) if isinstance(q2, Mapping) else 0.75
        node_basis = max(1, int(q1.get("physical_node_count", profile_before.get("node_count", 1))) if isinstance(q1, Mapping) else int(profile_before.get("node_count", 1)))
        node_coverage = self._bounded(max(int(profile_before.get("node_count", 0)), int(profile_after.get("node_count", 0))) / node_basis)
        sensor_network_coverage = self._bounded(0.45 * type_coverage + 0.25 * q1_coverage + 0.20 * node_coverage + 0.10 * q2_health)
        expansion_readiness_index = self._bounded(0.40 * sensor_network_coverage + 0.25 * q2_health + 0.20 * (approved_count / max(1, len(qualified))) + 0.15 * (1.0 if onboarding.get("registry_update_success", False) else 0.0))

        recommendations: list[str] = []
        missing_types = sorted(self.CANONICAL_SENSOR_TYPES - types_after)
        if missing_types:
            recommendations.append("Prioritize missing canonical sensor types: " + ", ".join(missing_types[:5]))
        if q2_health < 0.6:
            recommendations.append("Delay aggressive sensor expansion until hardware health improves.")
        if not recommendations:
            recommendations.append("Maintain governed incremental sensor expansion and longitudinal monitoring.")

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "success": True,
            "schema_version": self.schema_version,
            "q1_registry_integrated": bool(isinstance(q1, Mapping) and q1),
            "q2_health_integrated": bool(isinstance(q2, Mapping) and q2),
            "registry_integrated": True,
            "candidate_sensor_count": len(qualified),
            "approved_candidate_count": approved_count,
            "onboarded_sensor_count": onboarded_count,
            "onboarded_node_count": int(onboarding.get("onboarded_node_count", 0)),
            "registry_update_success": bool(onboarding.get("registry_update_success", False)),
            "sensor_count_before": before_count,
            "sensor_count_after": projected_after_count,
            "distributed_sensor_node_count": max(int(profile_before.get("node_count", 0)), int(profile_after.get("node_count", 0))),
            "sensor_growth_rate": round(sensor_growth_rate, 6),
            "sensor_network_coverage": round(sensor_network_coverage, 6),
            "sensor_type_coverage": round(type_coverage, 6),
            "node_coverage": round(node_coverage, 6),
            "expansion_readiness_index": round(expansion_readiness_index, 6),
            "hardware_health_index": round(q2_health, 6),
            "known_sensor_types": sorted(types_after),
            "missing_sensor_types": missing_types,
            "qualified_candidates": qualified,
            "recommendations": recommendations,
            "state_path": str(self.state_path),
            "latest_path": str(self.latest_path),
            "history_path": str(self.history_path),
            "governance": {
                "revocable": True,
                "non_closure_preserved": True,
                "human_review_required_for_irreversible_physical_action": True,
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
            },
            "timestamp_utc": self._utc(),
        }
        if "registry_update_error" in onboarding:
            result["registry_update_error"] = onboarding["registry_update_error"]

        if persist:
            self.sensor_dir.mkdir(parents=True, exist_ok=True)
            self.state_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            self.latest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            result["history_written"] = self._append_history(result)
            # Rewrite latest files with the final history flag included.
            self.state_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
            self.latest_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        else:
            result["history_written"] = False

        return result


if __name__ == "__main__":
    print(json.dumps(DistributedSensorExpansionManager().step(persist=False), ensure_ascii=False, indent=2, sort_keys=True))
