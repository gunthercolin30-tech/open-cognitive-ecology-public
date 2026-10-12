\
"""ACEE1 — governed capability map for Autonomous Cognitive Evolution Engine.

Consumes ACEE0 integration-audit output and produces a deterministic mapping
from ACEE stages to reusable modules, coverage levels and governed actions.
"""
from __future__ import annotations

import fcntl
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

from ontology.acee_integration_auditor import AceeIntegrationAuditor

PRIMITIVE = "ACEE_CAPABILITY_MAP"
STATUS_READY = "ACEE_CAPABILITY_MAP_READY"
STATUS_DEGRADED = "ACEE_CAPABILITY_MAP_DEGRADED"
PUBLIC_SCHEMA_VERSION = "1.0.0"
DEPENDENCIES = [
    "acee_integration_auditor",
    "autonomous_capability_discovery",
    "open_ended_capability_discovery_engine",
    "node_capability_registry",
    "external_capability_planner",
    "ontology_gap_detector",
    "scientific_supervision_gap_analysis",
    "metrics_history_recorder",
    "validation_history_archive",
    "epistemic_guard",
]

LEVEL_SCORES = {
    "covered": 1.0,
    "substantially_covered": 0.75,
    "partially_covered": 0.5,
    "weakly_covered": 0.25,
    "missing": 0.0,
    "deferred": None,
}

