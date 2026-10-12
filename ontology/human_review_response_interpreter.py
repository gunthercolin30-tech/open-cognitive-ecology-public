from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class HumanReviewResponseInterpreter:
    """Interpret human review responses into governed machine-actionable decisions.

    This primitive does not assume phenomenality. It provides a functional,
    auditable parser for human governance responses in the L8 review loop.
    """

    primitive = "human_review_response_interpreter"
    VALID_STATUSES = {"authorized", "rejected", "deferred", "pending"}

    AUTHORIZED_TERMS = {
        "authorized", "authorize", "autorise", "autorisé", "autorisee",
        "autorisee", "validé", "valide", "approved", "approve", "ok", "oui",
        "go", "accord", "accept", "accepted", "accepté",
    }
    REJECTED_TERMS = {
        "rejected", "reject", "refuse", "refusé", "refuse", "non", "stop",
        "blocked", "bloque", "bloqué", "deny", "denied", "interdit",
    }
    DEFERRED_TERMS = {
        "deferred", "defer", "différé", "differe", "attendre", "plus tard",
        "pending", "pause", "besoin", "clarification", "information", "infos",
        "incertain", "pas sûr", "pas sur", "not sure", "uncertain",
    }

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _normalize(self, value: Any) -> str:
        return str(value or "").strip().lower()

    def _extract_rationale(self, raw_response: str, explicit_rationale: str | None = None) -> str:
        if explicit_rationale:
            return str(explicit_rationale).strip()
        text = str(raw_response or "").strip()
        separators = ["raison:", "rationale:", "because", "car", "parce que", "motif:"]
        lower = text.lower()
        for sep in separators:
            if sep in lower:
                idx = lower.index(sep) + len(sep)
                return text[idx:].strip(" -:;\n\t")
        parts = text.splitlines()
        if len(parts) > 1:
            return " ".join(p.strip() for p in parts[1:] if p.strip())
        tokens = text.split(maxsplit=1)
        if len(tokens) == 2 and tokens[0].lower() in self.AUTHORIZED_TERMS | self.REJECTED_TERMS | self.DEFERRED_TERMS:
            return tokens[1].strip(" -:;\n\t")
        return ""

    def _classify(self, text: str) -> tuple[str, float, list[str]]:
        normalized = self._normalize(text)
        evidence: list[str] = []
        if not normalized:
            return "pending", 0.0, ["empty_response"]

        def contains_any(terms: set[str]) -> list[str]:
            hits = []
            for term in terms:
                if term in normalized:
                    hits.append(term)
            return sorted(hits, key=len, reverse=True)

        auth_hits = contains_any(self.AUTHORIZED_TERMS)
        reject_hits = contains_any(self.REJECTED_TERMS)
        defer_hits = contains_any(self.DEFERRED_TERMS)

        classes = [("authorized", auth_hits), ("rejected", reject_hits), ("deferred", defer_hits)]
        non_empty = [(status, hits) for status, hits in classes if hits]
        if len(non_empty) == 1:
            status, hits = non_empty[0]
            evidence.extend(hits[:3])
            confidence = min(1.0, 0.70 + 0.10 * len(hits))
            return status, confidence, evidence
        if len(non_empty) > 1:
            # Prefer explicit first token when mixed language appears in rationale.
            first = normalized.split()[0].strip(" .,:;!?()[]{}")
            if first in self.AUTHORIZED_TERMS:
                return "authorized", 0.85, [first, "mixed_evidence"]
            if first in self.REJECTED_TERMS:
                return "rejected", 0.85, [first, "mixed_evidence"]
            if first in self.DEFERRED_TERMS:
                return "deferred", 0.85, [first, "mixed_evidence"]
            return "pending", 0.35, ["ambiguous_mixed_evidence"]
        return "pending", 0.25, ["unrecognized_response"]

    def step(self, inputs: dict[str, Any] | None = None) -> dict[str, Any]:
        inputs = dict(inputs or {})
        raw_response = str(inputs.get("human_response", inputs.get("response", "")))
        explicit_rationale = inputs.get("human_review_rationale") or inputs.get("rationale")
        status, confidence, evidence = self._classify(raw_response)
        rationale = self._extract_rationale(raw_response, explicit_rationale)

        rationale_required = bool(inputs.get("rationale_required", True))
        if status in {"authorized", "rejected", "deferred"} and rationale_required and not rationale:
            machine_actionable = False
            clarification_required = True
            clarification_reason = "missing_rationale"
        elif status == "pending":
            machine_actionable = False
            clarification_required = True
            clarification_reason = "unresolved_or_ambiguous_response"
        else:
            machine_actionable = True
            clarification_required = False
            clarification_reason = None

        return {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": self._now(),
            "raw_response": raw_response,
            "human_review_status": status,
            "human_review_rationale": rationale,
            "interpretation_confidence": confidence,
            "interpretation_evidence": evidence,
            "machine_actionable": machine_actionable,
            "clarification_required": clarification_required,
            "clarification_reason": clarification_reason,
            "valid_status": status in self.VALID_STATUSES,
        }
