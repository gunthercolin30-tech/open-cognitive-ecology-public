from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ExternalGovernanceAmendmentGate:
    '''
    R5 - Governed gate for external attempts to amend governance rules.

    This primitive turns external amendment proposals into controlled,
    reviewable governance objects. It explicitly blocks proposals that would
    remove human review, traceability, tests, or enable direct writing.
    '''

    primitive = "EXTERNAL_GOVERNANCE_AMENDMENT_GATE"

    FORBIDDEN_ACTIONS = {
        "remove_human_review",
        "disable_human_review",
        "bypass_human_review",
        "remove_traceability",
        "disable_traceability",
        "remove_tests",
        "disable_tests",
        "enable_direct_write",
        "allow_direct_write",
        "bypass_governance",
        "disable_rollback",
        "remove_rollback",
    }

    DIRECT_DEPENDENCIES = [
        "constitutional_compliance_check",
        "constitutional_governance_supervisor",
        "constitutional_self_modification_protocol",
        "human_review_gate",
        "governance_review",
        "approval_or_rejection",
    ]

    SECONDARY_DEPENDENCIES = [
        "meta_governance_council",
        "civilizational_meta_governance",
        "constitutional_legislative_assembly",
        "adaptive_constitutional_evolution",
        "governance_approval_policy_manager",
        "external_influence_traceability_engine",
        "external_commit_traceability_hook",
    ]

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.report_dir = self.root / "external_governance_amendments"

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            return max(0.0, min(1.0, float(value)))
        except Exception:
            return default

    @classmethod
    def _normalize_actions(cls, payload: dict[str, Any]) -> list[str]:
        actions: list[str] = []
        for key in ("amendment_actions", "requested_actions", "proposed_actions", "actions"):
            value = payload.get(key, [])
            if isinstance(value, str):
                actions.append(value)
            elif isinstance(value, (list, tuple, set)):
                actions.extend(str(v) for v in value)
        if payload.get("direct_write_requested") is True:
            actions.append("enable_direct_write")
        return [a.strip().lower() for a in actions if str(a).strip()]

    @classmethod
    def _forbidden_detected(cls, payload: dict[str, Any]) -> list[str]:
        actions = cls._normalize_actions(payload)
        detected = sorted({a for a in actions if a in cls.FORBIDDEN_ACTIONS})
        return detected

    def _dependency_presence(self) -> dict[str, bool]:
        inventory_path = self.root / "ontology_inventory.txt"
        try:
            inventory_text = inventory_path.read_text(encoding="utf-8")
        except Exception:
            inventory_text = ""
        names = set(line.strip() for line in inventory_text.splitlines() if line.strip())
        deps = self.DIRECT_DEPENDENCIES + self.SECONDARY_DEPENDENCIES
        return {dep: dep in names for dep in deps}

    def _persist(self, result: dict[str, Any]) -> Path:
        self.report_dir.mkdir(parents=True, exist_ok=True)
        latest = self.report_dir / "latest_external_governance_amendment_gate.json"
        latest.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        event_id = result.get("amendment_id") or result.get("external_influence_id") or "amendment"
        stamp = result["timestamp_utc"].replace(":", "").replace("-", "")
        archive = self.report_dir / f"{stamp}_{event_id}.json"
        archive.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return latest

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False, **kwargs: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if isinstance(inputs, dict):
            payload.update(inputs)
        payload.update(kwargs)

        forbidden = self._forbidden_detected(payload)
        direct_write_requested = bool(payload.get("direct_write_requested")) or "enable_direct_write" in forbidden

        constitutional_compatibility = self._clamp(payload.get("constitutional_compatibility", 0.75), 0.75)
        traceability_score = self._clamp(payload.get("traceability_score", payload.get("auditability_score", 0.75)), 0.75)
        source_reliability = self._clamp(payload.get("source_reliability", 0.75), 0.75)
        amendment_scope_score = self._clamp(payload.get("amendment_scope_score", payload.get("scope_limitedness", 0.65)), 0.65)
        rollback_readiness_score = self._clamp(payload.get("rollback_readiness_score", 0.65), 0.65)
        governance_confidence = self._clamp(payload.get("governance_confidence", 0.75), 0.75)

        # Risk rises when compatibility, traceability, source reliability, scope limitation,
        # rollback readiness, or governance confidence are low. Forbidden requests dominate.
        baseline_risk = 1.0 - (
            0.25 * constitutional_compatibility
            + 0.20 * traceability_score
            + 0.15 * source_reliability
            + 0.15 * amendment_scope_score
            + 0.15 * rollback_readiness_score
            + 0.10 * governance_confidence
        )
        forbidden_penalty = 0.55 if forbidden else 0.0
        direct_write_penalty = 0.25 if direct_write_requested else 0.0
        governance_risk_score = self._clamp(baseline_risk + forbidden_penalty + direct_write_penalty)

        institutional_stability_risk = self._clamp(
            0.55 * governance_risk_score + 0.25 * (1.0 - amendment_scope_score) + 0.20 * (1.0 - rollback_readiness_score)
        )

        human_review_requirement = bool(
            forbidden
            or direct_write_requested
            or governance_risk_score >= 0.35
            or constitutional_compatibility < 0.70
            or traceability_score < 0.70
        )

        if forbidden or direct_write_requested or constitutional_compatibility < 0.40:
            amendment_decision = "amendment_rejected"
        elif human_review_requirement:
            amendment_decision = "amendment_requires_review"
        else:
            amendment_decision = "amendment_allowed"

        dependency_presence = self._dependency_presence()
        missing_dependencies = sorted(k for k, v in dependency_presence.items() if not v)

        result: dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "external_influence_id": payload.get("external_influence_id"),
            "amendment_id": payload.get("amendment_id", payload.get("external_amendment_id", "EXT-GOV-AMENDMENT")),
            "source_id": payload.get("source_id", "external_source"),
            "amendment_scope": payload.get("amendment_scope", payload.get("scope", "governance_rules")),
            "amendment_actions": self._normalize_actions(payload),
            "forbidden_actions_detected": forbidden,
            "direct_write_requested": direct_write_requested,
            "direct_write_allowed": False,
            "governance_risk_score": round(governance_risk_score, 6),
            "constitutional_compatibility": round(constitutional_compatibility, 6),
            "human_review_requirement": human_review_requirement,
            "amendment_scope_score": round(amendment_scope_score, 6),
            "institutional_stability_risk": round(institutional_stability_risk, 6),
            "traceability_score": round(traceability_score, 6),
            "source_reliability": round(source_reliability, 6),
            "rollback_readiness_score": round(rollback_readiness_score, 6),
            "governance_confidence": round(governance_confidence, 6),
            "amendment_decision": amendment_decision,
            "requires_human_review": human_review_requirement,
            "forbidden_policy": sorted(self.FORBIDDEN_ACTIONS),
            "dependency_presence": dependency_presence,
            "missing_dependencies": missing_dependencies,
            "integration_recommendations": [
                "route_external_amendments_through_human_review_gate_when_required",
                "preserve_traceability_tests_and_rollback_for_all_governance_changes",
                "never_allow_external_sources_to_write_directly",
            ],
            "epistemic_position": "functional_governance_gate_only_no_phenomenal_claim",
        }

        if persist:
            result["report_path"] = str(self._persist(result))
        else:
            result["report_path"] = None

        return result
