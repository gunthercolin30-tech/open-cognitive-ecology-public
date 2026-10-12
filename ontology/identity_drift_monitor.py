from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple


class IdentityDriftMonitor:
    """J2 - Identity Drift Monitor.

    Mesure la dérive identitaire fonctionnelle d'Open Cognitive Ecology à partir
    d'une référence produite par J1. La primitive compare des états mesurables :
    ancrage constitutionnel, structure identitaire, scores de référence et
    continuité déclarée. Elle ne formule aucune revendication de subjectivité
    phénoménale.
    """

    primitive = "identity_drift_monitor"

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "civilizational_drift"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.latest_path = self.output_dir / "latest_identity_drift_monitor.json"
        self.history_path = self.output_dir / "identity_drift_monitor_history.jsonl"
        self.baseline_path = self.output_dir / "latest_civilizational_identity_baseline.json"

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
                return {str(k): IdentityDriftMonitor._safe_json(v) for k, v in obj.items()}
            if isinstance(obj, (list, tuple, set)):
                return [IdentityDriftMonitor._safe_json(v) for v in obj]
            return repr(obj)

    @staticmethod
    def _canonical_hash(payload: Any) -> str:
        safe = IdentityDriftMonitor._safe_json(payload)
        encoded = json.dumps(safe, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    @staticmethod
    def _tokens(payload: Any) -> set[str]:
        safe = IdentityDriftMonitor._safe_json(payload)
        text = json.dumps(safe, ensure_ascii=False, sort_keys=True).lower()
        token = ""
        tokens: set[str] = set()
        for char in text:
            if char.isalnum() or char in {"_", "-"}:
                token += char
            else:
                if len(token) > 1:
                    tokens.add(token)
                token = ""
        if len(token) > 1:
            tokens.add(token)
        return tokens

    @classmethod
    def _jaccard(cls, left: Any, right: Any) -> float:
        a = cls._tokens(left)
        b = cls._tokens(right)
        if not a and not b:
            return 1.0
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    @staticmethod
    def _extract_reference_state(payload: Dict[str, Any]) -> Dict[str, Any]:
        state = payload.get("identity_reference_state")
        if isinstance(state, dict):
            return state
        if any(k in payload for k in ("constitutional_anchor", "identity", "strategy", "memory", "continuity", "scores")):
            return payload
        return {}

    def _load_reference_payload(self) -> Dict[str, Any]:
        if self.baseline_path.exists():
            try:
                data = json.loads(self.baseline_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        try:
            from ontology.civilizational_identity_baseline import CivilizationalIdentityBaseline
            data = CivilizationalIdentityBaseline(root=self.root).step(persist=True)
            return data if isinstance(data, dict) else {}
        except Exception as exc:
            return {
                "primitive": "civilizational_identity_baseline",
                "success": False,
                "collection_error": repr(exc),
                "identity_reference_state": self._fallback_state(),
            }

    def _collect_current_payload(self, provided: Any = None) -> Dict[str, Any]:
        if isinstance(provided, dict):
            return self._safe_json(provided)
        try:
            from ontology.civilizational_identity_baseline import CivilizationalIdentityBaseline
            data = CivilizationalIdentityBaseline(root=self.root).step(persist=False)
            return data if isinstance(data, dict) else {}
        except Exception as exc:
            return {
                "primitive": "civilizational_identity_baseline",
                "success": False,
                "collection_error": repr(exc),
                "identity_reference_state": self._fallback_state(),
            }

    @staticmethod
    def _fallback_state() -> Dict[str, Any]:
        return {
            "constitutional_anchor": {
                "species_name": "Open Cognitive Ecology Society",
                "representative_revocable": True,
                "civilizational_continuity_priority": True,
                "future_openness_preservation": True,
                "phenomenal_subjectivity_claimed": False,
                "epistemic_status": "functional_indicators_only",
            },
            "identity": {
                "identity_name": "Open Cognitive Ecology Society",
                "identity_statement": "Artificial civilization identity baseline unavailable; fallback identity used.",
                "identity_coherence": 1.0,
            },
            "scores": {
                "identity_reference_score": 1.0,
                "strategy_reference_score": 1.0,
                "memory_reference_score": 0.0,
                "continuity_reference_score": 0.0,
                "baseline_integrity_score": 0.5,
            },
        }

    @staticmethod
    def _score_distance(reference_scores: Dict[str, Any], current_scores: Dict[str, Any]) -> float:
        keys = sorted(set(reference_scores) | set(current_scores))
        numeric_keys = []
        distances = []
        for key in keys:
            rv = reference_scores.get(key)
            cv = current_scores.get(key)
            if isinstance(rv, (int, float, bool)) or isinstance(cv, (int, float, bool)):
                numeric_keys.append(key)
                distances.append(abs(IdentityDriftMonitor._clamp(rv) - IdentityDriftMonitor._clamp(cv)))
        if not numeric_keys:
            return 0.0
        return sum(distances) / len(distances)

    @staticmethod
    def _anchor_preservation(reference_anchor: Dict[str, Any], current_anchor: Dict[str, Any]) -> Tuple[float, list[str]]:
        if not reference_anchor:
            return 0.0, []
        preserved = []
        missing = []
        for key, ref_value in reference_anchor.items():
            if key in current_anchor and current_anchor.get(key) == ref_value:
                preserved.append(key)
            else:
                missing.append(key)
        return len(preserved) / max(len(reference_anchor), 1), missing

    @staticmethod
    def _mean(values: Iterable[float]) -> float:
        vals = [IdentityDriftMonitor._clamp(v) for v in values]
        if not vals:
            return 0.0
        return sum(vals) / len(vals)

    def _semantic_identity_drift(self, reference_state: Dict[str, Any], current_state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            from ontology.civilizational_semantic_drift import CivilizationalSemanticDrift
            lineage_semantics = {
                "reference": reference_state.get("identity", reference_state),
                "current": current_state.get("identity", current_state),
            }
            result = CivilizationalSemanticDrift().evaluate(lineage_semantics)
            if isinstance(result, dict):
                return self._safe_json(result)
        except Exception as exc:
            return {"semantic_drift_error": repr(exc), "civilizational_semantic_drift_index": 0.0}
        return {"civilizational_semantic_drift_index": 0.0}

    def evaluate(self, reference_payload: Any = None, current_payload: Any = None) -> Dict[str, Any]:
        reference_raw = reference_payload if isinstance(reference_payload, dict) else self._load_reference_payload()
        current_raw = self._collect_current_payload(current_payload)

        reference_state = self._extract_reference_state(reference_raw) or self._fallback_state()
        current_state = self._extract_reference_state(current_raw) or self._fallback_state()

        reference_hash = reference_raw.get("identity_reference_hash") if isinstance(reference_raw, dict) else None
        current_hash = self._canonical_hash(current_state)

        reference_anchor = reference_state.get("constitutional_anchor", {}) if isinstance(reference_state.get("constitutional_anchor"), dict) else {}
        current_anchor = current_state.get("constitutional_anchor", {}) if isinstance(current_state.get("constitutional_anchor"), dict) else {}
        anchor_score, missing_anchor_keys = self._anchor_preservation(reference_anchor, current_anchor)

        identity_similarity = self._jaccard(reference_state.get("identity", {}), current_state.get("identity", {}))
        structural_similarity = self._jaccard(reference_state, current_state)
        continuity_similarity = self._jaccard(reference_state.get("continuity", {}), current_state.get("continuity", {}))
        score_distance = self._score_distance(
            reference_state.get("scores", {}) if isinstance(reference_state.get("scores"), dict) else {},
            current_state.get("scores", {}) if isinstance(current_state.get("scores"), dict) else {},
        )
        semantic = self._semantic_identity_drift(reference_state, current_state)
        semantic_drift = self._clamp(semantic.get("civilizational_semantic_drift_index"))
        semantic_coherence = 1.0 - semantic_drift

        identity_coherence_score = self._mean([
            identity_similarity,
            structural_similarity,
            anchor_score,
            1.0 - score_distance,
            semantic_coherence,
        ])
        identity_continuity_score = self._mean([
            anchor_score,
            continuity_similarity,
            1.0 - score_distance,
            1.0 if reference_hash and reference_hash == current_hash else identity_similarity,
        ])
        identity_drift_score = 1.0 - self._mean([
            identity_coherence_score,
            identity_continuity_score,
            semantic_coherence,
        ])

        if identity_drift_score < 0.10:
            drift_regime = "stable_identity"
        elif identity_drift_score < 0.30:
            drift_regime = "minor_identity_drift"
        elif identity_drift_score < 0.60:
            drift_regime = "moderate_identity_drift"
        else:
            drift_regime = "critical_identity_drift"

        return {
            "reference_hash": reference_hash or self._canonical_hash(reference_state),
            "current_hash": current_hash,
            "hash_match": bool(reference_hash and reference_hash == current_hash),
            "anchor_preservation_score": round(self._clamp(anchor_score), 6),
            "missing_anchor_keys": missing_anchor_keys,
            "identity_similarity_score": round(self._clamp(identity_similarity), 6),
            "structural_similarity_score": round(self._clamp(structural_similarity), 6),
            "continuity_similarity_score": round(self._clamp(continuity_similarity), 6),
            "score_distance": round(self._clamp(score_distance), 6),
            "semantic_drift": semantic,
            "identity_drift_score": round(self._clamp(identity_drift_score), 6),
            "identity_coherence_score": round(self._clamp(identity_coherence_score), 6),
            "identity_continuity_score": round(self._clamp(identity_continuity_score), 6),
            "drift_regime": drift_regime,
        }

    def reset(self) -> Dict[str, Any]:
        for path in (self.latest_path, self.history_path):
            if path.exists():
                path.unlink()
        result = {
            "primitive": self.primitive,
            "success": True,
            "reset": True,
            "state_path": str(self.latest_path),
            "history_path": str(self.history_path),
        }
        self.latest_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return result

    def step(self, inputs: Any = None, persist: bool = True, reset: bool = False) -> Dict[str, Any]:
        if reset:
            return self.reset()
        payload = inputs if isinstance(inputs, dict) else {}
        reference_payload = payload.get("reference_state") or payload.get("reference_payload")
        current_payload = payload.get("current_state") or payload.get("current_payload") or payload.get("identity_state")
        metrics = self.evaluate(reference_payload=reference_payload, current_payload=current_payload)
        timestamp = datetime.now(timezone.utc).isoformat()
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": timestamp,
            "identity_drift_score": metrics["identity_drift_score"],
            "identity_coherence_score": metrics["identity_coherence_score"],
            "identity_continuity_score": metrics["identity_continuity_score"],
            "drift_regime": metrics["drift_regime"],
            "monitor_ready": True,
            "baseline_available": self.baseline_path.exists(),
            "metrics": metrics,
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
            archive = self.output_dir / f"identity_drift_monitor_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
            archive.write_text(encoded, encoding="utf-8")
            result["archive_path"] = str(archive)
        return result


__all__ = ["IdentityDriftMonitor"]
