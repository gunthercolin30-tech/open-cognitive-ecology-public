
from __future__ import annotations

import json
import math
import os
import platform
import socket
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple


ROOT = Path.home() / "open-cognitive-ecology"


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        x = float(value)
        if math.isnan(x) or math.isinf(x):
            return default
        return x
    except Exception:
        return default


def _bounded(value: Any, lo: float = 0.0, hi: float = 1.0) -> float:
    x = _safe_float(value, lo)
    return max(lo, min(hi, x))


def _as_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


class EnvironmentalStateModel:
    """
    G6 — environmental_state_model.

    Functional environmental-state fusion layer. It does not claim phenomenal
    perception. It fuses observable traces from embodied interfaces, multimodal
    perception, vision, acoustic perception, Raspberry/sensor gateways and
    runtime/system context into a bounded, auditable environmental state.
    """

    primitive = "environmental_state_model"
    refinement = "G6-R1"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else ROOT
        self.state_dir = self.root / "environmental_state"
        self.history_path = self.state_dir / "environmental_state_history.jsonl"
        self.latest_path = self.state_dir / "latest_environmental_state.json"
        self.registry_path = self.state_dir / "environmental_state_registry.json"

    def _safe_component_step(self, module_name: str, class_name: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            module = __import__(f"ontology.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            obj = cls()
            if payload is None:
                return _as_dict(obj.step())
            try:
                return _as_dict(obj.step(payload, persist=False))
            except TypeError:
                return _as_dict(obj.step(payload))
        except Exception as exc:
            return {
                "success": False,
                "component": module_name,
                "error": f"{type(exc).__name__}: {exc}",
            }

    def _runtime_state(self) -> Dict[str, Any]:
        return {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "pid": os.getpid(),
            "cwd": str(Path.cwd()),
            "oce_ssd_mounted": Path("/Volumes/OCE_SSD").exists(),
        }

    def _extract_vision(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        vision = _as_dict(payload.get("vision")) or _as_dict(payload.get("visual"))
        image = _as_dict(payload.get("image"))
        if image and not vision:
            vision = {"image": image}
        labels = []
        labels.extend(_as_list(vision.get("detected_objects")))
        labels.extend(_as_list(vision.get("labels")))
        labels.extend(_as_list(image.get("labels")))
        motion = bool(vision.get("motion_detected") or image.get("motion_detected"))
        events = int(_safe_float(vision.get("vision_events"), 0.0))
        if labels:
            events += len([x for x in labels if x is not None])
        if motion:
            events += 1
        return {
            "active": bool(labels or motion or events),
            "objects": sorted({str(x) for x in labels if x is not None}),
            "motion_detected": motion,
            "event_count": max(0, events),
            "confidence": _bounded(vision.get("visual_grounding_score", vision.get("vision_detection_rate", 0.6 if (labels or motion) else 0.0))),
        }

    def _extract_audio(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        audio = _as_dict(payload.get("audio")) or _as_dict(payload.get("acoustic"))
        events_list = _as_list(audio.get("events")) or _as_list(audio.get("sound_events"))
        transcript = str(audio.get("transcript") or audio.get("text") or "").strip()
        speech = bool(audio.get("speech_detected") or transcript)
        amplitude = _bounded(audio.get("amplitude", 0.0))
        events = int(_safe_float(audio.get("audio_events"), 0.0))
        events += len([x for x in events_list if x is not None])
        if speech:
            events += 1
        if amplitude > 0.0:
            events += 1
        return {
            "active": bool(events or transcript or amplitude > 0.0),
            "sound_events": sorted({str(x) for x in events_list if x is not None}),
            "speech_detected": speech,
            "transcript_present": bool(transcript),
            "amplitude": amplitude,
            "event_count": max(0, events),
            "confidence": _bounded(audio.get("acoustic_grounding_score", audio.get("acoustic_detection_rate", 0.6 if (events or transcript) else 0.0))),
        }

    def _extract_sensors(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        sensors = _as_dict(payload.get("sensors")) or _as_dict(payload.get("sensor")) or _as_dict(payload.get("simulated_sensors"))
        gateway = _as_dict(payload.get("sensor_gateway")) or _as_dict(payload.get("raspberry_sensor_gateway"))
        if gateway:
            sensors = {**_as_dict(gateway.get("sensors")), **sensors}
            for key in ("temperature", "humidity", "light", "button", "relay", "gpio"):
                if key in gateway and key not in sensors:
                    sensors[key] = gateway[key]
        active = {str(k): v for k, v in sensors.items() if v is not None and v is not False}
        numeric_values = {k: _safe_float(v, 0.0) for k, v in active.items() if isinstance(v, (int, float))}
        kinds = sorted(active.keys())
        return {
            "active": bool(active),
            "sensor_count": len(sensors),
            "active_sensor_count": len(active),
            "sensor_kinds": kinds,
            "numeric_values": numeric_values,
            "temperature": sensors.get("temperature"),
            "humidity": sensors.get("humidity"),
            "light": sensors.get("light"),
            "event_count": len(active),
            "confidence": _bounded(gateway.get("gateway_operational_score", 0.7 if active else 0.0)),
        }

    def _extract_multimodal(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        mm = _as_dict(payload.get("multimodal")) or _as_dict(payload.get("multimodal_state"))
        active_modalities = _as_list(mm.get("active_modalities"))
        count = int(_safe_float(mm.get("active_modality_count", len(active_modalities)), 0.0))
        return {
            "active": bool(active_modalities or count),
            "active_modalities": [str(x) for x in active_modalities],
            "active_modality_count": max(count, len(active_modalities)),
            "fusion_quality_score": _bounded(mm.get("fusion_quality_score", 0.0)),
            "sensor_diversity_index": _bounded(mm.get("sensor_diversity_index", 0.0)),
        }

    def _infer_environment_class(self, vision: Dict[str, Any], audio: Dict[str, Any], sensors: Dict[str, Any], runtime: Dict[str, Any]) -> str:
        if vision["active"] and sensors["active"] and audio["active"]:
            return "multimodal_physical_environment"
        if sensors["active"] and (vision["active"] or audio["active"]):
            return "partially_embodied_environment"
        if sensors["active"]:
            return "sensor_grounded_environment"
        if vision["active"] or audio["active"]:
            return "perceptual_environment"
        if runtime:
            return "runtime_context_environment"
        return "unknown_environment"

    def _stability_score(self, state_vector: Dict[str, float]) -> float:
        if not state_vector:
            return 0.0
        values = list(state_vector.values())
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return _bounded(1.0 - min(1.0, math.sqrt(variance)))

    def _write_record(self, record: Dict[str, Any]) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        self.latest_path.write_text(json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        registry = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "latest_state_id": record["state_id"],
            "latest_timestamp_utc": record["timestamp_utc"],
            "history_path": str(self.history_path),
            "latest_path": str(self.latest_path),
            "environment_class": record["environment_class"],
            "environmental_state_stability": record["environmental_state_stability"],
        }
        self.registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def step(self, payload: Optional[Dict[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        payload = _as_dict(payload)

        component_results: Dict[str, Any] = {}
        if payload.get("auto_collect", False):
            component_results["embodied_world_interface"] = self._safe_component_step("embodied_world_interface", "EmbodiedWorldInterface")
            component_results["multimodal_perception_engine"] = self._safe_component_step("multimodal_perception_engine", "MultimodalPerceptionEngine")
            component_results["visual_world_perception"] = self._safe_component_step("visual_world_perception", "VisualWorldPerception")
            component_results["acoustic_world_perception"] = self._safe_component_step("acoustic_world_perception", "AcousticWorldPerception")
            component_results["raspberry_sensor_gateway"] = self._safe_component_step("raspberry_sensor_gateway", "RaspberrySensorGateway")

        vision = self._extract_vision(payload)
        audio = self._extract_audio(payload)
        sensors = self._extract_sensors(payload)
        multimodal = self._extract_multimodal(payload)
        runtime = _as_dict(payload.get("runtime")) or self._runtime_state()
        system = _as_dict(payload.get("system"))

        if not sensors["active"] and component_results.get("raspberry_sensor_gateway", {}).get("success"):
            sensors = self._extract_sensors({"raspberry_sensor_gateway": component_results["raspberry_sensor_gateway"]})
        if not vision["active"] and component_results.get("visual_world_perception", {}).get("success"):
            vision = self._extract_vision({"vision": component_results["visual_world_perception"]})
        if not audio["active"] and component_results.get("acoustic_world_perception", {}).get("success"):
            audio = self._extract_audio({"audio": component_results["acoustic_world_perception"]})
        if not multimodal["active"] and component_results.get("multimodal_perception_engine", {}).get("success"):
            multimodal = self._extract_multimodal({"multimodal": component_results["multimodal_perception_engine"]})

        active_modalities = []
        for name, block in (("vision", vision), ("audio", audio), ("sensors", sensors), ("runtime", {"active": bool(runtime)}), ("system", {"active": bool(system)}), ("multimodal", multimodal)):
            if block.get("active"):
                active_modalities.append(name)

        observation_count = int(vision["event_count"] + audio["event_count"] + sensors["event_count"] + (1 if runtime else 0) + (1 if system else 0))
        model_updates = 1 if observation_count > 0 or runtime else 0
        modality_capacity = 6.0
        environmental_coverage_index = _bounded(len(active_modalities) / modality_capacity)
        grounding_values = [vision["confidence"], audio["confidence"], sensors["confidence"], multimodal["fusion_quality_score"]]
        grounding_values = [x for x in grounding_values if x > 0.0]
        environmental_grounding_score = _bounded(sum(grounding_values) / len(grounding_values)) if grounding_values else 0.0
        state_vector = {
            "vision": vision["confidence"],
            "audio": audio["confidence"],
            "sensors": sensors["confidence"],
            "coverage": environmental_coverage_index,
            "grounding": environmental_grounding_score,
        }
        stability = self._stability_score(state_vector)
        coherence = _bounded((environmental_coverage_index + environmental_grounding_score + stability) / 3.0)
        env_class = self._infer_environment_class(vision, audio, sensors, runtime)

        state_id_seed = json.dumps({"timestamp": _utc(), "modalities": active_modalities, "obs": observation_count}, sort_keys=True)
        import hashlib
        state_id = "ENV-" + hashlib.sha256(state_id_seed.encode("utf-8")).hexdigest()[:16]

        record = {
            "primitive": self.primitive,
            "refinement": self.refinement,
            "success": True,
            "timestamp_utc": _utc(),
            "state_id": state_id,
            "environment_class": env_class,
            "active_modalities": active_modalities,
            "active_modality_count": len(active_modalities),
            "environmental_model_updates": model_updates,
            "environmental_observation_count": observation_count,
            "environmental_state_stability": stability,
            "environmental_state_coherence": coherence,
            "environmental_grounding_score": environmental_grounding_score,
            "environmental_coverage_index": environmental_coverage_index,
            "sensor_count": sensors["sensor_count"],
            "active_sensor_count": sensors["active_sensor_count"],
            "vision_event_count": vision["event_count"],
            "audio_event_count": audio["event_count"],
            "runtime_context_active": bool(runtime),
            "state": {
                "vision": vision,
                "audio": audio,
                "sensors": sensors,
                "multimodal": multimodal,
                "runtime": runtime,
                "system": system,
            },
            "component_results": component_results,
            "diagnostics": {
                "functional_validation_only": True,
                "phenomenal_subjectivity_claimed": False,
                "non_redundant_role": "sensor_visual_audio_runtime_environmental_state_fusion",
                "depends_on_phases": ["G1", "G2", "G3", "G4", "G5"],
                "supports_future_phases": ["G7", "G8", "G9", "G10"],
            },
            "history_path": str(self.history_path),
            "latest_path": str(self.latest_path),
            "registry_path": str(self.registry_path),
        }

        if persist:
            self._write_record(record)
            record["history_written"] = True
        else:
            record["history_written"] = False

        return record


if __name__ == "__main__":
    result = EnvironmentalStateModel().step({
        "vision": {"detected_objects": ["screen"], "motion_detected": False},
        "audio": {"events": ["ambient"], "amplitude": 0.2},
        "sensors": {"temperature": 21.0, "humidity": 0.5, "light": 0.7},
    }, persist=False)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