CAPABILITY_SPECS = {
    "ACEE0": ("integration audit", ("acee_integration_auditor",)),
    "ACEE1": ("capability mapping", ("acee_capability_map",)),
    "ACEE2": ("meta orchestration", ("controlled_evolution_orchestrator", "recursive_self_improvement_controller")),
    "ACEE3": ("bridge adaptation", ("auto_improvement_runtime_bridge",)),
    "ACEE4": ("autonomous cycle management", ("runtime_experiment_manager", "controlled_evolution_orchestrator")),
    "ACEE5": ("governed code generation", ("automated_primitive_designer", "constitutional_evolution_gate")),
    "ACEE6": ("governed installation", ("controlled_execution_layer", "constitutional_evolution_gate")),
    "ACEE7": ("validation execution", ("validation_history_archive", "scientific_consistency_validator")),
    "ACEE8": ("impact evaluation", ("effectiveness_assessment", "trajectory_outcome_evaluation")),
    "ACEE9": ("causal effect analysis", ("causal_inference", "advanced_causal_reasoning_engine")),
    "ACEE10": ("selection policy", ("trajectory_selection", "approval_or_rejection")),
    "ACEE11": ("rollback", ("failure_recovery_orchestrator", "trajectory_reversibility")),
    "ACEE12": ("architecture genealogy", ("genealogical_evolution_dashboard", "genealogical_continuity")),
    "ACEE13": ("lineage management", ("runtime_lineage_inheritance", "multi_lineage_topology")),
    "ACEE14": ("best architecture archive", ("civilizational_historical_archive", "validation_history_archive")),
    "ACEE15": ("autonomous scheduling", ("continuous_civilizational_scheduler", "scientific_priority_scheduler")),
    "ACEE16": ("longitudinal tracking", ("longitudinal_metrics_archive", "metrics_history_recorder")),
    "ACEE17": ("dashboard", ("genealogical_evolution_dashboard", "scientific_meta_dashboard")),
    "ACEE18": ("evolution prediction", ("performance_improvement_planner", "trajectory_prediction")),
    "ACEE19": ("meta analysis", ("scientific_meta_analysis_engine", "constitutional_meta_analysis_engine")),
    "ACEE20": ("final certification", ("ecological_certifier", "civilizational_scientific_certification")),
}
DEFERRED_STAGES = {"ACEE5", "ACEE6"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def _finite(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(number):
        return default
    return max(0.0, min(1.0, number))


def _names(values: Any) -> list[str]:
    if not isinstance(values, Iterable) or isinstance(values, (str, bytes, Mapping)):
        return []
    return sorted({str(value).strip() for value in values if str(value).strip()})


def _stage_key(value: str) -> int:
    return int(value[4:])


def _level(score: float) -> str:
    if score >= 0.875:
        return "covered"
    if score >= 0.625:
        return "substantially_covered"
    if score >= 0.375:
        return "partially_covered"
    if score > 0.0:
        return "weakly_covered"
    return "missing"


@dataclass
class AceeCapabilityMap:
    root: Path | None = None

    def __post_init__(self) -> None:
        self.root = Path(self.root) if self.root is not None else Path.home() / "open-cognitive-ecology"

    def _paths(self) -> tuple[Path, Path, Path]:
        directory = self.root / "acee_runtime" / "ACEE1_acee_capability_map"
        return (
            directory / "latest_capability_map.json",
            directory / "capability_map_history.jsonl",
            directory / ".capability_map.lock",
        )

    def _source_audit(self, supplied: Mapping[str, Any]) -> dict[str, Any]:
        direct = supplied.get("integration_audit") or supplied.get("source_audit")
        if isinstance(direct, Mapping):
            return dict(direct)
        audit_inputs = supplied.get("audit_inputs")
        if audit_inputs is not None and not isinstance(audit_inputs, Mapping):
            audit_inputs = {}
        return AceeIntegrationAuditor(root=self.root).step(inputs=audit_inputs, persist=False)

    def _entry(self, stage: str, audit: Mapping[str, Any], modules: list[str]) -> dict[str, Any]:
        capability, preferred = CAPABILITY_SPECS[stage]
        installed = set(modules)
        source_matrix = audit.get("coverage_matrix", {})
        source_entry = source_matrix.get(stage, {}) if isinstance(source_matrix, Mapping) else {}
        source_candidates = _names(source_entry.get("candidate_modules", [])) if isinstance(source_entry, Mapping) else []
        candidates = sorted(set(source_candidates) | (installed & set(preferred)))
        if stage == "ACEE1" and "acee_capability_map" in installed:
            candidates = ["acee_capability_map"] + [item for item in candidates if item != "acee_capability_map"]
            score = 1.0
        else:
            source_score = _finite(source_entry.get("coverage_score", 0.0)) if isinstance(source_entry, Mapping) else 0.0
            preferred_fraction = len(installed & set(preferred)) / len(preferred) if preferred else 0.0
            score = max(source_score, preferred_fraction)
        if stage in DEFERRED_STAGES:
            coverage_level = "deferred"
            action = "defer_governed_implementation"
            score_value = None
            justification = "Implementation is deliberately deferred because autonomous code generation or installation requires later governance gates."
        else:
            coverage_level = _level(score)
            score_value = round(score, 6)
            if coverage_level == "covered":
                action = "reuse"
            elif coverage_level in {"substantially_covered", "partially_covered"}:
                action = "integrate_or_refine"
            elif coverage_level == "weakly_covered":
                action = "refine_after_targeted_audit"
            else:
                action = "create_after_non_redundancy_audit"
            justification = (
                f"{len(candidates)} candidate module(s) support {capability}; "
                f"normalized functional coverage is {score_value:.6f}."
                if candidates
                else f"No installed candidate supports {capability}; governed creation remains conditional on a dedicated non-redundancy audit."
            )
        primary = candidates[0] if candidates else None
        confidence = 1.0 if stage in DEFERRED_STAGES else round(min(1.0, 0.5 + (0.5 * score)), 6)
        return {
            "acee_stage": stage,
            "capability": capability,
            "candidate_modules": candidates,
            "primary_module": primary,
            "coverage_level": coverage_level,
            "coverage_score": score_value,
            "confidence": confidence,
            "recommended_action": action,
            "justification": justification,
        }

    def _read_previous(self, history_path: Path) -> tuple[dict[str, Any] | None, bool]:
        if not history_path.is_file():
            return None, False
        try:
            lines = [line for line in history_path.read_text(encoding="utf-8").splitlines() if line.strip()]
            return (json.loads(lines[-1]), False) if lines else (None, False)
        except (OSError, json.JSONDecodeError):
            return None, True

    def step(self, inputs: Mapping[str, Any] | None = None, persist: bool = False) -> dict[str, Any]:
        supplied = dict(inputs or {})
        audit = self._source_audit(supplied)
        modules = _names(audit.get("existing_modules", []))
        if supplied.get("modules") is not None:
            modules = _names(supplied.get("modules"))
        matrix = {
            stage: self._entry(stage, audit, modules)
            for stage in sorted(CAPABILITY_SPECS, key=_stage_key)
        }
        operational = [entry for entry in matrix.values() if entry["coverage_level"] != "deferred"]
        coverage_score = round(sum(float(entry["coverage_score"] or 0.0) for entry in operational) / len(operational), 6)
        weights = supplied.get("weights", {})
        if not isinstance(weights, Mapping):
            weights = {}
        normalized_weights = {stage: max(0.0, _finite(weights.get(stage, 1.0), 1.0)) for stage in matrix if stage not in DEFERRED_STAGES}
        total_weight = sum(normalized_weights.values()) or float(len(normalized_weights))
        weighted_score = round(sum(float(matrix[stage]["coverage_score"] or 0.0) * normalized_weights[stage] for stage in normalized_weights) / total_weight, 6)
        distribution = {level: sum(1 for entry in matrix.values() if entry["coverage_level"] == level) for level in LEVEL_SCORES}
        capability_to_modules = {stage: entry["candidate_modules"] for stage, entry in matrix.items()}
        module_to_capabilities: dict[str, list[str]] = {}
        for stage, candidates in capability_to_modules.items():
            for module in candidates:
                module_to_capabilities.setdefault(module, []).append(stage)
        module_to_capabilities = {module: sorted(stages, key=_stage_key) for module, stages in sorted(module_to_capabilities.items())}
        recommendations = [{
            "acee_stage": stage,
            "action": entry["recommended_action"],
            "primary_module": entry["primary_module"],
            "justification": entry["justification"],
        } for stage, entry in matrix.items()]
        latest_path, history_path, lock_path = self._paths()
        previous, corrupted = self._read_previous(history_path)
        previous_hash = "" if not previous or corrupted else str(previous.get("mapping_hash", ""))
        degraded_reasons: list[str] = []
        if audit.get("audit_status") != "ACEE_INTEGRATION_AUDIT_COMPLETE":
            degraded_reasons.append("source_audit_not_complete")
        if not modules:
            degraded_reasons.append("empty_source_module_inventory")
        if corrupted:
            degraded_reasons.append("history_corrupted")
        timestamp = str(supplied.get("map_timestamp_utc") or _utc_now())
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            degraded_reasons.append("invalid_map_timestamp")
        payload = {
            "primitive": PRIMITIVE,
            "public_schema_version": PUBLIC_SCHEMA_VERSION,
            "capability_map_status": STATUS_DEGRADED if degraded_reasons else STATUS_READY,
            "capability_map_ready": not degraded_reasons,
            "map_timestamp_utc": timestamp,
            "source_audit_id": audit.get("audit_id"),
            "source_audit_hash": audit.get("audit_hash"),
            "source_integration_hash": audit.get("integration_hash"),
            "capability_matrix": matrix,
            "capability_count": len(matrix),
            "covered_capabilities": [stage for stage, entry in matrix.items() if entry["coverage_level"] == "covered"],
            "partially_covered_capabilities": [stage for stage, entry in matrix.items() if entry["coverage_level"] in {"substantially_covered", "partially_covered", "weakly_covered"}],
            "missing_capabilities": [stage for stage, entry in matrix.items() if entry["coverage_level"] == "missing"],
            "deferred_capabilities": [stage for stage, entry in matrix.items() if entry["coverage_level"] == "deferred"],
            "coverage_score": coverage_score,
            "weighted_coverage_score": weighted_score,
            "coverage_distribution": distribution,
            "capability_to_modules": capability_to_modules,
            "module_to_capabilities": module_to_capabilities,
            "primary_reuse_modules": sorted({entry["primary_module"] for entry in matrix.values() if entry["recommended_action"] == "reuse" and entry["primary_module"]}),
            "secondary_reuse_modules": sorted({module for entry in matrix.values() for module in entry["candidate_modules"][1:]}),
            "refinement_candidates": [stage for stage, entry in matrix.items() if entry["recommended_action"] in {"integrate_or_refine", "refine_after_targeted_audit"}],
            "creation_candidates": [stage for stage, entry in matrix.items() if entry["recommended_action"] == "create_after_non_redundancy_audit"],
            "recommended_actions": recommendations,
            "recommendation_justifications_complete": all(bool(item["justification"].strip()) for item in recommendations),
            "confidence_score": round(sum(float(entry["confidence"]) for entry in matrix.values()) / len(matrix), 6),
            "previous_mapping_hash": previous_hash,
            "degraded_reasons": degraded_reasons,
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
        hash_body = dict(payload)
        hash_body.pop("map_timestamp_utc", None)
        payload["mapping_hash"] = _sha256({"previous_mapping_hash": previous_hash, "payload": hash_body})
        payload["map_id"] = "ACEE1-" + payload["mapping_hash"][:16]
        payload["persisted"] = False
        payload["output_path"] = str(latest_path)
        payload["history_path"] = str(history_path)
        if persist:
            latest_path.parent.mkdir(parents=True, exist_ok=True)
            with lock_path.open("a+", encoding="utf-8") as lock_handle:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
                previous_locked, corrupted_locked = self._read_previous(history_path)
                locked_previous_hash = "" if not previous_locked or corrupted_locked else str(previous_locked.get("mapping_hash", ""))
                payload["previous_mapping_hash"] = locked_previous_hash
                hash_body = dict(payload)
                for key in ("mapping_hash", "map_id", "persisted", "output_path", "history_path", "map_timestamp_utc"):
                    hash_body.pop(key, None)
                payload["mapping_hash"] = _sha256({"previous_mapping_hash": locked_previous_hash, "payload": hash_body})
                payload["map_id"] = "ACEE1-" + payload["mapping_hash"][:16]
                stored = dict(payload)
                stored["persisted"] = True
                latest_path.write_text(json.dumps(stored, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
                with history_path.open("a", encoding="utf-8") as history:
                    history.write(json.dumps(stored, sort_keys=True, ensure_ascii=False) + "\n")
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
            payload["persisted"] = True
        return payload
