"""
G3 — Visual World Perception.

This module provides a governed, passive and reversible visual perception
layer for Open Cognitive Ecology. It does not claim phenomenological vision;
it records functional visual observations and measurable indicators only.

Design constraints:
- no mandatory OpenCV / camera dependency;
- simulated and file-based observations are supported;
- physical capture is best-effort and disabled unless explicitly requested;
- all outputs are traceable, bounded and reversible;
- optional integration with G2 multimodal perception is observational only.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path.home() / "open-cognitive-ecology"
VISUAL_DIR = ROOT / "visual_world_observations"
HISTORY_PATH = VISUAL_DIR / "visual_world_perception_history.jsonl"
LATEST_PATH = VISUAL_DIR / "latest_visual_world_perception.json"


class VisualWorldPerception:
    """
    Passive visual perception interface.

    The class can process synthetic observations, image metadata, image file
    paths, and best-effort camera availability signals. It intentionally avoids
    mandatory hardware or computer-vision dependencies so validation remains
    stable on Mac, Linux, cloud and headless nodes.
    """

    primitive = "VISUAL_WORLD_PERCEPTION"
    schema_version = "VWP.v1"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or ROOT
        self.visual_dir = self.root / "visual_world_observations"
        self.history_path = self.visual_dir / "visual_world_perception_history.jsonl"
        self.latest_path = self.visual_dir / "latest_visual_world_perception.json"

    def step(
        self,
        inputs: dict[str, Any] | None = None,
        *,
        persist: bool = True,
    ) -> dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = self._now()

        visual_input = self._normalize_visual_input(inputs)
        interface_state = self._read_embodied_interface(inputs)
        capture_result = self._capture_best_effort(inputs, interface_state)
        detection = self._detect_visual_events(visual_input, capture_result)

        captured_images = 1 if capture_result.get("image_available") else 0
        object_count = len(detection["detected_objects"])
        motion_events = 1 if detection["motion_detected"] else 0
        vision_events = object_count + motion_events
        visual_signal_available = bool(
            visual_input.get("image_active")
            or visual_input.get("path")
            or captured_images
            or object_count
            or motion_events
        )

        visual_detection_rate = self._bounded(
            (object_count * 0.55 + motion_events * 0.35 + (1 if visual_signal_available else 0) * 0.10)
            / max(1.0, object_count + motion_events + 1.0)
        )
        motion_detection_rate = 1.0 if detection["motion_detected"] else 0.0
        image_traceability_score = self._bounded(
            0.35
            + (0.25 if visual_input.get("path") else 0.0)
            + (0.20 if visual_input.get("labels") else 0.0)
            + (0.20 if capture_result.get("capture_mode") else 0.0)
        )
        visual_grounding_score = self._bounded(
            0.30 * (1 if interface_state.get("camera_available") else 0)
            + 0.30 * (1 if visual_signal_available else 0)
            + 0.20 * visual_detection_rate
            + 0.20 * image_traceability_score
        )

        record = {
            "primitive": self.primitive,
            "schema_version": self.schema_version,
            "timestamp_utc": timestamp,
            "success": True,
            "observational_only": True,
            "no_code_modification_authorized": True,
            "non_closure_compliant": True,
            "visual_input": visual_input,
            "interface_state": interface_state,
            "capture_result": capture_result,
            "detected_objects": detection["detected_objects"],
            "motion_detected": detection["motion_detected"],
            "visual_events": vision_events,
            "captured_images": captured_images,
            "vision_detection_rate": visual_detection_rate,
            "motion_detection_rate": motion_detection_rate,
            "image_traceability_score": image_traceability_score,
            "visual_grounding_score": visual_grounding_score,
            "archive_ready": persist,
        }

        multimodal_result = self._optional_multimodal_integration(record, inputs)
        record["multimodal_integration"] = multimodal_result
        record["integrated_with_g2"] = bool(multimodal_result.get("success"))

        if persist:
            self._persist(record)

        return {
            "primitive": "visual_world_perception",
            "success": True,
            "timestamp_utc": timestamp,
            "captured_images": captured_images,
            "vision_events": vision_events,
            "detected_object_count": object_count,
            "detected_objects": detection["detected_objects"],
            "motion_detected": detection["motion_detected"],
            "vision_detection_rate": visual_detection_rate,
            "motion_detection_rate": motion_detection_rate,
            "image_traceability_score": image_traceability_score,
            "visual_grounding_score": visual_grounding_score,
            "camera_available": bool(interface_state.get("camera_available")),
            "visual_signal_available": visual_signal_available,
            "capture_mode": capture_result.get("capture_mode", "none"),
            "history_path": str(self.history_path),
            "latest_path": str(self.latest_path),
            "integrated_with_g2": record["integrated_with_g2"],
            "multimodal_integration": multimodal_result,
            "diagnostics": {
                "causal_scope": "functional_visual_observation_not_phenomenal_vision",
                "hardware_dependency_required": False,
                "opencv_required": False,
                "reversible": True,
                "storage_path": str(self.visual_dir),
            },
        }

    def _normalize_visual_input(self, inputs: dict[str, Any]) -> dict[str, Any]:
        image = inputs.get("image", inputs.get("visual", {}))
        if not isinstance(image, dict):
            image = {"raw": image}

        labels = image.get("labels") or image.get("objects") or inputs.get("labels") or []
        if isinstance(labels, str):
            labels = [labels]
        labels = [str(x).strip() for x in labels if str(x).strip()]

        path = image.get("path") or inputs.get("image_path") or inputs.get("frame_path")
        path_exists = False
        file_size = 0
        file_hash = None
        if path:
            try:
                p = Path(path).expanduser()
                path_exists = p.exists() and p.is_file()
                if path_exists:
                    file_size = p.stat().st_size
                    file_hash = self._hash_file(p)
            except Exception:
                path_exists = False

        motion = bool(
            image.get("motion_detected", inputs.get("motion_detected", False))
            or image.get("motion", False)
        )

        return {
            "image_active": bool(labels or path or motion or image),
            "labels": labels,
            "path": str(path) if path else None,
            "path_exists": path_exists,
            "file_size_bytes": file_size,
            "file_hash": file_hash,
            "motion_hint": motion,
            "source": str(image.get("source", inputs.get("source", "synthetic_or_passive"))),
        }

    def _read_embodied_interface(self, inputs: dict[str, Any]) -> dict[str, Any]:
        explicit = inputs.get("interface_state")
        if isinstance(explicit, dict):
            camera_available = bool(
                explicit.get("camera_available")
                or explicit.get("camera")
                or "camera" in explicit.get("active_interface_kinds", [])
            )
            return {
                "camera_available": camera_available,
                "source": "provided_interface_state",
                "raw": explicit,
            }

        try:
            from ontology.embodied_world_interface import EmbodiedWorldInterface

            embodied = EmbodiedWorldInterface().step()
            active = embodied.get("active_interface_kinds", [])
            summary = embodied.get("interface_summary", {})
            return {
                "camera_available": "camera" in active or bool(summary.get("camera", {}).get("active")),
                "source": "embodied_world_interface",
                "raw": embodied,
            }
        except Exception as exc:
            return {
                "camera_available": False,
                "source": "fallback",
                "error": repr(exc),
                "raw": {},
            }

    def _capture_best_effort(
        self,
        inputs: dict[str, Any],
        interface_state: dict[str, Any],
    ) -> dict[str, Any]:
        if inputs.get("capture") is False:
            return {
                "capture_attempted": False,
                "image_available": False,
                "capture_mode": "disabled_by_input",
            }

        simulated = inputs.get("simulated_frame") or inputs.get("image") or inputs.get("visual")
        if simulated:
            return {
                "capture_attempted": True,
                "image_available": True,
                "capture_mode": "simulated_or_supplied_frame",
            }

        path = inputs.get("image_path") or inputs.get("frame_path")
        if path and Path(path).expanduser().exists():
            return {
                "capture_attempted": True,
                "image_available": True,
                "capture_mode": "file_path",
            }

        if interface_state.get("camera_available"):
            return {
                "capture_attempted": True,
                "image_available": False,
                "capture_mode": "camera_available_no_forced_capture",
                "reason": "physical capture is not attempted unless explicit frame is provided",
            }

        return {
            "capture_attempted": False,
            "image_available": False,
            "capture_mode": "no_visual_source_available",
        }

    def _detect_visual_events(
        self,
        visual_input: dict[str, Any],
        capture_result: dict[str, Any],
    ) -> dict[str, Any]:
        labels = list(dict.fromkeys(visual_input.get("labels", [])))
        if visual_input.get("path_exists") and not labels:
            labels.append("image_file")
        if capture_result.get("image_available") and not labels:
            labels.append("visual_frame")

        motion_detected = bool(visual_input.get("motion_hint"))
        return {
            "detected_objects": labels,
            "motion_detected": motion_detected,
        }

    def _optional_multimodal_integration(
        self,
        record: dict[str, Any],
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        if inputs.get("integrate_with_g2") is False:
            return {"success": False, "reason": "disabled_by_input"}
        try:
            from ontology.multimodal_perception_engine import MultimodalPerceptionEngine

            result = MultimodalPerceptionEngine().step(
                {
                    "image": {
                        "labels": record.get("detected_objects", []),
                        "motion_detected": record.get("motion_detected", False),
                        "source": "visual_world_perception",
                    },
                    "system": {
                        "visual_events": record.get("visual_events", 0),
                        "vision_detection_rate": record.get("vision_detection_rate", 0.0),
                    },
                },
                persist=bool(inputs.get("persist_multimodal", False)),
            )
            return {
                "success": bool(result.get("success")),
                "active_modalities": result.get("active_modalities", []),
                "fusion_quality_score": result.get("fusion_quality_score", 0.0),
            }
        except Exception as exc:
            return {"success": False, "error": repr(exc)}

    def _persist(self, record: dict[str, Any]) -> None:
        self.visual_dir.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        self.latest_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _hash_file(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()[:16]

    def _bounded(self, value: float) -> float:
        try:
            value = float(value)
        except Exception:
            value = 0.0
        return max(0.0, min(1.0, value))

    def _now(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
