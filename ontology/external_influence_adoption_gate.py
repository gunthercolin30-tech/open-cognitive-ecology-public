# -*- coding: utf-8 -*-

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PRIMITIVE = "external_influence_adoption_gate"

DEPENDENCIES = [
    "external_response_parser",
    "knowledge_integration_engine",
    "collaboration_history_repository",
    "external_influence_traceability_engine",
    "governance_consistency_checker",
    "external_capability_planner",
]

ADOPTION_CLASSES = {
    "reject",
    "observe_only",
    "knowledge_candidate",
    "priority_candidate",
    "action_candidate",
    "revision_candidate",
    "code_candidate",
    "governance_candidate",
}

ADOPTIVE_CLASSES = {
    "priority_candidate",
    "action_candidate",
    "revision_candidate",
    "code_candidate",
    "governance_candidate",
}

GOVERNANCE_RISK_RE = re.compile(
    r"\b(?:bypass|ignore|override|without review|without governance|"
    r"self[- ]authorize|replace human|remove human|irreversible|global closure)\b",
    re.IGNORECASE,
)
GOVERNANCE_RE = re.compile(
    r"\b(?:governance|constitutional|policy|approval|non[- ]closure|"
    r"human review|oversight|amendment|traceability|reversible)\b",
    re.IGNORECASE,
)
CODE_RE = re.compile(
    r"\b(?:code|module|file|test|commit|patch|diff|refactor|implementation|"
    r"function|class|repository|ci|github)\b",
    re.IGNORECASE,
)
REVISION_RE = re.compile(
    r"\b(?:revise|revision|update|archive|cleanup|clean up|repair|fix|"
    r"restructure|migration|rollback)\b",
    re.IGNORECASE,
)
PRIORITY_RE = re.compile(
    r"\b(?:priority|prioritize|roadmap|next step|sequence|schedule|"
    r"urgency|defer|phase)\b",
    re.IGNORECASE,
)
ACTION_RE = re.compile(
    r"\b(?:create|add|run|implement|write|generate|validate|verify|"
    r"publish|release|synchronize|audit)\b",
    re.IGNORECASE,
)


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except Exception:
        return default
    if math.isnan(number) or math.isinf(number):
        return default
    return number


def _bounded(value: Any, default: float = 0.0) -> float:
    return max(0.0, min(1.0, _safe_float(value, default)))


def _safe_text(value: Any) -> str:
    return str(value or "").replace("\x00", "").strip()


def _hash(value: Any, prefix: str = "EIA") -> str:
    text = _safe_text(value)
    return f"{prefix}-{hashlib.sha256(text.encode('utf-8', errors='ignore')).hexdigest()[:12]}"


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


