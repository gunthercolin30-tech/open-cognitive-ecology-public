from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ParadigmEvolutionObservatory:
    '''I7 - Paradigm Evolution Observatory.

    Historise les états paradigmatiques produits par I1-I6 et calcule
    des indicateurs longitudinaux mesurables : paradigm_history_length,
    transition_density, historical_regime_sequence et paradigm_evolution_rate.
    Cette primitive mesure uniquement des propriétés fonctionnelles traçables.
    '''

    primitive = "paradigm_evolution_observatory"
    taxonomy = ("stability", "transition", "rupture", "expansion", "collapse")

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "paradigm_surveillance"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.history_path = self.output_dir / "paradigm_evolution_history.jsonl"
        self.latest_path = self.output_dir / "latest_paradigm_evolution_observatory.json"

    @staticmethod
    def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
        return max(low, min(high, float(value)))

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, (int, float)) and math.isfinite(float(value)):
            return float(value)
        return None

    def _load_history(self) -> List[Dict[str, Any]]:
        if not self.history_path.exists():
            return []
        records: List[Dict[str, Any]] = []
        for line in self.history_path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                records.append(obj)
        return records

    def _append_history(self, record: Dict[str, Any]) -> None:
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

    def reset_history(self) -> Dict[str, Any]:
        if self.history_path.exists():
            self.history_path.unlink()
        result = {
            "primitive": self.primitive,
            "success": True,
            "history_reset": True,
            "history_path": str(self.history_path),
        }
        self.latest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return result

    def _extract_from_inputs(self, inputs: Any) -> Tuple[Dict[str, Any], str]:
        if inputs is None:
            return {}, "empty"
        if isinstance(inputs, dict):
            return dict(inputs), "precomputed_indicators"
        if isinstance(inputs, list):
            observations = [x for x in inputs if isinstance(x, dict)]
            if not observations:
                return {"observations": []}, "observation_series_empty"
            latest = dict(observations[-1])
            latest["observations"] = observations
            return latest, "observation_series"
        return {}, "unsupported_input"

    def _classify_if_needed(self, data: Dict[str, Any], input_mode: str) -> Dict[str, Any]:
        if data.get("current_paradigm") in self.taxonomy:
            return data
        try:
            from ontology.paradigm_classification_engine import ParadigmClassificationEngine
            payload: Any = data.get("observations") if input_mode == "observation_series" else data
            classification = ParadigmClassificationEngine(root=self.root).step(payload, persist=False)
            if isinstance(classification, dict):
                data = dict(data)
                data["classification_result"] = classification
                if classification.get("current_paradigm") in self.taxonomy:
                    data["current_paradigm"] = classification.get("current_paradigm")
                if "classification_confidence" in classification:
                    data["classification_confidence"] = classification.get("classification_confidence")
        except Exception as exc:
            data = dict(data)
            data["classification_error"] = repr(exc)
        return data

    def _event_record(self, data: Dict[str, Any], input_mode: str) -> Dict[str, Any]:
        current = data.get("current_paradigm")
        if current not in self.taxonomy:
            current = "stability"
        confidence = self._to_float(data.get("classification_confidence"))
        if confidence is None and isinstance(data.get("classification_result"), dict):
            confidence = self._to_float(data["classification_result"].get("classification_confidence"))
        if confidence is None:
            confidence = 0.0
        indicators = {
            "shift_signal_strength": self._to_float(data.get("shift_signal_strength")) or 0.0,
            "transition_probability": self._to_float(data.get("transition_probability")) or 0.0,
            "break_significance": self._to_float(data.get("break_significance")) or 0.0,
            "constraint_shift_index": self._to_float(data.get("constraint_shift_index")) or 0.0,
            "emergence_probability": self._to_float(data.get("emergence_probability")) or 0.0,
            "novelty_index": self._to_float(data.get("novelty_index")) or 0.0,
        }
        return {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "current_paradigm": current,
            "classification_confidence": round(self._clamp(confidence), 6),
            "input_mode": input_mode,
            "indicators": {k: round(self._clamp(v), 6) for k, v in indicators.items()},
        }

    def _summarize(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        paradigms = [str(r.get("current_paradigm", "stability")) for r in history]
        transitions = sum(1 for a, b in zip(paradigms, paradigms[1:]) if a != b)
        history_length = len(history)
        transition_density = transitions / max(history_length - 1, 1) if history_length > 1 else 0.0
        current = paradigms[-1] if paradigms else "stability"
        previous = paradigms[-2] if len(paradigms) > 1 else None
        counts: Dict[str, int] = {name: paradigms.count(name) for name in self.taxonomy}
        non_stable = sum(1 for p in paradigms if p != "stability")
        evolution_rate = non_stable / max(history_length, 1)
        confidence_values = [self._to_float(r.get("classification_confidence")) or 0.0 for r in history]
        mean_confidence = sum(confidence_values) / max(len(confidence_values), 1)
        return {
            "paradigm_history_length": history_length,
            "transition_count": transitions,
            "transition_density": round(self._clamp(transition_density), 6),
            "paradigm_evolution_rate": round(self._clamp(evolution_rate), 6),
            "historical_regime_sequence": paradigms[-10:],
            "current_paradigm": current,
            "previous_paradigm": previous,
            "paradigm_counts": counts,
            "mean_classification_confidence": round(self._clamp(mean_confidence), 6),
        }

    def step(self, inputs: Any = None, persist: bool = True, reset: bool = False) -> Dict[str, Any]:
        if reset:
            return self.reset_history()
        data, input_mode = self._extract_from_inputs(inputs)
        data = self._classify_if_needed(data, input_mode)
        event = self._event_record(data, input_mode)
        history_after = self._load_history() + [event]
        summary = self._summarize(history_after)
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "input_mode": input_mode,
            "latest_event": event,
            **summary,
            "paradigm_evolution_observatory_ready": True,
            "epistemic_status": "functional_indicators_only",
            "governance": {
                "non_closure_preserved": True,
                "phenomenal_subjectivity_claimed": False,
                "traceable": True,
                "reversible": True,
            },
            "history_path": str(self.history_path),
            "state_path": str(self.latest_path),
        }
        if persist:
            self._append_history(event)
            archive = self.output_dir / f"paradigm_evolution_observatory_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
            payload = json.dumps(result, indent=2, ensure_ascii=False)
            self.latest_path.write_text(payload, encoding="utf-8")
            archive.write_text(payload, encoding="utf-8")
            result["archive_path"] = str(archive)
        return result


__all__ = ["ParadigmEvolutionObservatory"]
