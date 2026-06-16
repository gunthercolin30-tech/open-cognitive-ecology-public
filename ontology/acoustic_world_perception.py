"""
G4 — Acoustic World Perception.

This module provides governed acoustic perception for Open Cognitive Ecology.
It does not claim phenomenological hearing. It implements functional,
measurable, traceable acoustic observation: microphone availability,
sound-event detection, optional transcription, archival persistence and
multimodal integration readiness.
"""

from __future__ import annotations

import json
import math
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AcousticWorldPerception:
    """
    Functional acoustic perception layer.

    The module is deliberately dependency-light. It accepts simulated or
    externally supplied audio observations, detects simple sound-event and
    transcription evidence, archives observations, and exposes metrics usable
    by multimodal perception and later environmental modeling.
    """

    primitive = "acoustic_world_perception"
    schema_version = "G4.acoustic.v1"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.archive_dir = self.root / "acoustic_world_perception"
        self.history_path = self.archive_dir / "acoustic_world_perception_history.jsonl"
        self.latest_path = self.archive_dir / "latest_acoustic_world_perception.json"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    @staticmethod
    def _safe_float(value: Any, default: float = 0.0) -> float:
        try:
            if value is None:
                return default
            number = float(value)
            if math.isnan(number) or math.isinf(number):
                return default
            return number
        except Exception:
            return default

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, set):
            return list(value)
        return [value]

    def _detect_microphone_from_g1(self) -> dict[str, Any]:
        """Best-effort microphone availability from embodied_world_interface."""
        try:
            from ontology.embodied_world_interface import EmbodiedWorldInterface

            g1 = EmbodiedWorldInterface(self.root).step()
            summary = g1.get("interface_summary", {}) if isinstance(g1, dict) else {}
            microphone_summary = summary.get("microphone", {}) if isinstance(summary, dict) else {}
            active_kinds = g1.get("active_interface_kinds", []) if isinstance(g1, dict) else []
            detected = bool(
                microphone_summary.get("detected")
                or microphone_summary.get("active")
                or "microphone" in active_kinds
            )
            return {
                "available": detected,
                "source": "embodied_world_interface",
                "raw": microphone_summary,
            }
        except Exception as exc:
            return {
                "available": False,
                "source": "embodied_world_interface_unavailable",
                "error": exc.__class__.__name__,
            }

    def _normalize_audio_input(self, inputs: Any) -> dict[str, Any]:
        if inputs is None:
            return {}
        if not isinstance(inputs, dict):
            return {"audio": inputs}
        audio = inputs.get("audio", inputs)
        if isinstance(audio, dict):
            return dict(audio)
        return {"raw_audio": audio}

    def _extract_audio_features(self, audio: dict[str, Any]) -> dict[str, Any]:
        transcript = str(audio.get("transcript") or audio.get("text") or "").strip()
        events = [str(e).strip() for e in self._as_list(audio.get("events") or audio.get("sound_events")) if str(e).strip()]

        amplitude = self._safe_float(audio.get("amplitude") or audio.get("volume") or audio.get("level"), 0.0)
        duration_seconds = self._safe_float(audio.get("duration_seconds") or audio.get("duration"), 0.0)
        sample_rate = self._safe_float(audio.get("sample_rate") or audio.get("sample_rate_hz"), 0.0)
        speech_detected = bool(audio.get("speech_detected") or transcript)
        noise_detected = bool(audio.get("noise_detected") or amplitude > 0.05)

        if speech_detected and "speech" not in events:
            events.append("speech")
        if noise_detected and not events:
            events.append("sound")

        audio_supplied = bool(audio) and any(
            key in audio
            for key in (
                "transcript",
                "text",
                "events",
                "sound_events",
                "amplitude",
                "volume",
                "level",
                "duration_seconds",
                "duration",
                "sample_rate",
                "speech_detected",
                "noise_detected",
                "raw_audio",
            )
        )

        transcribed_events = 1 if transcript else 0
        event_count = len(events) + transcribed_events
        if audio_supplied and event_count == 0:
            event_count = 1

        evidence_slots = 5
        evidence_score = sum(
            1 for flag in [audio_supplied, bool(events), bool(transcript), speech_detected, noise_detected]
            if flag
        ) / evidence_slots

        acoustic_detection_rate = max(0.0, min(1.0, evidence_score))
        acoustic_grounding_score = max(0.0, min(1.0, (acoustic_detection_rate + (1.0 if event_count else 0.0)) / 2.0))

        return {
            "audio_supplied": audio_supplied,
            "transcript": transcript,
            "transcribed_events": transcribed_events,
            "sound_events": events,
            "audio_events": event_count,
            "amplitude": amplitude,
            "duration_seconds": duration_seconds,
            "sample_rate": sample_rate,
            "speech_detected": speech_detected,
            "noise_detected": noise_detected,
            "acoustic_detection_rate": acoustic_detection_rate,
            "acoustic_grounding_score": acoustic_grounding_score,
        }

    def _integrate_with_g2(self, record: dict[str, Any], persist: bool) -> dict[str, Any]:
        try:
            from ontology.multimodal_perception_engine import MultimodalPerceptionEngine

            g2_input = {
                "audio": {
                    "transcript": record.get("transcript", ""),
                    "events": record.get("sound_events", []),
                    "speech_detected": record.get("speech_detected", False),
                    "noise_detected": record.get("noise_detected", False),
                },
                "system": {
                    "source": self.primitive,
                    "timestamp_utc": record.get("timestamp_utc"),
                },
            }
            result = MultimodalPerceptionEngine(self.root).step(g2_input, persist=persist)
            return {
                "success": bool(result.get("success")),
                "active_modalities": result.get("active_modalities", []),
                "multimodal_observation_count": result.get("multimodal_observation_count", 0),
            }
        except Exception as exc:
            return {"success": False, "error": exc.__class__.__name__}

    def _persist(self, record: dict[str, Any]) -> None:
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        self.latest_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    def _history_count(self) -> int:
        if not self.history_path.exists():
            return 0
        try:
            return sum(1 for line in self.history_path.read_text(encoding="utf-8").splitlines() if line.strip())
        except Exception:
            return 0

    def step(self, inputs: Any | None = None, persist: bool = True) -> dict[str, Any]:
        audio = self._normalize_audio_input(inputs)
        mic = self._detect_microphone_from_g1()
        features = self._extract_audio_features(audio)

        prior_count = self._history_count()
        timestamp = self._utc_now()

        record: dict[str, Any] = {
            "primitive": self.primitive,
            "schema_version": self.schema_version,
            "timestamp_utc": timestamp,
            "success": True,
            "operational": bool(mic.get("available") or features["audio_supplied"]),
            "microphone_available": bool(mic.get("available")),
            "microphone_source": mic.get("source"),
            "audio_events": int(features["audio_events"]),
            "transcribed_events": int(features["transcribed_events"]),
            "sound_events": features["sound_events"],
            "transcript": features["transcript"],
            "speech_detected": bool(features["speech_detected"]),
            "noise_detected": bool(features["noise_detected"]),
            "amplitude": features["amplitude"],
            "duration_seconds": features["duration_seconds"],
            "sample_rate": features["sample_rate"],
            "acoustic_detection_rate": features["acoustic_detection_rate"],
            "acoustic_grounding_score": features["acoustic_grounding_score"],
            "acoustic_observation_count": prior_count + 1 if persist else prior_count,
            "environment": {
                "platform": platform.system(),
                "python_version": platform.python_version(),
            },
            "diagnostics": {
                "phenomenology_claimed": False,
                "functional_acoustic_perception": True,
                "observational_only": True,
                "no_uncontrolled_recording": True,
                "requires_explicit_audio_input_for_content": True,
                "non_closure_compliant": True,
            },
            "history_path": str(self.history_path),
            "latest_path": str(self.latest_path),
        }

        record["multimodal_integration"] = self._integrate_with_g2(record, persist=persist)

        if persist:
            self._persist(record)
            record["acoustic_observation_count"] = self._history_count()

        return record
