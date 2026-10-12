"""
ACEE19 — governed multi-cycle meta-analysis.

This module harmonizes ACEE observations, performs a deterministic fixed-effect
meta-analysis, quantifies heterogeneity, records exclusions and anomalies, and
produces only functional conclusions. It does not certify, select, schedule,
execute, install, mutate, or roll back.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import os
from pathlib import Path
from statistics import mean, pstdev
from typing import Any, Mapping, Sequence

PRIMITIVE = "ACEE_META_ANALYSIS"
STATUS = "ACEE_META_ANALYSIS_COMPLETE"

DEPENDENCIES = [
    "scientific_meta_analysis_engine",
    "constitutional_meta_analysis_engine",
    "inter_run_stability_synthesizer",
    "anomaly_in_evidence_detector",
    "acee_impact_evaluator",
    "acee_causal_effect_analyzer",
    "acee_longitudinal_tracker",
    "acee_prediction_engine",
]

EPISTEMIC_STATUS = {
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

FORBIDDEN_TRUE_FIELDS = (
    "certification_performed",
    "selection_performed",
    "execution_authorized",
    "schedule_created",
    "installation_completed",
    "mutation_executed",
    "rollback_performed",
)


def _finite_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _bounded(value: Any, default: float = 0.0) -> float:
    parsed = _finite_number(value)
    if parsed is None:
        return default
    return max(0.0, min(1.0, parsed))


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _analysis_hash(payload: Mapping[str, Any]) -> str:
    copy = deepcopy(dict(payload))
    copy.pop("analysis_hash", None)
    copy.pop("generated_at_utc", None)
    copy.pop("persist_requested", None)
    copy.pop("persisted", None)
    copy.pop("artifacts", None)
    return sha256(_canonical_json(copy).encode("utf-8")).hexdigest()


class ACEEMetaAnalysis:
    primitive = PRIMITIVE

    def __init__(
        self,
        root: Path | str | None = None,
        runtime_dir: Path | str | None = None,
    ) -> None:
        self.root = Path(
            root or (Path.home() / "open-cognitive-ecology")
        ).resolve()
        requested = Path(runtime_dir) if runtime_dir else (
            self.root / "acee_runtime" / "ACEE19_acee_meta_analysis"
        )
        self.runtime_dir = requested.resolve()
        try:
            self.runtime_dir.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("runtime_dir_outside_root") from exc

    @staticmethod
    def _observation_id(
        observation: Mapping[str, Any],
        index: int,
    ) -> str:
        if "observation_id" in observation:
            raw = observation.get("observation_id")
            observation_id = "" if raw is None else str(raw).strip()
            if not observation_id:
                raise ValueError("empty_observation_id")
            return observation_id

        raw = (
            observation.get("cycle_id")
            or observation.get("prediction_id")
            or observation.get("candidate_id")
            or f"observation-{index + 1:04d}"
        )
        observation_id = str(raw).strip()
        if not observation_id:
            raise ValueError("empty_observation_id")
        return observation_id

    def _derive_observations(
        self,
        inputs: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        explicit = inputs.get("observations", [])
        if (
            isinstance(explicit, Sequence)
            and not isinstance(explicit, (str, bytes))
        ):
            observations = [
                dict(item)
                for item in explicit
                if isinstance(item, Mapping)
            ]
            if observations:
                return observations

        records = inputs.get("records", inputs.get("longitudinal_records", []))
        observations: list[dict[str, Any]] = []
        if isinstance(records, Sequence) and not isinstance(records, (str, bytes)):
            for index, record in enumerate(records):
                if not isinstance(record, Mapping):
                    continue
                before = _finite_number(record.get("before_score"))
                after = _finite_number(record.get("after_score"))
                effect = _finite_number(record.get("effect_size"))
                if effect is None and before is not None and after is not None:
                    effect = after - before
                observations.append({
                    "observation_id": (
                        record.get("cycle_id")
                        or f"cycle-{index + 1:04d}"
                    ),
                    "cycle_id": record.get("cycle_id"),
                    "effect_size": effect,
                    "variance": record.get("variance", 1.0),
                    "confidence": record.get("confidence", 0.5),
                    "validation_status": record.get(
                        "validation_status", "unknown"
                    ),
                    "causal_status": record.get("causal_status", "unknown"),
                    "decision": record.get("decision", "unknown"),
                    "rollback_performed": (
                        record.get("rollback_performed") is True
                    ),
                    "closure_pressure_delta": record.get(
                        "closure_pressure_delta", 0.0
                    ),
                    "stability_score": record.get(
                        "stability_score",
                        record.get("metrics", {}).get("stability_score", 0.0)
                        if isinstance(record.get("metrics"), Mapping)
                        else 0.0,
                    ),
                    "source": "acee_longitudinal_tracker",
                })

        predictions = inputs.get("predictions", [])
        if isinstance(predictions, Sequence) and not isinstance(
            predictions, (str, bytes)
        ):
            offset = len(observations)
            for index, prediction in enumerate(predictions):
                if not isinstance(prediction, Mapping):
                    continue
                observations.append({
                    "observation_id": (
                        prediction.get("candidate_id")
                        or f"prediction-{offset + index + 1:04d}"
                    ),
                    "effect_size": prediction.get("predicted_gain"),
                    "variance": prediction.get("variance", 1.0),
                    "confidence": prediction.get("confidence", 0.5),
                    "validation_status": "predicted",
                    "causal_status": "not_resolved",
                    "decision": "not_selected",
                    "rollback_performed": False,
                    "closure_pressure_delta": prediction.get(
                        "closure_pressure_delta", 0.0
                    ),
                    "stability_score": prediction.get("robustness", 0.0),
                    "source": "acee_prediction_engine",
                })
        return observations

    def normalize_observations(
        self,
        inputs: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        raw = self._derive_observations(dict(inputs or {}))
        included: list[dict[str, Any]] = []
        exclusions: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        for index, observation in enumerate(raw):
            observation_id = self._observation_id(observation, index)
            if observation_id in seen_ids:
                raise ValueError(
                    f"duplicate_observation_id:{observation_id}"
                )
            seen_ids.add(observation_id)

            effect = _finite_number(observation.get("effect_size"))
            variance = _finite_number(observation.get("variance"))
            if effect is None:
                exclusions.append({
                    "observation_id": observation_id,
                    "reason": "non_finite_effect_size",
                })
                continue
            if variance is None or variance <= 0.0:
                exclusions.append({
                    "observation_id": observation_id,
                    "reason": "invalid_variance",
                })
                continue

            normalized = {
                "observation_id": observation_id,
                "cycle_id": (
                    None
                    if observation.get("cycle_id") is None
                    else str(observation.get("cycle_id"))
                ),
                "effect_size": round(effect, 12),
                "variance": round(variance, 12),
                "weight": round(1.0 / variance, 12),
                "confidence": round(
                    _bounded(observation.get("confidence"), 0.5), 6
                ),
                "validation_status": str(
                    observation.get("validation_status", "unknown")
                ),
                "causal_status": str(
                    observation.get("causal_status", "unknown")
                ),
                "decision": str(observation.get("decision", "unknown")),
                "rollback_performed": (
                    observation.get("rollback_performed") is True
                ),
                "closure_pressure_delta": round(
                    _finite_number(
                        observation.get("closure_pressure_delta")
                    )
                    or 0.0,
                    6,
                ),
                "stability_score": round(
                    _bounded(observation.get("stability_score"), 0.0),
                    6,
                ),
                "source": str(observation.get("source", "explicit")),
            }
            included.append(normalized)

        included.sort(key=lambda item: item["observation_id"])
        exclusions.sort(
            key=lambda item: (item["observation_id"], item["reason"])
        )
        return {
            "raw_count": len(raw),
            "included": included,
            "exclusions": exclusions,
        }

    @staticmethod
    def _fixed_effect(
        observations: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        count = len(observations)
        if count == 0:
            return {
                "pooled_effect": None,
                "standard_error": None,
                "confidence_interval": {"lower": None, "upper": None},
                "heterogeneity": {
                    "Q": None,
                    "degrees_of_freedom": 0,
                    "I2": None,
                    "tau2": None,
                },
                "overall_significance": "insufficient_evidence",
            }

        total_weight = sum(float(item["weight"]) for item in observations)
        pooled = sum(
            float(item["effect_size"]) * float(item["weight"])
            for item in observations
        ) / total_weight
        variance_combined = 1.0 / total_weight
        standard_error = math.sqrt(variance_combined)
        lower = pooled - 1.96 * standard_error
        upper = pooled + 1.96 * standard_error
        z_value = pooled / standard_error if standard_error > 0 else 0.0
        q = sum(
            float(item["weight"])
            * (float(item["effect_size"]) - pooled) ** 2
            for item in observations
        )
        df = count - 1
        i2 = (
            max(0.0, (q - df) / q)
            if q > 0.0 and df > 0
            else 0.0
        )
        sum_w_sq = sum(float(item["weight"]) ** 2 for item in observations)
        c_value = (
            total_weight - (sum_w_sq / total_weight)
            if total_weight > 0
            else 0.0
        )
        tau2 = (
            max(0.0, (q - df) / c_value)
            if c_value > 0 and df > 0
            else 0.0
        )

        if count < 2:
            significance = "insufficient_evidence"
        elif abs(z_value) >= 3.29:
            significance = "p<0.001"
        elif abs(z_value) >= 2.58:
            significance = "p<0.01"
        elif abs(z_value) >= 1.96:
            significance = "p<0.05"
        else:
            significance = "ns"

        return {
            "pooled_effect": round(pooled, 6),
            "standard_error": round(standard_error, 6),
            "confidence_interval": {
                "lower": round(lower, 6),
                "upper": round(upper, 6),
            },
            "heterogeneity": {
                "Q": round(q, 6),
                "degrees_of_freedom": df,
                "I2": round(i2, 6),
                "tau2": round(tau2, 6),
            },
            "overall_significance": significance,
        }

    @staticmethod
    def _anomalies(
        observations: Sequence[Mapping[str, Any]],
    ) -> list[dict[str, Any]]:
        if len(observations) < 3:
            return []
        effects = [float(item["effect_size"]) for item in observations]
        center = mean(effects)
        spread = pstdev(effects)
        if spread <= 0.0:
            return []
        anomalies = []
        for item in observations:
            z_score = abs(float(item["effect_size"]) - center) / spread
            if z_score >= 2.0:
                anomalies.append({
                    "observation_id": item["observation_id"],
                    "reason": "effect_size_outlier",
                    "z_score": round(z_score, 6),
                })
        return anomalies

    def build_meta_analysis(
        self,
        inputs: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized = self.normalize_observations(inputs)
        observations = normalized["included"]
        statistical = self._fixed_effect(observations)
        count = len(observations)

        confidence_values = [
            float(item["confidence"]) for item in observations
        ]
        stability_values = [
            float(item["stability_score"]) for item in observations
        ]
        rollback_count = sum(
            1 for item in observations if item["rollback_performed"]
        )
        closure_increase_count = sum(
            1
            for item in observations
            if float(item["closure_pressure_delta"]) > 0.0
        )
        resolved_causal_count = sum(
            1
            for item in observations
            if item["causal_status"] in {
                "resolved",
                "causal_effect_resolved",
                "confirmed",
            }
        )
        validated_count = sum(
            1
            for item in observations
            if item["validation_status"] in {
                "passed",
                "valid",
                "validated",
                "complete",
            }
        )

        mean_confidence = mean(confidence_values) if confidence_values else 0.0
        mean_stability = mean(stability_values) if stability_values else 0.0
        consistency_score = (
            max(
                0.0,
                1.0 - float(
                    statistical["heterogeneity"]["I2"] or 0.0
                ),
            )
            if count >= 2
            else 0.0
        )
        replication_support = (
            min(1.0, count / 3.0) * consistency_score
            if count >= 2
            else 0.0
        )
        validation_ratio = validated_count / count if count else 0.0
        causal_ratio = resolved_causal_count / count if count else 0.0
        rollback_penalty = rollback_count / count if count else 0.0
        closure_penalty = closure_increase_count / count if count else 0.0
        evidence_quality = max(
            0.0,
            min(
                1.0,
                0.30 * mean_confidence
                + 0.20 * mean_stability
                + 0.20 * validation_ratio
                + 0.15 * causal_ratio
                + 0.15 * consistency_score
                - 0.10 * rollback_penalty
                - 0.10 * closure_penalty,
            ),
        )

        limitations: list[str] = []
        if count == 0:
            limitations.append("no_valid_observations")
        elif count == 1:
            limitations.append("single_observation_no_meta_inference")
        if count < 3:
            limitations.append("limited_replication_support")
        if float(statistical["heterogeneity"]["I2"] or 0.0) > 0.5:
            limitations.append("high_heterogeneity")
        if normalized["exclusions"]:
            limitations.append("observations_excluded")
        if causal_ratio < 0.5 and count:
            limitations.append("limited_causal_resolution")

        if count < 2:
            functional_conclusion = (
                "Insufficient evidence for a multi-cycle functional conclusion."
            )
        elif statistical["overall_significance"] == "ns":
            functional_conclusion = (
                "No statistically significant pooled functional effect was "
                "detected under the current fixed-effect synthesis."
            )
        elif evidence_quality < 0.6:
            functional_conclusion = (
                "A pooled functional effect was detected, but evidence quality "
                "or consistency remains insufficient for a strong conclusion."
            )
        else:
            functional_conclusion = (
                "The included cycles show a statistically supported pooled "
                "functional effect, subject to the reported limitations."
            )

        result = {
            "primitive": PRIMITIVE,
            "status": STATUS,
            "meta_analysis_complete": True,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "observation_count": normalized["raw_count"],
            "included_observation_count": count,
            "excluded_observation_count": len(
                normalized["exclusions"]
            ),
            "included_observations": observations,
            "exclusions": normalized["exclusions"],
            **statistical,
            "consistency_score": round(consistency_score, 6),
            "replication_support": round(replication_support, 6),
            "evidence_quality": round(evidence_quality, 6),
            "anomalies": self._anomalies(observations),
            "functional_conclusion": functional_conclusion,
            "limitations": sorted(set(limitations)),
            "certification_performed": False,
            "selection_performed": False,
            "execution_authorized": False,
            "schedule_created": False,
            "installation_completed": False,
            "mutation_executed": False,
            "rollback_performed": False,
            "functional_conclusion_only": True,
            "epistemic_status": deepcopy(EPISTEMIC_STATUS),
            "diagnostics": {
                "fixed_effect_model": True,
                "read_only": True,
                "acee20_boundary_preserved": True,
                "validated_observation_count": validated_count,
                "causally_resolved_observation_count": resolved_causal_count,
                "rollback_observation_count": rollback_count,
                "closure_increase_observation_count": closure_increase_count,
            },
            "persist_requested": False,
            "persisted": False,
            "artifacts": {"json_path": None},
        }
        result["analysis_hash"] = _analysis_hash(result)
        return result

    def verify_meta_analysis(
        self,
        result: Mapping[str, Any],
    ) -> dict[str, Any]:
        errors: list[str] = []
        payload = dict(result)
        if payload.get("status") != STATUS:
            errors.append("invalid_status")
        if payload.get("meta_analysis_complete") is not True:
            errors.append("meta_analysis_not_complete")
        for field in FORBIDDEN_TRUE_FIELDS:
            if payload.get(field) is not False:
                errors.append(f"forbidden_true:{field}")
        if payload.get("epistemic_status") != EPISTEMIC_STATUS:
            errors.append("epistemic_status_violation")
        if payload.get("analysis_hash") != _analysis_hash(payload):
            errors.append("analysis_hash_mismatch")
        included = payload.get("included_observations", [])
        if not isinstance(included, list):
            errors.append("included_observations_not_list")
        elif included != sorted(
            included,
            key=lambda item: str(item.get("observation_id", "")),
        ):
            errors.append("observation_order_not_canonical")
        return {
            "verified": not errors,
            "verification_errors": errors,
        }

    @staticmethod
    def _atomic_write(path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
        with temporary.open("w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)

    def step(
        self,
        inputs: Mapping[str, Any] | None = None,
        persist: bool = False,
    ) -> dict[str, Any]:
        result = self.build_meta_analysis(inputs)
        verification = self.verify_meta_analysis(result)
        if not verification["verified"]:
            raise ValueError(
                "invalid_meta_analysis:"
                + ",".join(verification["verification_errors"])
            )

        result["persist_requested"] = bool(persist)
        if persist:
            path = (
                self.runtime_dir / "latest_meta_analysis.json"
            ).resolve()
            result["persisted"] = True
            result["artifacts"]["json_path"] = str(path)
            text = json.dumps(
                result,
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
                allow_nan=False,
            )
            self._atomic_write(path, text)
        return result
