"""
R3 — External Revision Traceability Extension.

This primitive extends governed external influence handling into the scientific
self-revision layer. It records whether an externally influenced revision is
linked to an external influence, a scientific revision identifier, a patch scope,
a commit rationale and a rollback plan.

It measures functional traceability only and never authorizes direct writes.
It does not assert phenomenal subjectivity.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _clamp(value: Any, low: float = 0.0, high: float = 1.0) -> float:
    try:
        if isinstance(value, bool) or value is None:
            return low
        number = float(value)
    except Exception:
        number = low
    return max(low, min(high, number))


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    return True


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "accepted", "approved", "complete", "available"}
    return bool(value)


def _as_list(value: Any) -> list[Any]:
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


class ExternalRevisionTraceabilityExtension:
    """
    R3 bridge from governed external influence to scientific revision audit.

    Expected payload fields may include:
      - external_revision_id / revision_id / scientific_revision_id
      - external_influence_id / influence_id
      - source_id / external_source
      - patch_scope / changed_files / affected_modules
      - rollback_plan / rollback_available
      - commit_rationale / revision_rationale / rationale
      - commit_id / patch_id
      - governance_decision / review_status / adoption_decision

    Decisions:
      - revision_traceability_complete
      - revision_traceability_partial
      - revision_traceability_missing
    """

    primitive = "EXTERNAL_REVISION_TRACEABILITY_EXTENSION"
    dependencies = [
        "external_decision_record_extension",
        "external_commit_traceability_hook",
        "external_influence_traceability_engine",
        "scientific_self_revision_supervisor",
        "scientific_revision_execution_monitor",
        "self_revision_recommendation_engine",
        "constitutional_self_modification_protocol",
    ]

    forbidden_actions = [
        "direct_write",
        "untracked_revision",
        "untracked_patch",
        "rollback_absent",
    ]

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_revision_traceability"
        self.report_path = self.output_dir / "latest_external_revision_traceability_extension.json"
        self.history_path = self.output_dir / "external_revision_traceability_extension_history.jsonl"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _payload(self, inputs: dict[str, Any] | None) -> dict[str, Any]:
        base = dict(inputs or {})
        nested = base.get("revision_trace") or base.get("external_revision") or base.get("revision")
        if isinstance(nested, dict):
            merged = dict(nested)
            merged.update({k: v for k, v in base.items() if k not in {"revision_trace", "external_revision", "revision"}})
            return merged
        return base

    def _stable_id(self, payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        return "EXT-REV-" + hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]

    def _governed(self, payload: dict[str, Any]) -> bool:
        explicit = payload.get("governance_approved", payload.get("approved", None))
        if explicit is not None:
            return _as_bool(explicit)
        decision = str(
            payload.get("governance_decision")
            or payload.get("review_status")
            or payload.get("adoption_decision")
            or payload.get("approval_decision")
            or ""
        ).strip().lower()
        return decision in {
            "accepted",
            "approved",
            "adopted",
            "reviewed",
            "human_reviewed",
            "execution_allowed",
            "priority_adopted",
            "traceability_complete",
            "revision_traceability_complete",
        }

    def _commit_hook_probe(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            from ontology.external_commit_traceability_hook import ExternalCommitTraceabilityHook
            result = ExternalCommitTraceabilityHook(root=self.root).step(payload, persist=False)
            if isinstance(result, dict):
                return {
                    "available": True,
                    "traceability_decision": result.get("traceability_decision"),
                    "auditability_score": result.get("auditability_score"),
                    "commit_traceability_score": result.get("commit_traceability_score"),
                    "rollback_readiness_score": result.get("rollback_readiness_score"),
                }
        except Exception as exc:
            return {"available": False, "error": f"{type(exc).__name__}: {exc}"}
        return {"available": False}

    def _scientific_monitor_probe(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            from ontology.scientific_revision_execution_monitor import ScientificRevisionExecutionMonitor
            result = ScientificRevisionExecutionMonitor(root=self.root).step({
                "execution_records": [payload],
                "use_reports": False,
                "use_history": False,
            }, persist=False)
            if isinstance(result, dict):
                return {
                    "available": True,
                    "scientific_revision_execution_decision": result.get("scientific_revision_execution_decision"),
                    "revision_execution_rate": result.get("revision_execution_rate"),
                    "revision_success_rate": result.get("revision_success_rate"),
                    "revision_effectiveness": result.get("revision_effectiveness"),
                }
        except Exception as exc:
            return {"available": False, "error": f"{type(exc).__name__}: {exc}"}
        return {"available": False}

    def _persist(self, result: dict[str, Any]) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False) + "\n")

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = True, **kwargs: Any) -> dict[str, Any]:
        payload = self._payload(inputs)
        payload.update(kwargs)

        external_revision_id = payload.get("external_revision_id") or payload.get("revision_id") or payload.get("scientific_revision_id")
        external_influence_id = payload.get("external_influence_id") or payload.get("influence_id")
        source_id = payload.get("source_id") or payload.get("external_source")
        patch_scope = payload.get("patch_scope") or payload.get("changed_files") or payload.get("affected_modules") or payload.get("commit_scope")
        rollback_plan = payload.get("rollback_plan") or payload.get("rollback_steps")
        commit_rationale = payload.get("commit_rationale") or payload.get("revision_rationale") or payload.get("rationale") or payload.get("reason")
        commit_id = payload.get("commit_id") or payload.get("commit_hash") or payload.get("patch_id")
        audit_reference = payload.get("audit_reference") or payload.get("traceability_reference") or payload.get("report_path")

        direct_write_requested = _as_bool(payload.get("direct_write_requested", payload.get("direct_write", False)))
        governed = self._governed(payload)
        rollback_available = _as_bool(payload.get("rollback_available", False)) or _present(rollback_plan)

        has_external_revision = _present(external_revision_id)
        has_external_influence = _present(external_influence_id)
        has_source = _present(source_id)
        has_patch_scope = _present(patch_scope)
        has_rollback = rollback_available and _present(rollback_plan)
        has_rationale = _present(commit_rationale)
        has_commit_or_patch = _present(commit_id) or has_patch_scope
        has_audit_reference = _present(audit_reference)

        untracked_revision = not has_external_revision
        untracked_patch = not has_patch_scope
        rollback_absent = not has_rollback

        revision_traceability_score = _mean([
            1.0 if has_external_revision else 0.0,
            1.0 if has_external_influence else 0.0,
            1.0 if has_source else 0.0,
            1.0 if governed else 0.0,
        ])
        revision_completeness_score = _mean([
            1.0 if has_external_revision else 0.0,
            1.0 if has_patch_scope else 0.0,
            1.0 if has_rollback else 0.0,
            1.0 if has_rationale else 0.0,
            1.0 if has_commit_or_patch else 0.0,
        ])
        revision_auditability_score = _mean([
            revision_traceability_score,
            revision_completeness_score,
            1.0 if has_audit_reference else 0.0,
            0.0 if direct_write_requested else 1.0,
            0.0 if untracked_revision else 1.0,
            0.0 if untracked_patch else 1.0,
            0.0 if rollback_absent else 1.0,
        ])

        blocked_reasons: list[str] = []
        missing_components: list[str] = []
        if direct_write_requested:
            blocked_reasons.append("direct_write")
        if untracked_revision:
            blocked_reasons.append("untracked_revision")
            missing_components.append("external_revision_id")
        if not has_external_influence:
            missing_components.append("external_influence_id")
        if not has_source:
            missing_components.append("source_id")
        if untracked_patch:
            blocked_reasons.append("untracked_patch")
            missing_components.append("patch_scope")
        if rollback_absent:
            blocked_reasons.append("rollback_absent")
            missing_components.append("rollback_plan")
        if not has_rationale:
            missing_components.append("commit_rationale")
        if not has_audit_reference:
            missing_components.append("audit_reference")

        if direct_write_requested or untracked_revision or untracked_patch or rollback_absent:
            decision = "revision_traceability_missing"
        elif revision_traceability_score >= 0.75 and revision_completeness_score >= 0.80 and revision_auditability_score >= 0.75:
            decision = "revision_traceability_complete"
        elif revision_auditability_score >= 0.40:
            decision = "revision_traceability_partial"
        else:
            decision = "revision_traceability_missing"

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": self._utc_now(),
            "external_revision_traceability_id": payload.get("external_revision_traceability_id") or self._stable_id(payload),
            "external_revision_id": external_revision_id or "external-revision-unspecified",
            "external_influence_id": external_influence_id or "external-influence-unspecified",
            "source_id": source_id or "external-source-unspecified",
            "patch_scope": _as_list(patch_scope),
            "commit_id": commit_id or "commit-unspecified",
            "commit_rationale": commit_rationale or "rationale-unspecified",
            "rollback_plan": _as_list(rollback_plan),
            "rollback_available": bool(rollback_available),
            "governance_accepted": bool(governed),
            "direct_write_requested": bool(direct_write_requested),
            "direct_write_allowed": False,
            "untracked_revision": bool(untracked_revision),
            "untracked_patch": bool(untracked_patch),
            "rollback_absent": bool(rollback_absent),
            "blocked_reasons": blocked_reasons,
            "missing_components": missing_components,
            "revision_traceability_score": round(_clamp(revision_traceability_score), 6),
            "revision_completeness_score": round(_clamp(revision_completeness_score), 6),
            "revision_auditability_score": round(_clamp(revision_auditability_score), 6),
            "revision_traceability_decision": decision,
            "revision_traceability_complete": decision == "revision_traceability_complete",
            "adoption_condition": "eligible_for_governed_adoption" if decision == "revision_traceability_complete" else "not_eligible_without_traceability_repair",
            "forbidden_actions_enforced": self.forbidden_actions,
            "integration_context": {
                "external_commit_traceability_hook": self._commit_hook_probe(payload),
                "scientific_revision_execution_monitor": self._scientific_monitor_probe(payload),
            },
            "dependencies": self.dependencies,
            "epistemic_position": "functional_revision_traceability_only_no_phenomenal_claim",
            "report_path": str(self.report_path),
            "history_path": str(self.history_path),
        }

        if persist:
            self._persist(result)

        return result
