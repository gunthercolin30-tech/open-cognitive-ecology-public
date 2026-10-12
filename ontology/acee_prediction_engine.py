"""
ACEE18 — Unified evolution prediction engine.

Read-only predictive ranking layer over existing improvement, trajectory,
reversibility and validation signals. It never selects, schedules, installs,
executes or rolls back a candidate.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any, Mapping, Sequence

PRIMITIVE = "ACEE_PREDICTION_ENGINE"
STATUS = "ACEE_EVOLUTION_PREDICTION_READY"

DEPENDENCIES = [
    "performance_improvement_planner",
    "self_parameter_optimization_engine",
    "trajectory_simulation",
    "trajectory_reversibility",
    "trajectory_validation",
    "acee_longitudinal_tracker",
    "acee_best_architecture_archive",
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
    "execution_authorized",
    "selection_performed",
    "schedule_created",
    "installation_completed",
    "mutation_executed",
    "rollback_performed",
)


def _number(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if math.isfinite(parsed) else default


def _bounded(value: Any, default: float = 0.0) -> float:
    return max(0.0, min(1.0, _number(value, default)))


def _canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _hash_payload(payload: Mapping[str, Any]) -> str:
    copy = deepcopy(dict(payload))
    copy.pop("prediction_hash", None)
    copy.pop("generated_at_utc", None)
    copy.pop("artifacts", None)
    copy.pop("persisted", None)
    copy.pop("persist_requested", None)
    return sha256(_canonical_json(copy).encode("utf-8")).hexdigest()


class ACEEPredictionEngine:
    primitive = PRIMITIVE

    def __init__(
        self,
        root: Path | str | None = None,
        runtime_dir: Path | str | None = None,
    ) -> None:
        self.root = Path(root or (Path.home() / "open-cognitive-ecology")).resolve()
        requested = Path(runtime_dir) if runtime_dir else (
            self.root / "acee_runtime" / "ACEE18_acee_prediction_engine"
        )
        self.runtime_dir = requested.resolve()
        try:
            self.runtime_dir.relative_to(self.root)
        except ValueError as exc:
            raise ValueError("runtime_dir_outside_root") from exc

    @staticmethod
    def _candidate_id(candidate: Mapping[str, Any], index: int) -> str:
        if "candidate_id" in candidate:
            raw = candidate.get("candidate_id")
            candidate_id = (
                "" if raw is None else str(raw).strip()
            )
            if not candidate_id:
                raise ValueError("empty_candidate_id")
            return candidate_id

        raw = (
            candidate.get("mutation_id")
            or candidate.get("trajectory_id")
            or candidate.get("name")
            or f"candidate-{index + 1:04d}"
        )
        candidate_id = str(raw).strip()
        if not candidate_id:
            raise ValueError("empty_candidate_id")
        return candidate_id

    def _normalize_candidate(
        self,
        candidate: Mapping[str, Any],
        index: int,
    ) -> dict[str, Any]:
        item = deepcopy(dict(candidate))
        candidate_id = self._candidate_id(item, index)

        predicted_gain = _bounded(
            item.get(
                "predicted_gain",
                item.get(
                    "projected_gain",
                    item.get("optimization_gain", item.get("projected_delta", 0.0)),
                ),
            )
        )
        confidence = _bounded(
            item.get(
                "confidence",
                item.get(
                    "improvement_confidence",
                    item.get("outcome_confidence", 0.5),
                ),
            ),
            0.5,
        )
        risk = _bounded(
            item.get(
                "risk",
                item.get("regression_risk", item.get("failure_risk", 0.0)),
            )
        )
        reversibility = _bounded(
            item.get(
                "reversibility",
                item.get("reversibility_score", 1.0),
            ),
            1.0,
        )
        validation = _bounded(
            item.get(
                "validation",
                item.get(
                    "validation_score",
                    item.get("aggregate_validation_score", 0.5),
                ),
            ),
            0.5,
        )
        robustness = _bounded(
            item.get("robustness", item.get("robustness_score", 0.5)),
            0.5,
        )
        non_closure = _bounded(
            item.get(
                "non_closure",
                item.get("non_closure_score", 0.5),
            ),
            0.5,
        )
        closure_delta = _number(item.get("closure_pressure_delta", 0.0), 0.0)
        closure_penalty = max(0.0, min(1.0, closure_delta))
        governance_compatible = bool(
            item.get(
                "governance_compatible",
                item.get("constitutional_compatible", True),
            )
        )
        required_evidence = item.get("required_evidence", [])
        if not isinstance(required_evidence, list):
            required_evidence = [str(required_evidence)]

        base = (
            0.30 * predicted_gain
            + 0.18 * confidence
            + 0.14 * reversibility
            + 0.12 * validation
            + 0.10 * robustness
            + 0.10 * non_closure
            + 0.06 * (1.0 - risk)
        )
        penalty = (
            0.28 * risk
            + 0.32 * closure_penalty
            + (0.40 if not governance_compatible else 0.0)
        )
        prediction_score = max(0.0, min(1.0, base - penalty))

        if not governance_compatible:
            recommendation = "reject_from_prediction_pipeline"
        elif closure_delta > 0.0:
            recommendation = "require_non_closure_review"
        elif risk > 0.35:
            recommendation = "sandbox_longer"
        elif validation < 0.70 or confidence < 0.65:
            recommendation = "collect_more_evidence"
        else:
            recommendation = "promising_for_selection_review"

        return {
            "candidate_id": candidate_id,
            "predicted_gain": round(predicted_gain, 6),
            "confidence": round(confidence, 6),
            "risk": round(risk, 6),
            "reversibility": round(reversibility, 6),
            "validation": round(validation, 6),
            "robustness": round(robustness, 6),
            "non_closure": round(non_closure, 6),
            "closure_pressure_delta": round(closure_delta, 6),
            "governance_compatible": governance_compatible,
            "recommended_horizon": str(item.get("recommended_horizon", "next_cycle")),
            "required_evidence": sorted(str(v) for v in required_evidence),
            "prediction_score": round(prediction_score, 6),
            "recommendation": recommendation,
            "source": str(item.get("source", "explicit_candidate")),
        }

    def _derive_candidates(
        self,
        inputs: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        explicit = inputs.get("candidates", [])
        if isinstance(explicit, Sequence) and not isinstance(explicit, (str, bytes)):
            candidates = [dict(item) for item in explicit if isinstance(item, Mapping)]
            if candidates:
                return candidates

        candidates: list[dict[str, Any]] = []
        plan = inputs.get("improvement_plan")
        if isinstance(plan, Mapping):
            for index, action in enumerate(plan.get("recommended_actions", [])):
                if isinstance(action, Mapping):
                    candidates.append({
                        "candidate_id": action.get(
                            "recommended_action",
                            f"plan-candidate-{index + 1}",
                        ),
                        "predicted_gain": plan.get("projected_gain", 0.0),
                        "confidence": plan.get("improvement_confidence", 0.5),
                        "source": "performance_improvement_planner",
                    })

        optimization = inputs.get("parameter_optimization")
        if isinstance(optimization, Mapping) and optimization:
            candidates.append({
                "candidate_id": optimization.get(
                    "optimization_trace", {}
                ).get("optimization_id", "parameter-optimization"),
                "predicted_gain": optimization.get("optimization_gain", 0.0),
                "confidence": optimization.get("parameter_stability_index", 0.5),
                "source": "self_parameter_optimization_engine",
            })
        return candidates

    def build_prediction(
        self,
        inputs: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        context = deepcopy(dict(inputs or {}))
        raw_candidates = self._derive_candidates(context)
        normalized: list[dict[str, Any]] = []
        seen_candidate_ids: set[str] = set()

        for index, candidate in enumerate(raw_candidates):
            normalized_candidate = self._normalize_candidate(
                candidate,
                index,
            )
            candidate_id = normalized_candidate["candidate_id"]

            if candidate_id in seen_candidate_ids:
                raise ValueError(
                    f"duplicate_candidate_id:{candidate_id}"
                )

            seen_candidate_ids.add(candidate_id)
            normalized.append(normalized_candidate)

        normalized.sort(
            key=lambda item: (
                -item["prediction_score"],
                -item["predicted_gain"],
                item["risk"],
                item["candidate_id"],
            )
        )
        ranked = []
        for rank, item in enumerate(normalized, start=1):
            ranked_item = deepcopy(item)
            ranked_item["rank"] = rank
            ranked.append(ranked_item)

        recommended = ranked[0]["candidate_id"] if ranked else None
        result = {
            "primitive": PRIMITIVE,
            "status": STATUS,
            "prediction_ready": True,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "candidate_count": len(ranked),
            "ranked_candidates": ranked,
            "recommended_candidate_id": recommended,
            "execution_authorized": False,
            "selection_performed": False,
            "schedule_created": False,
            "installation_completed": False,
            "mutation_executed": False,
            "rollback_performed": False,
            "functional_conclusion_only": True,
            "epistemic_status": deepcopy(EPISTEMIC_STATUS),
            "diagnostics": {
                "input_candidate_count": len(raw_candidates),
                "ranking_policy": "gain_confidence_reversibility_validation_non_closure_minus_risk",
                "read_only": True,
                "producer_boundaries_preserved": True,
            },
            "persist_requested": False,
            "persisted": False,
            "artifacts": {
                "json_path": None,
            },
        }
        result["prediction_hash"] = _hash_payload(result)
        return result

    def verify_prediction(
        self,
        prediction: Mapping[str, Any],
    ) -> dict[str, Any]:
        errors: list[str] = []
        payload = dict(prediction)
        if payload.get("status") != STATUS:
            errors.append("invalid_status")
        if payload.get("prediction_ready") is not True:
            errors.append("prediction_not_ready")
        for field in FORBIDDEN_TRUE_FIELDS:
            if payload.get(field) is not False:
                errors.append(f"forbidden_true:{field}")
        if payload.get("epistemic_status") != EPISTEMIC_STATUS:
            errors.append("epistemic_status_violation")
        ranked = payload.get("ranked_candidates", [])
        if not isinstance(ranked, list):
            errors.append("ranked_candidates_not_list")
        else:
            expected = sorted(
                ranked,
                key=lambda item: (
                    -_number(item.get("prediction_score"), 0.0),
                    -_number(item.get("predicted_gain"), 0.0),
                    _number(item.get("risk"), 0.0),
                    str(item.get("candidate_id", "")),
                ),
            )
            if ranked != expected:
                errors.append("ranking_not_canonical")
        if payload.get("prediction_hash") != _hash_payload(payload):
            errors.append("prediction_hash_mismatch")
        return {
            "verified": not errors,
            "verification_errors": errors,
        }

    @staticmethod
    def _atomic_write(path: Path, text: str, filesystem_effect_context) -> None:
        if filesystem_effect_context is None:
            raise PermissionError("filesystem_effect_context_required")
        if not path.parent.exists():
            filesystem_effect_context.execute_path(
                "prediction_parent_create", "FS_CREATE_DIR", path.parent
            )
        filesystem_effect_context.execute_path(
            "prediction_write_replace", "FS_WRITE_REPLACE_BYTES", path,
            payload=text.encode("utf-8"),
        )

    def step(
        self,
        inputs: Mapping[str, Any] | None = None,
        persist: bool = False,
        filesystem_effect_context=None,
    ) -> dict[str, Any]:
        result = self.build_prediction(inputs=inputs)
        verification = self.verify_prediction(result)
        if not verification["verified"]:
            raise ValueError(
                "invalid_prediction:" + ",".join(
                    verification["verification_errors"]
                )
            )
        result["persist_requested"] = bool(persist)
        if persist:
            json_path = (
                self.runtime_dir / "latest_prediction.json"
            ).resolve()
            result["persisted"] = True
            result["artifacts"]["json_path"] = str(json_path)
            persisted = deepcopy(result)
            text = json.dumps(
                persisted,
                ensure_ascii=False,
                sort_keys=True,
                indent=2,
                allow_nan=False,
            )
            self._atomic_write(json_path, text, filesystem_effect_context)
        return result
