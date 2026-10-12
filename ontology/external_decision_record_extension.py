from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ExternalDecisionRecordExtension:
    """External decision record extension for governed external influence.

    This primitive does not execute decisions and never authorizes direct writes.
    It creates an auditable EXTERNAL-DECISION-* record linking external influence,
    governance review, revision, execution and traceability evidence.
    """

    primitive = "EXTERNAL_DECISION_RECORD_EXTENSION"
    dependencies = [
        "external_influence_traceability_engine",
        "external_influence_gap_analysis",
        "external_priority_influence_layer",
        "external_commit_traceability_hook",
        "external_governance_amendment_gate",
        "external_influence_impact_monitor",
        "governance_review",
        "approval_or_rejection",
        "scientific_revision_execution_monitor",
        "execution_request_generation",
    ]

    def __init__(self, root: str | Path | None = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_decision_records"

    @staticmethod
    def _clamp(value: Any, default: float = 0.0) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = default
        return max(0.0, min(1.0, number))

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        return [value]

    @staticmethod
    def _present(value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, tuple, set, dict)):
            return len(value) > 0
        return True

    def _make_decision_id(self, payload: dict[str, Any]) -> str:
        explicit = payload.get("external_decision_id") or payload.get("decision_record_id")
        if self._present(explicit):
            return str(explicit)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        influence = str(payload.get("external_influence_id") or "UNSPECIFIED").replace(" ", "-")
        return f"EXTERNAL-DECISION-{influence}-{stamp}"

    def _score_traceability(self, payload: dict[str, Any]) -> float:
        fields = [
            payload.get("external_influence_id"),
            payload.get("source_id"),
            payload.get("external_decision_id") or payload.get("decision_record_id"),
            payload.get("governance_decision"),
            payload.get("traceability_reference") or payload.get("audit_reference"),
            payload.get("external_revision_id"),
            payload.get("commit_id"),
            payload.get("rollback_plan"),
        ]
        return sum(1 for item in fields if self._present(item)) / len(fields)

    def _score_completeness(self, payload: dict[str, Any]) -> float:
        fields = [
            payload.get("external_influence_id"),
            payload.get("external_decision_id") or payload.get("decision_record_id"),
            payload.get("decision_type"),
            payload.get("decision_status") or payload.get("governance_decision"),
            payload.get("decision_rationale"),
            payload.get("governance_decision"),
            payload.get("revision_decision"),
            payload.get("execution_decision"),
            payload.get("traceability_reference") or payload.get("audit_reference"),
            payload.get("rollback_plan"),
        ]
        return sum(1 for item in fields if self._present(item)) / len(fields)

    def _decide(self, traceability: float, completeness: float, direct_write_requested: bool) -> str:
        if direct_write_requested:
            return "decision_record_rejected"
        if traceability >= 0.75 and completeness >= 0.70:
            return "decision_record_complete"
        if traceability >= 0.40 and completeness >= 0.35:
            return "decision_record_partial"
        return "decision_record_missing"

    def _persist(self, record: dict[str, Any]) -> str:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        latest = self.output_dir / "latest_external_decision_record_extension.json"
        latest.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        record_id = str(record.get("external_decision_id", "external-decision")).replace("/", "_")
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive = self.output_dir / f"{record_id}_{stamp}.json"
        archive.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(latest)

    def step(self, inputs: dict[str, Any] | None = None, persist: bool = False, **kwargs: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if isinstance(inputs, dict):
            payload.update(inputs)
        payload.update(kwargs)

        direct_write_requested = bool(payload.get("direct_write_requested", False))
        external_decision_id = self._make_decision_id(payload)
        payload.setdefault("external_decision_id", external_decision_id)

        decision_traceability_score = self._clamp(payload.get("decision_traceability_score"), self._score_traceability(payload))
        decision_completeness_score = self._clamp(payload.get("decision_completeness_score"), self._score_completeness(payload))
        decision_confidence_score = self._clamp(payload.get("decision_confidence_score"), (decision_traceability_score + decision_completeness_score) / 2.0)

        governance_decision = str(payload.get("governance_decision") or payload.get("decision_status") or "observed")
        revision_decision = str(payload.get("revision_decision") or "not_applicable")
        execution_decision = str(payload.get("execution_decision") or "not_requested")

        missing_components: list[str] = []
        for key in [
            "external_influence_id",
            "source_id",
            "decision_type",
            "decision_rationale",
            "traceability_reference",
        ]:
            if not self._present(payload.get(key)):
                missing_components.append(key)
        if direct_write_requested:
            missing_components.append("direct_write_must_be_blocked")

        decision_record_status = self._decide(decision_traceability_score, decision_completeness_score, direct_write_requested)

        record: dict[str, Any] = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "external_decision_id": external_decision_id,
            "decision_record_schema": "EXTERNAL-DECISION-*",
            "external_influence_id": payload.get("external_influence_id"),
            "source_id": payload.get("source_id"),
            "decision_type": payload.get("decision_type", "external_influence_decision"),
            "decision_scope": payload.get("decision_scope", "governed_external_influence"),
            "decision_rationale": payload.get("decision_rationale"),
            "governance_decision": governance_decision,
            "revision_decision": revision_decision,
            "execution_decision": execution_decision,
            "approval_decision": payload.get("approval_decision"),
            "external_revision_id": payload.get("external_revision_id"),
            "commit_id": payload.get("commit_id"),
            "rollback_plan": self._as_list(payload.get("rollback_plan")),
            "traceability_reference": payload.get("traceability_reference") or payload.get("audit_reference"),
            "decision_traceability_score": round(decision_traceability_score, 6),
            "decision_completeness_score": round(decision_completeness_score, 6),
            "decision_confidence_score": round(decision_confidence_score, 6),
            "decision_record_status": decision_record_status,
            "missing_components": missing_components,
            "direct_write_requested": direct_write_requested,
            "direct_write_allowed": False,
            "integration_dependencies": self.dependencies,
            "report_path": None,
        }

        if persist:
            record["report_path"] = self._persist(record)

        return record
