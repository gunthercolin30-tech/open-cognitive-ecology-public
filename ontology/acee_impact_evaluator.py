\
"""ACEE8 — governed before/after impact comparison facade.

This module does not produce domain metrics, decide causal attribution,
select a mutation, execute validation, install code or perform rollback.
It normalizes and compares measurements supplied by ACEE4/ACEE7 and existing
metric producers, then emits a functional impact assessment.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple

PRIMITIVE = "ACEE_IMPACT_EVALUATOR"
STATUS_READY = "ACEE_IMPACT_EVALUATED"
STATUS_DEGRADED = "ACEE_IMPACT_EVALUATION_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"

METRIC_SPECS = {
    "error_count": {
        "direction": "lower_is_better",
        "aliases": ("error_count", "errors", "failed_calls"),
        "kind": "count",
    },
    "modules_discovered": {
        "direction": "higher_is_better",
        "aliases": ("modules_discovered", "module_count", "discovered_modules"),
        "kind": "count",
    },
    "active_primitives": {
        "direction": "higher_is_better",
        "aliases": ("active_primitives", "classes_instantiated", "active_primitive_count"),
        "kind": "count",
    },
    "stability_score": {
        "direction": "higher_is_better",
        "aliases": (
            "stability_score", "overall_stability_score", "civilizational_stability_index",
            "longitudinal_stability_score", "stability_index",
        ),
        "kind": "score",
    },
    "governance_score": {
        "direction": "higher_is_better",
        "aliases": (
            "governance_score", "governance_consistency_score",
            "constitutional_integrity_score", "constitutional_integrity_index",
            "constitutional_alignment_score",
        ),
        "kind": "score",
    },
    "evolution_score": {
        "direction": "higher_is_better",
        "aliases": (
            "evolution_score", "evolutionary_score", "improvement_score",
            "fitness_score", "effectiveness_score",
        ),
        "kind": "score",
    },
    "closure_pressure": {
        "direction": "lower_is_better",
        "aliases": ("closure_pressure", "closure_pressure_index", "baseline_closure_pressure"),
        "kind": "score",
    },
    "runtime_score": {
        "direction": "higher_is_better",
        "aliases": (
            "runtime_score", "runtime_health", "runtime_health_score",
            "global_viability_score", "operational_score", "scheduler_health",
        ),
        "kind": "score",
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _mapping(value: Any) -> Dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _finite_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return number if math.isfinite(number) else None


def _walk(mapping: Mapping[str, Any], prefix: str = ""):
    for key, value in mapping.items():
        path = f"{prefix}.{key}" if prefix else str(key)
        yield str(key), path, value
        if isinstance(value, Mapping):
            yield from _walk(value, path)


@dataclass
class AceeImpactEvaluator:
    root: Optional[Path] = None

    def __post_init__(self) -> None:
        self.root = (
            Path(self.root) if self.root is not None
            else Path.home() / "open-cognitive-ecology"
        ).expanduser().resolve()

    def _paths(self) -> Tuple[Path, Path, Path]:
        directory = self.root / "acee_runtime" / "ACEE8_acee_impact_evaluator"
        return (
            directory / "latest_impact_evaluation.json",
            directory / "impact_evaluation_history.jsonl",
            directory / ".impact_evaluation.lock",
        )

    def _previous(self, history: Path) -> Tuple[Optional[Dict[str, Any]], bool]:
        if not history.is_file():
            return None, False
        try:
            lines = [line for line in history.read_text(encoding="utf-8").splitlines() if line.strip()]
            return (json.loads(lines[-1]), False) if lines else (None, False)
        except (OSError, json.JSONDecodeError, TypeError):
            return None, True

    def _extract(self, snapshot: Mapping[str, Any]) -> Tuple[Dict[str, float], Dict[str, str], List[str]]:
        flattened = list(_walk(snapshot))
        metrics: Dict[str, float] = {}
        sources: Dict[str, str] = {}
        invalid: List[str] = []
        for metric, spec in METRIC_SPECS.items():
            found = False
            for alias in spec["aliases"]:
                matches = [(path, value) for key, path, value in flattened if key == alias]
                if not matches:
                    continue
                path, value = matches[0]
                found = True
                number = _finite_number(value)
                if number is None or number < 0:
                    invalid.append(metric)
                    break
                if spec["kind"] == "score" and number > 1.0:
                    invalid.append(metric)
                    break
                metrics[metric] = number
                sources[metric] = path
                break
            if not found:
                continue
        return metrics, sources, sorted(set(invalid))

    @staticmethod
    def _normalized_delta(metric: str, before: float, after: float) -> float:
        spec = METRIC_SPECS[metric]
        if spec["kind"] == "count":
            raw = (after - before) / max(1.0, abs(before))
        else:
            raw = after - before
        if spec["direction"] == "lower_is_better":
            raw = -raw
        return max(-1.0, min(1.0, raw))

    def _build(
        self,
        supplied: Mapping[str, Any],
        previous_hash: Optional[str],
        corrupted: bool,
    ) -> Dict[str, Any]:
        before_raw = _mapping(supplied.get("before"))
        after_raw = _mapping(supplied.get("after"))
        before, before_sources, invalid_before = self._extract(before_raw)
        after, after_sources, invalid_after = self._extract(after_raw)

        missing_before = sorted(set(METRIC_SPECS) - set(before))
        missing_after = sorted(set(METRIC_SPECS) - set(after))
        invalid_metrics = sorted(set(invalid_before + invalid_after))
        comparable = sorted((set(before) & set(after)) - set(invalid_metrics))

        deltas: Dict[str, float] = {}
        normalized: Dict[str, float] = {}
        classifications: Dict[str, str] = {}
        tolerance = _finite_number(supplied.get("neutral_tolerance"))
        tolerance = 1e-9 if tolerance is None else max(0.0, min(0.1, tolerance))

        for metric in comparable:
            raw_delta = after[metric] - before[metric]
            deltas[metric] = round(raw_delta, 12)
            value = self._normalized_delta(metric, before[metric], after[metric])
            normalized[metric] = round(value, 12)
            if value > tolerance:
                classifications[metric] = "improved"
            elif value < -tolerance:
                classifications[metric] = "regressed"
            else:
                classifications[metric] = "unchanged"

        impact_score = (
            sum(normalized.values()) / len(normalized)
            if normalized else 0.0
        )
        impact_score = round(impact_score, 12)
        if impact_score > tolerance:
            impact_classification = "net_improvement"
        elif impact_score < -tolerance:
            impact_classification = "net_regression"
        else:
            impact_classification = "neutral_or_inconclusive"

        blocking: List[str] = []
        if not before_raw:
            blocking.append("before_snapshot_missing")
        if not after_raw:
            blocking.append("after_snapshot_missing")
        if missing_before:
            blocking.append("before_metrics_incomplete")
        if missing_after:
            blocking.append("after_metrics_incomplete")
        if invalid_metrics:
            blocking.append("invalid_or_non_finite_metrics")
        if corrupted:
            blocking.append("history_corrupted")

        validation_after = _mapping(after_raw.get("validation"))
        if not validation_after:
            validation_after = _mapping(after_raw.get("validation_result"))
        validation_failed = (
            validation_after.get("validation_passed") is False
            or validation_after.get("error_count", 0) not in (0, 0.0, None)
        )

        rollback_reasons: List[str] = []
        if "error_count" in comparable and after["error_count"] > before["error_count"]:
            rollback_reasons.append("error_count_increased")
        if after.get("error_count", 0.0) > 0.0:
            rollback_reasons.append("post_intervention_errors_present")
        if classifications.get("stability_score") == "regressed":
            rollback_reasons.append("stability_regression")
        if classifications.get("governance_score") == "regressed":
            rollback_reasons.append("governance_regression")
        if classifications.get("closure_pressure") == "regressed":
            rollback_reasons.append("closure_pressure_increase")
        if validation_failed:
            rollback_reasons.append("validation_failure")

        complete = not blocking and len(comparable) == len(METRIC_SPECS)
        status = STATUS_READY if complete else STATUS_DEGRADED
        source_ids = {
            "cycle_id": supplied.get("cycle_id") or after_raw.get("cycle_id"),
            "validation_id": supplied.get("validation_id") or validation_after.get("validation_id"),
            "rollback_transaction_id": supplied.get("rollback_transaction_id"),
        }

        result: Dict[str, Any] = {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "evaluation_id": str(supplied.get("evaluation_id") or "impact-unspecified"),
            "timestamp_utc": str(supplied.get("timestamp_utc") or _now()),
            "impact_status": status,
            "impact_evaluated": complete,
            "comparison_valid": complete,
            "metric_contract": {
                key: {"direction": value["direction"], "kind": value["kind"]}
                for key, value in METRIC_SPECS.items()
            },
            "before_metrics": before,
            "after_metrics": after,
            "before_metric_sources": before_sources,
            "after_metric_sources": after_sources,
            "metric_deltas": deltas,
            "normalized_deltas": normalized,
            "metric_classifications": classifications,
            "improved_metrics": sorted(k for k, v in classifications.items() if v == "improved"),
            "regressed_metrics": sorted(k for k, v in classifications.items() if v == "regressed"),
            "unchanged_metrics": sorted(k for k, v in classifications.items() if v == "unchanged"),
            "missing_before_metrics": missing_before,
            "missing_after_metrics": missing_after,
            "invalid_metrics": invalid_metrics,
            "impact_score": impact_score,
            "impact_classification": impact_classification,
            "observed_regression_signal": bool(rollback_reasons),
            "observed_regression_reasons": sorted(set(rollback_reasons)),
            "rollback_recommended": bool(rollback_reasons),
            "rollback_trigger_reasons": sorted(set(rollback_reasons)),
            "rollback_fields_deprecated": True,
            "blocking_reasons": sorted(set(blocking)),
            "source_ids": source_ids,
            "history_corrupted": corrupted,
            "previous_impact_hash": previous_hash,
            "validation_executed_by_evaluator": False,
            "causal_analysis_required": complete,
            "ready_for_causal_analysis": complete,
            "ready_for_selection": False,
            "causal_effect_resolved": False,
            "selection_decision_made": False,
            "rollback_executed": False,
            "code_generated": False,
            "code_installed": False,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
            "collective_consciousness_proven": False,
            "collective_subjectivity_proven": False,
            "collective_qualia_proven": False,
            "collective_phenomenology_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
        }
        result["impact_hash"] = _sha({k: v for k, v in result.items() if k != "impact_hash"})
        return result

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> Dict[str, Any]:
        supplied = _mapping(inputs)
        latest, history, lock = self._paths()
        previous, corrupted = self._previous(history)
        result = self._build(
            supplied,
            previous.get("impact_hash") if previous else None,
            corrupted,
        )
        result.update({
            "persisted": False,
            "latest_path": str(latest),
            "history_path": str(history),
        })
        if not persist:
            return result

        latest.parent.mkdir(parents=True, exist_ok=True)
        with lock.open("a+", encoding="utf-8") as lock_stream:
            fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX)
            previous, corrupted = self._previous(history)
            result = self._build(
                supplied,
                previous.get("impact_hash") if previous else None,
                corrupted,
            )
            record = dict(result)
            record.update({
                "persisted": True,
                "latest_path": str(latest),
                "history_path": str(history),
            })
            tmp = latest.with_suffix(".tmp")
            tmp.write_text(json.dumps(record, sort_keys=True, indent=2), encoding="utf-8")
            tmp.replace(latest)
            with history.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record, sort_keys=True) + "\n")
                stream.flush()
            fcntl.flock(lock_stream.fileno(), fcntl.LOCK_UN)
            return record
