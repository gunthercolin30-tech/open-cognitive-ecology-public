# -*- coding: utf-8 -*-

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import json
import math
import os
import platform
import re

PRIMITIVE = "multimodal_perception_engine"
REFINEMENT = "G2-R1"

DEPENDENCIES = [
    "embodied_world_interface",
    "embodied_sensorimotor_ecology",
    "embodiment",
    "hierarchical_world_model_engine",
    "predictive_environment_simulator",
    "experience_integration_loop",
    "experiential_stream_integration",
    "global_temporal_binding",
    "memory_consolidation",
    "multimodal_observation_archive",
    "metrics_history_recorder",
    "governance_consistency_checker",
    "constitutional_alert_system",
    "openness_preservation_supervisor",
    "anti_closure_metaconstraint",
]

MODALITIES = ["text", "image", "audio", "sensor", "system", "embodied_interface"]


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bounded(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = default
    if math.isnan(number) or math.isinf(number):
        return default
    return max(0.0, min(1.0, number))


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _json_text(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except Exception:
        return str(value)


def _hash(value: Any) -> str:
    return hashlib.sha256(_json_text(value).encode("utf-8", errors="replace")).hexdigest()[:16]


def _short_text(value: Any, limit: int = 240) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= limit:
        return text
    return text[:limit - 3] + "..."


def _payload_size(value: Any) -> int:
    try:
        return len(_json_text(value).encode("utf-8"))
    except Exception:
        return len(str(value).encode("utf-8", errors="replace"))


class MultimodalPerceptionEngine:
    """G2 — Multimodal Perception Layer.

    Fuses passive observations from text, image metadata, audio metadata,
    sensors, local system state, and the G1 embodied interface foundation. The
    engine deliberately avoids mandatory capture dependencies. Actual camera
    and microphone acquisition belong to G3/G4; G2 builds the shared semantic
    observation format and archiveable fusion layer.
    """

    primitive = PRIMITIVE
    refinement = REFINEMENT
    dependencies = DEPENDENCIES

    def __init__(self, root: Optional[str | Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.state_dir = self.root / "multimodal_observations"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.state_dir / "multimodal_perception_state.json"

    def _load_state(self) -> Dict[str, Any]:
        if self.state_path.exists():
            try:
                data = json.loads(self.state_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        return {
            "primitive": PRIMITIVE,
            "perception_cycles": 0,
            "multimodal_observation_count": 0,
            "latest_observation_id": None,
            "latest_timestamp_utc": None,
        }

    def _save_state(self, state: Dict[str, Any]) -> None:
        state["primitive"] = PRIMITIVE
        self.state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")

    def _normalise_text(self, payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict):
            text = payload.get("text") or payload.get("content") or payload.get("message") or ""
            source = payload.get("source", "provided")
        else:
            text = payload or ""
            source = "provided"
        text = str(text or "")
        token_count = len(re.findall(r"\w+", text, flags=re.UNICODE))
        active = bool(text.strip())
        return {
            "kind": "text",
            "active": active,
            "source": source,
            "summary": _short_text(text),
            "token_count": token_count,
            "confidence": 0.9 if active else 0.0,
            "hash": _hash(text) if active else None,
        }

    def _normalise_image(self, payload: Any) -> Dict[str, Any]:
        if payload is None:
            return {"kind": "image", "active": False, "confidence": 0.0, "summary": "no image observation"}
        if isinstance(payload, dict):
            path = payload.get("path") or payload.get("image_path")
            labels = payload.get("labels") or payload.get("objects") or []
            width = payload.get("width")
            height = payload.get("height")
            motion = bool(payload.get("motion_detected", False))
            active = bool(path or labels or width or height or motion or payload.get("present"))
            summary = {
                "path": str(path) if path else None,
                "labels": labels if isinstance(labels, list) else [str(labels)],
                "width": width,
                "height": height,
                "motion_detected": motion,
            }
        else:
            active = bool(payload)
            summary = {"descriptor": _short_text(payload)}
        return {
            "kind": "image",
            "active": active,
            "summary": summary,
            "confidence": 0.75 if active else 0.0,
            "hash": _hash(summary) if active else None,
        }

    def _normalise_audio(self, payload: Any) -> Dict[str, Any]:
        if payload is None:
            return {"kind": "audio", "active": False, "confidence": 0.0, "summary": "no audio observation"}
        if isinstance(payload, dict):
            transcript = payload.get("transcript") or payload.get("text") or ""
            events = payload.get("events") or payload.get("sound_events") or []
            level = payload.get("level") or payload.get("rms") or payload.get("volume")
            duration = payload.get("duration_seconds")
            active = bool(transcript or events or level is not None or payload.get("present"))
            summary = {
                "transcript": _short_text(transcript),
                "events": events if isinstance(events, list) else [str(events)],
                "level": level,
                "duration_seconds": duration,
            }
        else:
            active = bool(payload)
            summary = {"descriptor": _short_text(payload)}
        return {
            "kind": "audio",
            "active": active,
            "summary": summary,
            "confidence": 0.75 if active else 0.0,
            "hash": _hash(summary) if active else None,
        }

    def _normalise_sensor(self, payload: Any) -> Dict[str, Any]:
        readings: Dict[str, Any] = {}
        if isinstance(payload, dict):
            readings = dict(payload)
        elif isinstance(payload, list):
            readings = {f"sensor_{i}": value for i, value in enumerate(payload)}
        elif payload is not None:
            readings = {"value": payload}
        active_items = {k: v for k, v in readings.items() if v is not None}
        numeric_count = 0
        for value in active_items.values():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                numeric_count += 1
        active = bool(active_items)
        return {
            "kind": "sensor",
            "active": active,
            "summary": active_items,
            "sensor_count": len(active_items),
            "numeric_sensor_count": numeric_count,
            "confidence": 0.8 if active else 0.0,
            "hash": _hash(active_items) if active else None,
        }

    def _system_observation(self, payload: Any) -> Dict[str, Any]:
        base = {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "python_version": platform.python_version(),
            "cwd": str(Path.cwd()),
        }
        if isinstance(payload, dict):
            base.update(payload)
        active = True
        return {
            "kind": "system",
            "active": active,
            "summary": base,
            "confidence": 0.85,
            "hash": _hash(base),
        }

    def _embodied_interface_observation(self, payload: Any) -> Dict[str, Any]:
        if isinstance(payload, dict) and payload:
            result = dict(payload)
        else:
            result = {}
            try:
                from ontology.embodied_world_interface import EmbodiedWorldInterface
                result = EmbodiedWorldInterface(root=self.root).step()
            except Exception as exc:
                result = {"error": exc.__class__.__name__, "physical_interfaces_detected": 0, "physical_interfaces_active": 0}
        active_kinds = result.get("active_interface_kinds") or []
        active = bool(result.get("physical_interfaces_active") or active_kinds)
        return {
            "kind": "embodied_interface",
            "active": active,
            "summary": {
                "physical_interfaces_detected": result.get("physical_interfaces_detected", 0),
                "physical_interfaces_active": result.get("physical_interfaces_active", 0),
                "active_interface_kinds": active_kinds,
                "sensor_diversity_index": result.get("sensor_diversity_index", 0.0),
            },
            "confidence": 0.85 if active else 0.25,
            "hash": _hash(result),
        }

    def _extract_payloads(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        observations = inputs.get("observations") if isinstance(inputs.get("observations"), dict) else {}
        return {
            "text": inputs.get("text", observations.get("text")),
            "image": inputs.get("image", observations.get("image")),
            "audio": inputs.get("audio", observations.get("audio")),
            "sensor": inputs.get("sensor", inputs.get("sensors", observations.get("sensor", observations.get("sensors")))),
            "system": inputs.get("system", observations.get("system")),
            "embodied_interface": inputs.get("embodied_interface", observations.get("embodied_interface")),
        }

    def _build_modalities(self, inputs: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        payloads = self._extract_payloads(inputs)
        return {
            "text": self._normalise_text(payloads.get("text")),
            "image": self._normalise_image(payloads.get("image")),
            "audio": self._normalise_audio(payloads.get("audio")),
            "sensor": self._normalise_sensor(payloads.get("sensor")),
            "system": self._system_observation(payloads.get("system")),
            "embodied_interface": self._embodied_interface_observation(payloads.get("embodied_interface")),
        }

    def _fusion(self, modalities: Dict[str, Dict[str, Any]]) -> Tuple[str, float, float, List[str]]:
        active = [name for name, rec in modalities.items() if rec.get("active")]
        confidence_values = [_bounded(rec.get("confidence")) for rec in modalities.values()]
        mean_confidence = sum(confidence_values) / max(1, len(confidence_values))
        diversity = len(active) / max(1, len(MODALITIES))
        markers: List[str] = []
        for name, rec in modalities.items():
            if rec.get("active"):
                markers.append(name)
        fusion_quality = _bounded(0.55 * diversity + 0.45 * mean_confidence)
        if active:
            summary = "active modalities: " + ", ".join(active)
        else:
            summary = "no active external modality; passive system observation only"
        return summary, diversity, fusion_quality, markers

    def _record_metrics(self, output: Dict[str, Any]) -> None:
        try:
            from ontology.metrics_history_recorder import MetricsHistoryRecorder
            MetricsHistoryRecorder(root=self.root).step(output)
        except Exception:
            pass

    def _archive(self, observation: Dict[str, Any], persist: bool) -> Dict[str, Any]:
        try:
            from ontology.multimodal_observation_archive import MultimodalObservationArchive
            return MultimodalObservationArchive(root=self.root).step(observation, persist=persist)
        except Exception as exc:
            return {
                "success": False,
                "observation_archived": False,
                "error": exc.__class__.__name__,
                "multimodal_observation_count": 0,
            }

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        state = self._load_state()
        modalities = self._build_modalities(inputs)
        fusion_summary, sensor_diversity_index, fusion_quality, markers = self._fusion(modalities)
        active_modalities = [name for name, rec in modalities.items() if rec.get("active")]
        timestamp = _utc()
        observation = {
            "primitive": PRIMITIVE,
            "refinement": REFINEMENT,
            "timestamp_utc": timestamp,
            "observation_id": "MMO-" + _hash({"timestamp": timestamp, "modalities": modalities}),
            "modality_summary": modalities,
            "active_modalities": active_modalities,
            "active_modality_count": len(active_modalities),
            "fusion_summary": fusion_summary,
            "fusion_markers": markers,
            "sensor_diversity_index": sensor_diversity_index,
            "fusion_quality_score": fusion_quality,
            "payload_size_bytes": _payload_size(modalities),
            "raw_binary_stored": False,
            "observational_only": True,
            "non_closure_compliant": True,
        }
        archive_result = self._archive(observation, persist=persist)
        state["perception_cycles"] = _safe_int(state.get("perception_cycles")) + 1
        if persist:
            state["multimodal_observation_count"] = _safe_int(state.get("multimodal_observation_count")) + 1
            state["latest_observation_id"] = observation["observation_id"]
            state["latest_timestamp_utc"] = timestamp
            self._save_state(state)

        output = {
            "primitive": PRIMITIVE,
            "refinement": REFINEMENT,
            "success": True,
            "timestamp_utc": timestamp,
            "observation_id": observation["observation_id"],
            "perception_cycles": state.get("perception_cycles", 0),
            "multimodal_observation_count": state.get("multimodal_observation_count", 0),
            "active_modalities": active_modalities,
            "active_modality_count": len(active_modalities),
            "modality_summary": modalities,
            "fusion_summary": fusion_summary,
            "fusion_quality_score": fusion_quality,
            "sensor_diversity_index": sensor_diversity_index,
            "observation_archived": bool(archive_result.get("observation_archived")),
            "archive_result": archive_result,
            "text_active": modalities["text"].get("active", False),
            "image_active": modalities["image"].get("active", False),
            "audio_active": modalities["audio"].get("active", False),
            "sensor_active": modalities["sensor"].get("active", False),
            "system_active": modalities["system"].get("active", False),
            "embodied_interface_active": modalities["embodied_interface"].get("active", False),
            "governance": {
                "observational_only": True,
                "raw_binary_stored": False,
                "direct_actuation_authorized": False,
                "non_closure_compliant": True,
                "human_oversight_preserved": True,
            },
            "metrics": {
                "multimodal_observation_count": state.get("multimodal_observation_count", 0),
                "active_modality_count": len(active_modalities),
                "sensor_diversity_index": sensor_diversity_index,
                "fusion_quality_score": fusion_quality,
            },
            "diagnostics": {
                "schema_version": "G2.multimodal_perception_engine.v1",
                "dependencies": DEPENDENCIES,
                "state_path": str(self.state_path),
                "archive_path": archive_result.get("history_path"),
                "capture_scope": "passive_metadata_and_supplied_observations",
                "next_layers": ["visual_world_perception", "acoustic_world_perception", "environmental_state_model"],
            },
        }
        if persist:
            self._record_metrics(output)
        return output


if __name__ == "__main__":
    demo = MultimodalPerceptionEngine().step({"text": "G2 multimodal perception demo"}, persist=False)
    print(json.dumps(demo, ensure_ascii=False, indent=2, sort_keys=True))
