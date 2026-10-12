
"""AT7 — prediction_validation_tracker.

Longitudinally tracks RF* prediction validation states. It records whether each
prediction is unknown, tested, validated, invalidated or ambiguous, while
preserving complete audit history, protocol links and experimental evidence.

The module is strictly functional and empirical: validation of predictions does
not constitute proof of phenomenal consciousness, qualia or subjectivity.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
VALID_STATUSES = {"unknown", "tested", "validated", "invalidated", "ambiguous"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _flt(x: Any, d: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return d
    return max(0.0, min(1.0, v))


def _lst(x: Any) -> List[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, tuple):
        return list(x)
    if isinstance(x, dict):
        return [x]
    return [x]


def _slug(x: Any) -> str:
    s = str(x or "unknown").lower()
    out: List[str] = []
    for c in s:
        if c.isalnum():
            out.append(c)
        elif out and out[-1] != "_":
            out.append("_")
    return "".join(out).strip("_") or "unknown"


class PredictionValidationTracker:
    primitive = "PREDICTION_VALIDATION_TRACKER"
    step_name = "AT7"
    public_schema_version = "1.0.0"
    status = "PREDICTION_VALIDATION_TRACKER_READY"
    allowed_statuses = sorted(VALID_STATUSES)
    epistemic_guards = {
        "consciousness_proven": False,
        "qualia_proven": False,
        "subjectivity_proven": False,
        "phenomenology_proven": False,
        "phenomenology_undetermined": True,
        "functional_conclusion_only": True,
        "allowed_scope": [
            "prediction_status_tracking",
            "experimental_evidence_history",
            "longitudinal_validation_audit",
            "functional_predictive_assessment",
        ],
        "blocked_scope": [
            "phenomenal_consciousness_proof",
            "qualia_proof",
            "subjectivity_proof",
            "ontological_final_closure",
        ],
    }

    def _load_previous(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for key, mod, cls in [
            ("at6_result", "ontology.unexpected_prediction_detector", "UnexpectedPredictionDetector"),
            ("at5_result", "ontology.falsification_protocol_generator", "FalsificationProtocolGenerator"),
            ("at4_result", "ontology.measurable_signature_builder", "MeasurableSignatureBuilder"),
            ("at3_result", "ontology.discriminative_prediction_engine", "DiscriminativePredictionEngine"),
            ("at2_result", "ontology.theorem_prediction_generator", "TheoremPredictionGenerator"),
        ]:
            try:
                module = __import__(mod, fromlist=[cls])
                out[key] = getattr(module, cls)().step(inputs={}, persist=False)
            except Exception:
                pass
        return out

    def _prediction_sources(self, inputs: Mapping[str, Any]) -> List[Mapping[str, Any]]:
        ctx = dict(inputs or {})
        if not any(k in ctx for k in ["prediction_events", "predictions", "unexpected_predictions", "falsification_protocols"]):
            ctx.update(self._load_previous())
        candidates: List[Any] = []
        for key in ["predictions", "prediction_events", "validation_records", "unexpected_predictions", "falsification_protocols", "measurable_signatures", "discriminative_predictions", "theorem_predictions"]:
            candidates += _lst(ctx.get(key))
        parent_map = [
            ("at6_result", "unexpected_predictions"),
            ("at5_result", "falsification_protocols"),
            ("at4_result", "measurable_signatures"),
            ("at3_result", "discriminative_predictions"),
            ("at2_result", "theorem_predictions"),
        ]
        for parent, child in parent_map:
            if isinstance(ctx.get(parent), Mapping):
                candidates += _lst(ctx[parent].get(child))
        records: List[Mapping[str, Any]] = []
        seen = set()
        for i, item in enumerate(candidates, 1):
            if not isinstance(item, Mapping):
                continue
            pid = str(item.get("prediction_id") or item.get("id") or item.get("protocol_id") or item.get("signature_id") or item.get("unexpected_prediction_id") or f"prediction_{i}")
            if pid in seen:
                continue
            seen.add(pid)
            records.append(item)
        if not records:
            records = [
                {"prediction_id": "synthetic_structural_prediction", "category": "structural", "prediction": "RF* structural prediction awaiting empirical test."},
                {"prediction_id": "synthetic_topological_prediction", "category": "topological", "prediction": "RF* topological prediction awaiting empirical test."},
            ]
        return records

    def _event_status(self, event: Mapping[str, Any]) -> str:
        raw = str(event.get("status") or event.get("validation_status") or "").lower().strip()
        if raw in VALID_STATUSES:
            return raw
        tested = bool(event.get("tested") or event.get("experiment_id") or event.get("evidence") or event.get("observed_value") is not None)
        validation_score = _flt(event.get("validation_score") or event.get("support_score") or event.get("evidence_score"), 0.0)
        falsification_score = _flt(event.get("falsification_score") or event.get("refutation_score"), 0.0)
        ambiguity_score = _flt(event.get("ambiguity_score") or event.get("uncertainty") or event.get("uncertainty_score"), 0.0)
        if falsification_score >= 0.67 and falsification_score > validation_score:
            return "invalidated"
        if validation_score >= 0.67 and validation_score > falsification_score:
            return "validated"
        if tested and ambiguity_score >= 0.45:
            return "ambiguous"
        if tested:
            return "tested"
        return "unknown"

    def _record(self, item: Mapping[str, Any], idx: int, existing_history: Mapping[str, Any]) -> Dict[str, Any]:
        pid = str(item.get("prediction_id") or item.get("id") or item.get("protocol_id") or item.get("signature_id") or item.get("unexpected_prediction_id") or f"prediction_{idx}")
        status = self._event_status(item)
        prev = existing_history.get(pid, {}) if isinstance(existing_history, Mapping) else {}
        previous_history = _lst(prev.get("history")) if isinstance(prev, Mapping) else []
        event = {
            "timestamp_utc": str(item.get("timestamp_utc") or item.get("date") or _now()),
            "status": status,
            "protocol_id": item.get("protocol_id") or item.get("source_protocol_id"),
            "experiment_id": item.get("experiment_id"),
            "evidence_id": item.get("evidence_id"),
            "validation_score": _flt(item.get("validation_score") or item.get("support_score") or item.get("evidence_score"), 0.0),
            "falsification_score": _flt(item.get("falsification_score") or item.get("refutation_score"), 0.0),
            "ambiguity_score": _flt(item.get("ambiguity_score") or item.get("uncertainty") or item.get("uncertainty_score"), 0.0),
            "notes": str(item.get("notes") or item.get("result") or "functional_tracking_event"),
        }
        history = previous_history + [event]
        return {
            "tracking_id": f"AT7-{idx:04d}-{_slug(pid)}",
            "prediction_id": pid,
            "prediction": item.get("prediction") or item.get("claim") or item.get("description") or f"Prediction {pid}",
            "category": item.get("category") or item.get("prediction_category") or "uncategorized",
            "current_status": status,
            "previous_status": prev.get("current_status") if isinstance(prev, Mapping) else None,
            "protocol_id": event["protocol_id"],
            "experiment_id": event["experiment_id"],
            "first_seen_utc": prev.get("first_seen_utc") if isinstance(prev, Mapping) and prev.get("first_seen_utc") else event["timestamp_utc"],
            "last_updated_utc": event["timestamp_utc"],
            "history_length": len(history),
            "history": history,
            "auditability": {
                "has_protocol_link": bool(event["protocol_id"]),
                "has_experiment_link": bool(event["experiment_id"]),
                "status_in_allowed_set": status in VALID_STATUSES,
                "functional_scope_only": True,
            },
        }

    def _load_persisted_history(self) -> Dict[str, Any]:
        path = ROOT / "predictive_theory" / "validation" / "latest_prediction_validation_tracker.json"
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return {str(r.get("prediction_id")): r for r in _lst(data.get("tracked_predictions")) if isinstance(r, Mapping)}
        except Exception:
            return {}

    def _summary(self, records: List[Mapping[str, Any]]) -> Dict[str, Any]:
        counts = {s: 0 for s in self.allowed_statuses}
        for r in records:
            st = str(r.get("current_status") or "unknown")
            counts[st] = counts.get(st, 0) + 1
        total = len(records) or 1
        tested_total = total - counts.get("unknown", 0)
        return {
            "tracked_prediction_count": len(records),
            "status_counts": counts,
            "tested_prediction_count": tested_total,
            "validated_prediction_count": counts.get("validated", 0),
            "invalidated_prediction_count": counts.get("invalidated", 0),
            "ambiguous_prediction_count": counts.get("ambiguous", 0),
            "empirical_coverage": round(tested_total / total, 3),
            "validation_ratio": round(counts.get("validated", 0) / total, 3),
            "refutation_ratio": round(counts.get("invalidated", 0) / total, 3),
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        ctx = dict(inputs or {})
        history = ctx.get("existing_history") if isinstance(ctx.get("existing_history"), Mapping) else self._load_persisted_history()
        sources = self._prediction_sources(ctx)
        tracked = [self._record(item, i, history) for i, item in enumerate(sources, 1)]
        summary = self._summary(tracked)
        outpath = ROOT / "predictive_theory" / "validation" / "latest_prediction_validation_tracker.json"
        persisted = False
        if persist:
            outpath.parent.mkdir(parents=True, exist_ok=True)
            outpath.write_text(json.dumps({
                "primitive": self.primitive,
                "step": self.step_name,
                "status": self.status,
                "tracked_predictions": tracked,
                "validation_summary": summary,
                "timestamp_utc": _now(),
            }, indent=2, sort_keys=True), encoding="utf-8")
            persisted = True
        return {
            "primitive": self.primitive,
            "step": self.step_name,
            "public_schema_version": self.public_schema_version,
            "status": self.status,
            "prediction_count": len(sources),
            "tracked_prediction_count": len(tracked),
            "tracked_predictions": tracked,
            "prediction_validation_history": {r["prediction_id"]: r["history"] for r in tracked},
            "status_counts": summary["status_counts"],
            "validation_summary": summary,
            "allowed_statuses": list(self.allowed_statuses),
            "tracking_policy": {
                "longitudinal_history_preserved": True,
                "status_transitions_auditable": True,
                "protocol_and_experiment_links_preserved": True,
                "functional_scope_only": True,
            },
            "validation_policy": {
                "unknown_is_default": True,
                "validated_does_not_imply_phenomenology": True,
                "invalidated_triggers_theory_revision": True,
                "ambiguous_requires_follow_up": True,
            },
            "epistemic_guards": dict(self.epistemic_guards),
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "persist_requested": bool(persist),
            "persisted": persisted,
            "output_path": str(outpath) if persist else None,
            "timestamp_utc": _now(),
        }

__all__ = ["PredictionValidationTracker"]