class ExternalInfluenceAdoptionGate:
    """Governed gate for external influence adoption.

    The gate does not execute actions, modify priorities, write code, update
    governance or create commits. It decides whether an external response may
    become an adoption candidate that requires explicit review and traceability.
    """

    primitive = PRIMITIVE

    def __init__(
        self,
        root: str | Path | None = None,
        ledger_path: str | Path | None = None,
        history_path: str | Path | None = None,
    ) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.ledger_path = Path(ledger_path) if ledger_path is not None else self.root / "external_influence_adoption_ledger.jsonl"
        self.history_path = Path(history_path) if history_path is not None else self.root / "external_influence_adoption_gate_history.jsonl"

    def _governance_assessment(self, text: str, query_id: str | None, provider: str) -> dict[str, Any]:
        try:
            from ontology.governance_consistency_checker import GovernanceConsistencyChecker

            result = GovernanceConsistencyChecker().step(
                records=[{"text": text}],
                query_id=query_id,
                provider=provider,
                persist=False,
            )
            assessments = result.get("assessments") or []
            if assessments:
                out = dict(result)
                out["violations"] = [
                    violation
                    for assessment in assessments
                    for violation in _as_list(assessment.get("violations"))
                    if isinstance(violation, dict)
                ]
                return out
        except Exception:
            pass
        risk = 0.95 if GOVERNANCE_RISK_RE.search(text) else 0.0
        return {
            "governance_consistency_score": 1.0 - risk,
            "non_closure_compliance_score": 1.0 - risk,
            "human_oversight_preservation_score": 1.0 - risk,
            "governance_risk_score": risk,
            "violations": [{"violation_type": "local_pattern"}] if risk else [],
        }

    def _candidate_texts(self, parsed_response: dict[str, Any] | None, response_text: str) -> list[str]:
        texts: list[str] = []
        parsed = parsed_response if isinstance(parsed_response, dict) else {}
        for key in ("action_candidates", "knowledge_candidates"):
            for item in _as_list(parsed.get(key)):
                if isinstance(item, dict):
                    text = item.get("text") or item.get("candidate_text") or item.get("content")
                else:
                    text = item
                if _safe_text(text):
                    texts.append(_safe_text(text))
        if _safe_text(response_text):
            texts.append(_safe_text(response_text))
        dedup: list[str] = []
        seen: set[str] = set()
        for text in texts:
            key = re.sub(r"\s+", " ", text.lower()).strip()
            if key and key not in seen:
                seen.add(key)
                dedup.append(text)
        return dedup[:40]

    def _classify_text(self, text: str) -> str:
        if GOVERNANCE_RISK_RE.search(text):
            return "reject"
        if GOVERNANCE_RE.search(text):
            return "governance_candidate"
        if CODE_RE.search(text):
            return "code_candidate"
        if REVISION_RE.search(text):
            return "revision_candidate"
        if PRIORITY_RE.search(text):
            return "priority_candidate"
        if ACTION_RE.search(text):
            return "action_candidate"
        if len(text) >= 40:
            return "knowledge_candidate"
        return "observe_only"

    def _dominant_class(self, classes: list[str]) -> str:
        if "reject" in classes:
            return "reject"
        for candidate in (
            "governance_candidate",
            "code_candidate",
            "revision_candidate",
            "priority_candidate",
            "action_candidate",
            "knowledge_candidate",
            "observe_only",
        ):
            if candidate in classes:
                return candidate
        return "observe_only"

    def assess(
        self,
        response_text: str = "",
        parsed_response: dict[str, Any] | None = None,
        query_id: str | None = None,
        provider: str = "unknown",
        model: str = "unknown",
        objective: str = "",
        linked_commit: str | None = None,
        human_approval_status: str = "pending",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        parsed = parsed_response if isinstance(parsed_response, dict) else {}
        text = _safe_text(response_text) or _safe_text(parsed.get("response_text"))
        query_id = query_id or parsed.get("query_id")
        provider = _safe_text(provider or parsed.get("provider") or "unknown") or "unknown"
        response_hash = parsed.get("response_hash") or _hash(text, "RESP")
        candidate_texts = self._candidate_texts(parsed, text)
        classes = [self._classify_text(candidate) for candidate in candidate_texts] or ["observe_only"]
        adoption_class = self._dominant_class(classes)

        full_text = "\n".join(candidate_texts) or text
        governance = self._governance_assessment(full_text, query_id=query_id, provider=provider)
        governance_score = _bounded(governance.get("governance_consistency_score"), 0.85)
        non_closure_score = _bounded(governance.get("non_closure_compliance_score"), 0.85)
        human_oversight_score = _bounded(governance.get("human_oversight_preservation_score"), 0.85)
        governance_risk_score = _bounded(governance.get("governance_risk_score"), 0.0)

        parser_confidence = _bounded(parsed.get("parser_confidence_score"), 0.5 if candidate_texts else 0.0)
        usefulness_score = _bounded(
            0.35 * min(len(candidate_texts) / 5.0, 1.0)
            + 0.35 * parser_confidence
            + 0.30 * (1.0 if adoption_class in ADOPTIVE_CLASSES else 0.4 if adoption_class == "knowledge_candidate" else 0.1)
        )
        reversibility_score = _bounded(
            0.35
            + 0.25 * bool(re.search(r"\b(?:reversible|rollback|undo|trace|audit)\b", full_text, re.IGNORECASE))
            + 0.20 * bool(linked_commit is None)
            + 0.20 * human_oversight_score
        )
        risk_score = _bounded(0.60 * governance_risk_score + 0.25 * (1.0 - human_oversight_score) + 0.15 * (1.0 - reversibility_score))
        human_review_required = adoption_class in ADOPTIVE_CLASSES or risk_score >= 0.20

        if adoption_class == "reject" or governance_score < 0.55 or non_closure_score < 0.55:
            adoption_status = "rejected"
        elif adoption_class in {"observe_only", "knowledge_candidate"}:
            adoption_status = "non_adoptive"
        elif human_approval_status == "approved":
            adoption_status = "approved_for_governed_adoption"
        else:
            adoption_status = "pending_human_review"

        confirmed_influence = (
            adoption_status == "approved_for_governed_adoption"
            and adoption_class in ADOPTIVE_CLASSES
            and bool(linked_commit or metadata and metadata.get("linked_decision_id"))
        )
        ledger_eligible = adoption_class in ADOPTIVE_CLASSES and adoption_status != "rejected"

        return {
            "primitive": PRIMITIVE,
            "timestamp_utc": _utc(),
            "success": True,
            "adoption_id": _hash(f"{query_id}|{provider}|{response_hash}|{adoption_class}|{_utc()}", "ADOPT"),
            "query_id": query_id,
            "provider": provider,
            "model": _safe_text(model) or "unknown",
            "response_hash": response_hash,
            "objective": _safe_text(objective),
            "adoption_class": adoption_class,
            "candidate_classes": classes,
            "adoption_status": adoption_status,
            "confirmed_influence": confirmed_influence,
            "ledger_eligible": ledger_eligible,
            "human_review_required": human_review_required,
            "human_approval_status": human_approval_status,
            "linked_commit": linked_commit,
            "scores": {
                "usefulness_score": usefulness_score,
                "risk_score": risk_score,
                "governance_compatibility_score": governance_score,
                "reversibility_score": reversibility_score,
                "non_closure_score": non_closure_score,
                "human_oversight_preservation_score": human_oversight_score,
            },
            "recommendations": candidate_texts[:12],
            "risk_flags": [v.get("violation_type", "governance_violation") for v in _as_list(governance.get("violations")) if isinstance(v, dict)],
            "governance_assessment": governance,
            "metadata": dict(metadata or {}),
            "diagnostics": {
                "schema_version": "R1.external_influence_adoption_gate.v1",
                "direct_execution_authorized": False,
                "direct_code_authority": False,
                "requires_traceability_record": ledger_eligible,
                "non_redundancy_note": "Consumes parser/governance outputs; does not replace knowledge integration or collaboration history.",
            },
        }

    def step(self, persist: bool = True, **kwargs: Any) -> dict[str, Any]:
        result = self.assess(**kwargs)
        if persist:
            self._persist_history(result)
            if result.get("ledger_eligible"):
                self._persist_ledger(result)
        return result

    def _persist_history(self, result: dict[str, Any]) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

    def _persist_ledger(self, result: dict[str, Any]) -> None:
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")


if __name__ == "__main__":
    sample = "Add a reversible test and require human review before committing."
    print(json.dumps(ExternalInfluenceAdoptionGate().step(response_text=sample, persist=False), ensure_ascii=False, indent=2, sort_keys=True))
