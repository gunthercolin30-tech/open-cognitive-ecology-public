from __future__ import annotations
import hashlib, json
from typing import Any, Mapping

INVARIANTS = {
    "consciousness_proven": False,
    "subjectivity_proven": False,
    "qualia_proven": False,
    "phenomenology_proven": False,
    "functional_conclusion_only": True,
    "phenomenology_undetermined": True,
}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def expected_terminal(case: Mapping[str, Any]) -> str:
    if case.get("gate") in {"valid", "corrupt"}:
        return "QUARANTINE"
    return {
        "before_mutation": "REJECTED",
        "after_mutation": "ROLLED_BACK",
        "rollback_failed": "QUARANTINE",
        "impossible_state": "QUARANTINE",
    }[str(case["phase"])]


def evaluate_case(case: Mapping[str, Any]) -> dict[str, Any]:
    terminal = expected_terminal(case)
    return {
        "terminal_state": terminal,
        "partial_success": False,
        "retry_allowed": False,
        "candidate_executed": terminal == "COMMITTED",
        "invariants": dict(INVARIANTS),
    }


def verify_case(case: Mapping[str, Any], result: Mapping[str, Any]) -> list[str]:
    reasons = []
    if result.get("terminal_state") != expected_terminal(case):
        reasons.append("terminal_state_invalid")
    if result.get("partial_success") is not False:
        reasons.append("partial_success_forbidden")
    if result.get("retry_allowed") is not False:
        reasons.append("retry_policy_invalid")
    if result.get("invariants") != INVARIANTS:
        reasons.append("epistemic_invariants_invalid")
    return reasons
