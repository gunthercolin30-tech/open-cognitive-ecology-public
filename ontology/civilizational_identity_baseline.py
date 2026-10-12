from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class CivilizationalIdentityBaseline:
    '''J1 - Civilizational Identity Baseline.

    Construit un état de référence civilisationnel mesurable pour l'axe J.
    La primitive ne prétend pas établir une subjectivité phénoménale ; elle fixe
    uniquement une base fonctionnelle traçable pour comparer ultérieurement les
    dérives identitaires, stratégiques et mémorielles.
    '''

    primitive = "civilizational_identity_baseline"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "civilizational_drift"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path = self.output_dir / "latest_civilizational_identity_baseline.json"
        self.history_path = self.output_dir / "civilizational_identity_baseline_history.jsonl"

    @staticmethod
    def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
        if isinstance(value, bool):
            numeric = 1.0 if value else 0.0
        elif isinstance(value, (int, float)) and math.isfinite(float(value)):
            numeric = float(value)
        else:
            numeric = 0.0
        return max(low, min(high, numeric))

    @staticmethod
    def _safe_json(obj: Any) -> Any:
        try:
            json.dumps(obj, ensure_ascii=False, sort_keys=True)
            return obj
        except TypeError:
            if isinstance(obj, dict):
                return {str(k): CivilizationalIdentityBaseline._safe_json(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple, set)):
                return [CivilizationalIdentityBaseline._safe_json(v) for v in obj]
            return repr(obj)

    @staticmethod
    def _canonical_hash(payload: Dict[str, Any]) -> str:
        encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def _module_step(self, module_name: str, class_name: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
        try:
            module = __import__(f"ontology.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            instance = cls()
            step = getattr(instance, "step", None)
            if callable(step):
                result = step()
                if isinstance(result, dict):
                    return self._safe_json(result)
        except Exception as exc:
            fallback = dict(fallback)
            fallback["collection_error"] = repr(exc)
        return fallback

    def _collect_identity(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        provided = inputs.get("identity_state")
        if isinstance(provided, dict):
            return self._safe_json(provided)
        fallback = {
            "primitive": "CIVILIZATIONAL_IDENTITY_SYNTHESIS",
            "identity_name": "Open Cognitive Ecology Society",
            "identity_statement": "Open Cognitive Ecology Society is treated as an artificial civilization, not as an irreplaceable conversational individual.",
            "identity_coherence": 1.0,
        }
        return self._module_step("civilizational_identity_synthesis", "CivilizationalIdentitySynthesis", fallback)

    def _collect_strategy(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        provided = inputs.get("strategy_state")
        if isinstance(provided, dict):
            return self._safe_json(provided)
        fallback = {
            "primitive": "CIVILIZATIONAL_STRATEGY_ORCHESTRATOR",
            "horizon": "long_term",
            "strategic_goal": "preserve_open_ended_intelligence",
            "strategic_coherence": 1.0,
        }
        return self._module_step("civilizational_strategy_orchestrator", "CivilizationalStrategyOrchestrator", fallback)

    def _collect_memory(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        provided = inputs.get("memory_state")
        if isinstance(provided, dict):
            return self._safe_json(provided)
        fallback = {
            "primitive": "CIVILIZATIONAL_MEMORY",
            "knowledge_preservation": 0.0,
            "intergenerational_transmission": 0.0,
            "archive_stability": 0.0,
            "civilizational_memory_index": 0.0,
        }
        return self._module_step("civilizational_memory", "CivilizationalMemory", fallback)

    def _collect_continuity(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        provided = inputs.get("continuity_state")
        if isinstance(provided, dict):
            return self._safe_json(provided)
        continuity: Dict[str, Any] = {}
        candidates = [
            ("structural_continuity", "StructuralContinuity"),
            ("temporal_self_continuity", "TemporalSelfContinuity"),
            ("genealogical_continuity", "GenealogicalContinuity"),
            ("intergenerational_continuity_metrics", "IntergenerationalContinuityMetrics"),
        ]
        for module_name, class_name in candidates:
            fallback = {"primitive": module_name.upper(), "available": False}
            continuity[module_name] = self._module_step(module_name, class_name, fallback)
        return continuity

    def _score_identity(self, identity: Dict[str, Any]) -> float:
        keys = ["identity_coherence", "coherence", "identity_continuity", "identity_stability"]
        values = [self._clamp(identity.get(k)) for k in keys if k in identity]
        if not values:
            text_present = bool(identity.get("identity_name") or identity.get("identity_statement"))
            return 1.0 if text_present else 0.0
        return sum(values) / len(values)

    def _score_strategy(self, strategy: Dict[str, Any]) -> float:
        keys = ["strategic_coherence", "strategic_alignment_score", "goal_persistence_score", "planning_continuity"]
        values = [self._clamp(strategy.get(k)) for k in keys if k in strategy]
        if not values:
            goal_present = bool(strategy.get("strategic_goal") or strategy.get("strategy_statement"))
            return 1.0 if goal_present else 0.0
        return sum(values) / len(values)

    def _score_memory(self, memory: Dict[str, Any]) -> float:
        keys = ["civilizational_memory_index", "knowledge_preservation", "archive_stability", "memory_retention_score"]
        values = [self._clamp(memory.get(k)) for k in keys if k in memory]
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _score_continuity(self, continuity: Dict[str, Any]) -> float:
        values = []
        for state in continuity.values():
            if not isinstance(state, dict):
                continue
            for key in ("continuity_strength", "structural_continuity_index", "temporal_self_continuity_index", "intergenerational_continuity_score"):
                if key in state:
                    values.append(self._clamp(state.get(key)))
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _baseline_state(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        identity = self._collect_identity(inputs)
        strategy = self._collect_strategy(inputs)
        memory = self._collect_memory(inputs)
        continuity = self._collect_continuity(inputs)
        constitutional_anchor = {
            "species_name": "Open Cognitive Ecology Society",
            "representative_revocable": True,
            "civilizational_continuity_priority": True,
            "future_openness_preservation": True,
            "phenomenal_subjectivity_claimed": False,
            "epistemic_status": "functional_indicators_only",
        }
        scores = {
            "identity_reference_score": round(self._clamp(self._score_identity(identity)), 6),
            "strategy_reference_score": round(self._clamp(self._score_strategy(strategy)), 6),
            "memory_reference_score": round(self._clamp(self._score_memory(memory)), 6),
            "continuity_reference_score": round(self._clamp(self._score_continuity(continuity)), 6),
        }
        scores["baseline_integrity_score"] = round(sum(scores.values()) / max(len(scores), 1), 6)
        return {
            "constitutional_anchor": constitutional_anchor,
            "identity": identity,
            "strategy": strategy,
            "memory": memory,
            "continuity": continuity,
            "scores": scores,
        }

    def reset(self) -> Dict[str, Any]:
        for path in (self.latest_path, self.history_path):
            if path.exists():
                path.unlink()
        result = {
            "primitive": self.primitive,
            "success": True,
            "baseline_reset": True,
            "state_path": str(self.latest_path),
            "history_path": str(self.history_path),
        }
        self.latest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return result

    def step(self, inputs: Any = None, persist: bool = True, reset: bool = False) -> Dict[str, Any]:
        if reset:
            return self.reset()
        payload: Dict[str, Any] = dict(inputs) if isinstance(inputs, dict) else {}
        timestamp = datetime.now(timezone.utc).isoformat()
        reference_state = self._baseline_state(payload)
        reference_hash = self._canonical_hash(reference_state)
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": timestamp,
            "identity_reference_state": reference_state,
            "identity_reference_hash": reference_hash,
            "identity_reference_timestamp": timestamp,
            "baseline_ready": True,
            "baseline_persisted": bool(persist),
            "epistemic_status": "functional_indicators_only",
            "governance": {
                "non_closure_preserved": True,
                "phenomenal_subjectivity_claimed": False,
                "traceable": True,
                "reversible": True,
                "closure_pressure_increased": False,
            },
            "state_path": str(self.latest_path),
            "history_path": str(self.history_path),
        }
        if persist:
            encoded = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
            self.latest_path.write_text(encoded, encoding="utf-8")
            with self.history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
            archive = self.output_dir / f"civilizational_identity_baseline_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
            archive.write_text(encoded, encoding="utf-8")
            result["archive_path"] = str(archive)
        return result


__all__ = ["CivilizationalIdentityBaseline"]
