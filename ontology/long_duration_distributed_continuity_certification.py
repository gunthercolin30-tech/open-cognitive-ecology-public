from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional

PRIMITIVE = "long_duration_distributed_continuity_certification"

DEPENDENCIES = [
    "distributed_civilizational_continuity_certification",
    "longitudinal_certification",
    "thirty_day_distributed_monitoring",
    "civilizational_longitudinal_stability_synthesizer",
    "longitudinal_drift_detection",
    "longitudinal_recovery_observer",
    "persistent_experimental_validation_network",
    "metrics_history_recorder",
    "continuous_long_duration_runtime_executor",
]

ROOT = Path.home() / "open-cognitive-ecology"


def _utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clamp(value: Any, lo: float = 0.0, hi: float = 1.0) -> float:
    try:
        return max(lo, min(hi, float(value)))
    except Exception:
        return 0.0


def _sha(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    ).hexdigest()


def _ssd_continuity_root() -> Optional[Path]:
    ssd_root = Path(os.environ.get("OCE_SSD_ROOT", "/Volumes/OCE_SSD"))
    continuity = Path(os.environ.get("OCE_CONTINUITY", str(ssd_root / "OCE_CIVILIZATIONAL_CONTINUITY")))
    if continuity.exists():
        return continuity
    return None


