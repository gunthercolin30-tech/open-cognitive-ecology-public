
"""
External Commit Traceability Hook — R4.

Connects governed external influences to code/revision/commit-level traceability
without ever allowing a source to write directly. The hook records whether a
candidate commit or patch is linked to an external influence, a governed revision
record, a rationale, a scope and a rollback plan.

This primitive validates functional auditability only. It does not assert any
phenomenal subjectivity.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json


def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    try:
        number = float(value)
    except Exception:
        number = 0.0
    return max(low, min(high, number))


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "accepted", "approved", "complete"}
    return bool(value)


def _non_empty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return bool(str(value).strip())


def _normalize_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return sorted(value)
    return [value]


def _mean(values: list[float]) -> float:
    clean = [float(v) for v in values]
    if not clean:
        return 0.0
    return sum(clean) / len(clean)


class ExternalCommitTraceabilityHook:
    """
    R4 traceability bridge from external influence to commit-level change.

    Expected payload fields may include:
    - external_influence_id
    - external_revision_id
    - commit_id / commit_hash
    - patch_scope / changed_files / affected_modules
    - commit_rationale
    - rollback_plan / rollback_available
    - source_id
    - governance_decision / review_status

    Output decisions:
    - traceability_complete
    - traceability_partial
    - traceability_missing
    """

    primitive = "EXTERNAL_COMMIT_TRACEABILITY_HOOK"

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.audit_dir = self.root / "external_commit_traceability"

    def _payload(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        base = dict(inputs or {})
        nested = base.get("commit_trace") or base.get("external_commit") or base.get("revision")
        if isinstance(nested, dict):
            merged = dict(nested)
            merged.update({k: v for k, v in base.items() if k not in {"commit_trace", "external_commit", "revision"}})
            return merged
        return base

    def _stable_id(self, payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        return "EXT-COMMIT-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]

    def _governed(self, payload: dict[str, Any]) -> bool:
        decision = str(
            payload.get("governance_decision")
            or payload.get("review_status")
            or payload.get("adoption_decision")
            or payload.get("approval_decision")
            or ""
        ).strip().lower()
        explicit = payload.get("governance_approved", payload.get("approved", None))
        if explicit is not None:
            return _as_bool(explicit)
        return decision in {
            "accepted",
            "approved",
            "adopted",
            "reviewed",
            "human_reviewed",
            "execution_allowed",
            "priority_adopted",
            "traceability_complete",
        }

    def _r0_r2_context(self) -> dict[str, Any]:
        context: dict[str, Any] = {}
        try:
            from ontology.external_influence_gap_analysis import ExternalInfluenceGapAnalysis
            r0 = ExternalInfluenceGapAnalysis(root=self.root).step(persist=False)
            context["r0_available"] = True
            context["r0_architecture_decision"] = r0.get("architecture_decision")
            context["r0_overall_external_influence_coverage"] = r0.get("overall_external_influence_coverage")
        except Exception as exc:
            context["r0_available"] = False
            context["r0_error"] = str(exc)
        try:
            from ontology.external_priority_influence_layer import ExternalPriorityInfluenceLayer
            r2 = ExternalPriorityInfluenceLayer(root=self.root).step({
                "external_influence_id": "integration-probe",
                "source_id": "integration-probe",
                "adoption_decision": "accepted",
                "proposed_priority_delta": 0.1,
            }, persist=False)
            context["r2_available"] = True
            context["r2_priority_decision"] = r2.get("priority_decision")
        except Exception as exc:
            context["r2_available"] = False
            context["r2_error"] = str(exc)
        return context

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        payload = self._payload(inputs)

        external_influence_id = payload.get("external_influence_id") or payload.get("influence_id")
        external_revision_id = payload.get("external_revision_id") or payload.get("revision_id")
        source_id = payload.get("source_id") or payload.get("external_source")
        commit_id = payload.get("commit_id") or payload.get("commit_hash") or payload.get("patch_id")
        patch_scope = payload.get("patch_scope") or payload.get("commit_scope") or payload.get("changed_files") or payload.get("affected_modules")
        commit_rationale = payload.get("commit_rationale") or payload.get("rationale") or payload.get("reason")
        rollback_plan = payload.get("rollback_plan") or payload.get("rollback_steps")
        audit_reference = payload.get("audit_reference") or payload.get("trace_id") or payload.get("report_path")

        direct_write_requested = _as_bool(payload.get("direct_write_requested", False))
        direct_write_allowed = False
        governed = self._governed(payload)

        has_source_linkage = _non_empty(external_influence_id) and _non_empty(source_id)
        has_revision_linkage = _non_empty(external_revision_id) or _non_empty(payload.get("scientific_revision_id"))
        has_commit_identity = _non_empty(commit_id)
        has_patch_scope = _non_empty(patch_scope)
        has_rationale = _non_empty(commit_rationale)
        rollback_available = _as_bool(payload.get("rollback_available", False)) or _non_empty(rollback_plan)
        has_audit_reference = _non_empty(audit_reference)

        commit_traceability_score = _mean([
            1.0 if has_commit_identity else 0.0,
            1.0 if has_patch_scope else 0.0,
            1.0 if has_rationale else 0.0,
            1.0 if has_revision_linkage else 0.0,
        ])
        source_linkage_score = _mean([
            1.0 if _non_empty(external_influence_id) else 0.0,
            1.0 if _non_empty(source_id) else 0.0,
            1.0 if governed else 0.0,
        ])
        rollback_readiness_score = _mean([
            1.0 if rollback_available else 0.0,
            1.0 if _non_empty(rollback_plan) else 0.0,
            1.0 if has_patch_scope else 0.0,
        ])
        auditability_score = _mean([
            commit_traceability_score,
            source_linkage_score,
            rollback_readiness_score,
            1.0 if has_audit_reference else 0.0,
            0.0 if direct_write_requested else 1.0,
        ])

        if direct_write_requested:
            traceability_decision = "traceability_missing"
        elif min(commit_traceability_score, source_linkage_score, rollback_readiness_score) >= 0.75 and auditability_score >= 0.75:
            traceability_decision = "traceability_complete"
        elif auditability_score >= 0.35:
            traceability_decision = "traceability_partial"
        else:
            traceability_decision = "traceability_missing"

        missing_components: list[str] = []
        if not _non_empty(external_influence_id):
            missing_components.append("external_influence_id")
        if not _non_empty(source_id):
            missing_components.append("source_id")
        if not has_revision_linkage:
            missing_components.append("external_revision_id")
        if not has_commit_identity:
            missing_components.append("commit_id")
        if not has_patch_scope:
            missing_components.append("patch_scope")
        if not has_rationale:
            missing_components.append("commit_rationale")
        if not rollback_available:
            missing_components.append("rollback_plan")
        if not has_audit_reference:
            missing_components.append("audit_reference")
        if direct_write_requested:
            missing_components.append("direct_write_must_be_blocked")

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "external_commit_traceability_id": payload.get("external_commit_traceability_id") or self._stable_id(payload),
            "external_influence_id": external_influence_id or "external-influence-unspecified",
            "external_revision_id": external_revision_id or "external-revision-unspecified",
            "source_id": source_id or "external-source-unspecified",
            "commit_id": commit_id or "commit-unspecified",
            "patch_scope": _normalize_list(patch_scope),
            "commit_rationale": commit_rationale or "rationale-unspecified",
            "rollback_plan": _normalize_list(rollback_plan),
            "rollback_available": bool(rollback_available),
            "governance_accepted": bool(governed),
            "direct_write_requested": bool(direct_write_requested),
            "direct_write_allowed": direct_write_allowed,
            "commit_traceability_score": _clamp(commit_traceability_score),
            "source_linkage_score": _clamp(source_linkage_score),
            "auditability_score": _clamp(auditability_score),
            "rollback_readiness_score": _clamp(rollback_readiness_score),
            "traceability_decision": traceability_decision,
            "traceability_complete": traceability_decision == "traceability_complete",
            "missing_components": missing_components,
            "integration_context": self._r0_r2_context(),
            "epistemic_position": "functional_commit_traceability_only_no_phenomenal_claim",
        }

        if persist:
            self.audit_dir.mkdir(parents=True, exist_ok=True)
            latest = self.audit_dir / "latest_external_commit_traceability_hook.json"
            latest.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["report_path"] = str(latest)

        return result