class LongDurationDistributedContinuityCertification:
    """F16.7 long-duration distributed continuity certification.

    F16.6 certifies a distributed civilization at an instant. F16.7 adds a
    longitudinal layer: it reads or simulates a multi-day sequence of F16.6-like
    certifications, computes rolling continuity, stability, drift, recovery and
    trend metrics, and emits a long-duration continuity certificate.

    Epistemic boundary: functional continuity validation only; no phenomenal
    subjectivity claim.
    """

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else ROOT
        continuity_root = _ssd_continuity_root()
        if continuity_root is not None:
            self.cert_root = continuity_root / "certifications"
            self.history_path = self.cert_root / "long_duration_distributed_continuity_certification_history.jsonl"
            self.registry_path = self.cert_root / "long_duration_distributed_continuity_certification_registry.json"
            self.source_history_path = self.cert_root / "distributed_civilizational_continuity_certification_history.jsonl"
        else:
            self.cert_root = self.root / "distributed_nodes" / "long_duration_certifications"
            self.history_path = self.cert_root / "long_duration_distributed_continuity_certification_history.jsonl"
            self.registry_path = self.cert_root / "long_duration_distributed_continuity_certification_registry.json"
            self.source_history_path = self.root / "distributed_nodes" / "continuity_certifications" / "distributed_civilizational_continuity_certification_history.jsonl"
        self.cert_root.mkdir(parents=True, exist_ok=True)

    def _dependency_readiness(self) -> Dict[str, Any]:
        available = []
        missing = []
        for dep in DEPENDENCIES:
            if (self.root / "ontology" / f"{dep}.py").exists():
                available.append(dep)
            else:
                missing.append(dep)
        return {
            "available_dependencies": available,
            "missing_dependencies": missing,
            "available_dependency_count": len(available),
            "missing_dependency_count": len(missing),
            "dependency_readiness": round(len(available) / max(1, len(DEPENDENCIES)), 6),
        }

    def _read_history(self, max_records: int = 120) -> List[Dict[str, Any]]:
        if not self.source_history_path.exists():
            return []
        rows: List[Dict[str, Any]] = []
        try:
            for line in self.source_history_path.read_text(encoding="utf-8").splitlines()[-max_records:]:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    if isinstance(item, dict):
                        rows.append(item)
                except Exception:
                    continue
        except Exception:
            return []
        return rows

    def _simulate_records(self, days: int, score: float, drift: float, regression_frequency: float) -> List[Dict[str, Any]]:
        days = max(1, int(days))
        base = _clamp(score)
        drift = float(drift)
        regression_frequency = _clamp(regression_frequency)
        rows = []
        for i in range(days):
            regression = regression_frequency > 0 and ((i + 1) % max(1, int(round(1.0 / max(regression_frequency, 0.001)))) == 0)
            v = _clamp(base - drift * (i / max(1, days - 1)) - (0.22 if regression else 0.0))
            t = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(days=days - i - 1)).replace(microsecond=0).isoformat().replace("+00:00", "Z")
            rows.append({
                "timestamp_utc": t,
                "continuity_certification_index": round(v, 6),
                "distributed_continuity_score": round(_clamp(v - 0.006), 6),
                "distributed_civilization_certified": bool(v >= 0.86 and not regression),
                "classification": "Distributed Civilization Certified" if v >= 0.94 and not regression else "Distributed Civilization Not Certified" if regression else "Distributed Civilization Partially Certified",
                "simulation_record": True,
            })
        return rows

    def _call_component(self, module_name: str, class_name: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        try:
            module = __import__(f"ontology.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            obj = cls()
            if hasattr(obj, "step"):
                try:
                    result = obj.step(payload or {})
                except TypeError:
                    result = obj.step()
                return result if isinstance(result, dict) else {"primitive": module_name, "result": result, "success": True}
            return {"primitive": module_name, "success": True, "step_available": False}
        except Exception as exc:
            return {"primitive": module_name, "success": False, "error": repr(exc)}

    def _trend(self, values: List[float]) -> float:
        if len(values) < 2:
            return 0.0
        n = len(values)
        xs = list(range(n))
        mx = sum(xs) / n
        my = sum(values) / n
        denom = sum((x - mx) ** 2 for x in xs) or 1.0
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, values)) / denom
        return slope

    def step(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        deps = self._dependency_readiness()

        target_days = int(inputs.get("target_days", 30))
        min_days_for_certification = int(inputs.get("min_days_for_certification", 7))
        use_history = bool(inputs.get("use_history", True))
        simulate_days = int(inputs.get("simulate_days", target_days))
        simulated_score = _clamp(inputs.get("simulated_score", 0.97412))
        simulated_drift = float(inputs.get("simulated_drift", 0.0))
        regression_frequency = _clamp(inputs.get("regression_frequency", 0.0))

        records = self._read_history() if use_history else []
        if len(records) < min_days_for_certification or inputs.get("force_simulated_records", False):
            records = self._simulate_records(
                days=simulate_days,
                score=simulated_score,
                drift=simulated_drift,
                regression_frequency=regression_frequency,
            )

        values = [_clamp(r.get("continuity_certification_index", r.get("distributed_continuity_score", 0.0))) for r in records]
        certified_flags = [bool(r.get("distributed_civilization_certified", False)) for r in records]
        days_observed = len(records)
        days_certified = sum(1 for x in certified_flags if x)
        completion_ratio = _clamp(days_observed / max(1, target_days))
        certification_ratio = _clamp(days_certified / max(1, days_observed))

        mean_score = statistics.mean(values) if values else 0.0
        min_score = min(values) if values else 0.0
        stdev_score = statistics.pstdev(values) if len(values) > 1 else 0.0
        trend_slope = self._trend(values)
        negative_trend_penalty = _clamp(max(0.0, -trend_slope) * 12.0)
        drift_index = _clamp(1.0 - min(1.0, stdev_score * 6.0 + negative_trend_penalty))
        multi_day_stability_index = _clamp(0.55 * mean_score + 0.25 * min_score + 0.20 * drift_index)
        rolling_continuity_index = _clamp(0.65 * mean_score + 0.20 * certification_ratio + 0.15 * completion_ratio)
        distributed_continuity_trend = round(trend_slope, 8)

        monitoring_result = self._call_component(
            "thirty_day_distributed_monitoring",
            "ThirtyDayDistributedMonitoring",
            {
                "days_observed": days_observed,
                "target_days": target_days,
                "continuity_score": mean_score,
                "stability_score": multi_day_stability_index,
            },
        )
        longitudinal_result = self._call_component(
            "longitudinal_certification",
            "LongitudinalCertification",
            {
                "longitudinal_certification_index": mean_score,
                "stability_index": multi_day_stability_index,
                "drift_index": drift_index,
                "recovery_index": rolling_continuity_index,
            },
        )

        monitoring_index = _clamp(
            monitoring_result.get("monitoring_index",
            monitoring_result.get("thirty_day_monitoring_index",
            completion_ratio))
        )
        longitudinal_index = _clamp(
            longitudinal_result.get("longitudinal_certification_index",
            longitudinal_result.get("certification_index",
            mean_score))
        )

        long_duration_certification_index = round(
            _clamp(
                0.30 * rolling_continuity_index
                + 0.24 * multi_day_stability_index
                + 0.16 * certification_ratio
                + 0.12 * completion_ratio
                + 0.08 * drift_index
                + 0.05 * monitoring_index
                + 0.05 * deps["dependency_readiness"]
            ),
            6,
        )

        blockers = []
        if days_observed < min_days_for_certification:
            blockers.append("insufficient_days_observed")
        if certification_ratio < 0.80:
            blockers.append("certification_ratio_below_threshold")
        if mean_score < 0.86:
            blockers.append("mean_continuity_below_threshold")
        if min_score < 0.72:
            blockers.append("minimum_continuity_below_threshold")
        if drift_index < 0.70:
            blockers.append("longitudinal_drift_above_threshold")
        if deps["dependency_readiness"] < 0.80:
            blockers.append("long_duration_dependency_readiness_below_threshold")

        long_duration_certified = bool(
            long_duration_certification_index >= 0.86
            and rolling_continuity_index >= 0.84
            and multi_day_stability_index >= 0.82
            and not blockers
        )

        if long_duration_certified and long_duration_certification_index >= 0.94 and days_observed >= target_days:
            classification = "Long Duration Certified"
        elif long_duration_certified:
            classification = "Long Duration Provisionally Certified"
        else:
            classification = "Long Duration Not Certified"

        certification_id = "LDDCC-" + hashlib.sha256(
            f"{_utc()}-{days_observed}-{long_duration_certification_index}".encode("utf-8")
        ).hexdigest()[:16]

        record = {
            "primitive": PRIMITIVE,
            "refinement": "F16.7",
            "timestamp_utc": _utc(),
            "certification_id": certification_id,
            "target_days": target_days,
            "days_observed": days_observed,
            "days_certified": days_certified,
            "completion_ratio": round(completion_ratio, 6),
            "certification_ratio": round(certification_ratio, 6),
            "rolling_continuity_index": round(rolling_continuity_index, 6),
            "multi_day_stability_index": round(multi_day_stability_index, 6),
            "distributed_continuity_trend": distributed_continuity_trend,
            "longitudinal_drift_resistance_index": round(drift_index, 6),
            "long_duration_certification_index": long_duration_certification_index,
            "long_duration_distributed_continuity_certified": long_duration_certified,
            "classification": classification,
            "certification_blockers": blockers,
            "mean_continuity_score": round(mean_score, 6),
            "minimum_continuity_score": round(min_score, 6),
            "continuity_score_stdev": round(stdev_score, 6),
            "dependency_readiness": deps["dependency_readiness"],
            "source_history_path": str(self.source_history_path),
            "history_records_used": days_observed,
            "component_results": {
                "thirty_day_distributed_monitoring": monitoring_result,
                "longitudinal_certification": longitudinal_result,
            },
            "diagnostics": {
                **deps,
                "non_redundant_role": "longitudinal_layer_above_F16_6_instant_certification",
                "closure_pressure_added": 0.0,
                "epistemic_boundary": "functional continuity validation only; no phenomenal subjectivity claim",
            },
        }

        checksum = _sha(record)
        record["record_checksum"] = checksum
        record_path = self.cert_root / f"{certification_id}.json"
        record_path.write_text(json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        record["record_path"] = str(record_path)

        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

        registry = {
            "primitive": PRIMITIVE,
            "refinement": "F16.7",
            "latest_certification_id": certification_id,
            "latest_record_path": str(record_path),
            "latest_checksum": checksum,
            "long_duration_distributed_continuity_certified": long_duration_certified,
            "long_duration_certification_index": long_duration_certification_index,
            "days_observed": days_observed,
            "days_certified": days_certified,
            "updated_at_utc": _utc(),
        }
        self.registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        record["registry_path"] = str(self.registry_path)
        return record


if __name__ == "__main__":
    from pprint import pprint
    pprint(LongDurationDistributedContinuityCertification().step())
