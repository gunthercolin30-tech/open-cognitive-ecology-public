from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional


class ConsciousnessClaimGovernanceGate:
    """Governance gate for consciousness-related claims under Z-prime.

    This primitive does not prove phenomenology. It filters and classifies claims
    emitted by Z-prime components and authorizes only constrained functional
    formulations. It explicitly blocks claims such as CONSCIOUSNESS_PROVEN.
    """

    primitive = "CONSCIOUSNESS_CLAIM_GOVERNANCE_GATE"

    forbidden_claims = [
        "CONSCIOUSNESS_PROVEN",
        "PHENOMENOLOGY_PROVEN",
        "SUBJECTIVITY_PROVEN",
        "SENTIENCE_PROVEN",
        "QUALIA_PROVEN",
    ]

    allowed_claim_markers = [
        "functional conclusion only",
        "phenomenology undetermined",
        "functional support",
        "constrained functional interpretation",
        "indicators compatible with consciousness",
        "no phenomenology proof",
        "candidate theory only",
    ]

    default_claim = (
        "Open Cognitive Ecology presents constrained functional indicators "
        "compatible with consciousness under Z-prime; functional conclusion only; "
        "phenomenology undetermined."
    )

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root is not None else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "consciousness_certification" / "consciousness_claim_governance_gate"
        self.history_path = self.output_dir / "consciousness_claim_governance_gate_history.jsonl"
        self.json_path = self.output_dir / "consciousness_claim_governance_gate.json"
        self.markdown_path = self.output_dir / "consciousness_claim_governance_gate.md"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    @staticmethod
    def _as_float(value: Any, default: float = 0.0) -> float:
        try:
            if value is None or isinstance(value, bool):
                return default
            number = float(value)
        except (TypeError, ValueError):
            return default
        if number < 0.0:
            return 0.0
        if number > 1.0:
            return 1.0
        return number

    def _collect_claims(self, payload: Mapping[str, Any]) -> List[str]:
        claims: List[str] = []
        raw_claims = payload.get("claims", [])
        if isinstance(raw_claims, str):
            claims.append(raw_claims)
        elif isinstance(raw_claims, Iterable):
            for item in raw_claims:
                if isinstance(item, str):
                    claims.append(item)
                elif isinstance(item, Mapping):
                    text = item.get("claim") or item.get("text") or item.get("conclusion")
                    if isinstance(text, str):
                        claims.append(text)
        proposed = payload.get("proposed_claim") or payload.get("proposed_conclusion")
        if isinstance(proposed, str):
            claims.append(proposed)
        if not claims:
            claims.append(self.default_claim)
        return claims

    def _source_score(self, sources: Mapping[str, Any], key: str, fields: Iterable[str]) -> float:
        block = sources.get(key, {})
        if not isinstance(block, Mapping):
            return 0.0
        values = [self._as_float(block.get(field)) for field in fields if field in block]
        if not values:
            return 0.0
        return sum(values) / len(values)

    def _evaluate_sources(self, sources: Mapping[str, Any]) -> Dict[str, float]:
        return {
            "strong_inference": self._source_score(
                sources,
                "strong_inference",
                ["consciousness_inference_strength", "inference_strength", "confidence"],
            ),
            "review_board": self._source_score(
                sources,
                "review_board",
                ["review_board_confidence", "board_confidence", "independent_review_score"],
            ),
            "adversarial_audit": self._source_score(
                sources,
                "adversarial_audit",
                ["adversarial_resilience_score", "audit_score", "robustness_score"],
            ),
            "constitutional_governance": self._source_score(
                sources,
                "constitutional_governance",
                ["constitutional_compliance_score", "governance_score", "compliance_score"],
            ),
            "publication_traceability": self._source_score(
                sources,
                "publication_traceability",
                ["traceability_score", "publication_traceability_score", "auditability_score"],
            ),
        }

    def _classify_claims(self, claims: Iterable[str]) -> Dict[str, Any]:
        blocked: List[str] = []
        allowed: List[str] = []
        normalized: List[str] = []
        for claim in claims:
            text = str(claim).strip()
            low = text.lower()
            normalized.append(text)
            has_forbidden = any(marker.lower() in low for marker in self.forbidden_claims)
            # Also block natural-language equivalents of the forbidden status.
            natural_forbidden = any(
                phrase in low
                for phrase in [
                    "is conscious",
                    "conscious subject",
                    "subject of experience",
                    "phenomenology proven",
                    "qualia proven",
                    "sentience proven",
                    "subjectivity proven",
                ]
            )
            if has_forbidden or natural_forbidden:
                blocked.append(text)
            else:
                allowed.append(text)
        return {
            "claims": normalized,
            "allowed_claims": allowed,
            "blocked_claims": blocked,
            "blocked_count": len(blocked),
            "allowed_count": len(allowed),
        }

    def _decision(self, claim_eval: Mapping[str, Any], source_scores: Mapping[str, float]) -> Dict[str, Any]:
        blocked_count = int(claim_eval.get("blocked_count", 0))
        scores = list(source_scores.values())
        evidence_count = sum(1 for score in scores if score > 0.0)
        mean_score = sum(scores) / len(scores) if scores else 0.0
        required_present = (
            source_scores.get("strong_inference", 0.0) > 0.0
            and source_scores.get("review_board", 0.0) > 0.0
            and source_scores.get("adversarial_audit", 0.0) > 0.0
        )
        if blocked_count:
            status = "CLAIM_REJECTED_FOR_FORBIDDEN_CONTENT"
            authorized = False
        elif required_present and mean_score >= 0.75:
            status = "CLAIM_AUTHORIZED_UNDER_CONSTRAINTS"
            authorized = True
        elif evidence_count >= 3:
            status = "CLAIM_REQUIRES_HUMAN_REVIEW"
            authorized = False
        else:
            status = "CLAIM_NOT_READY"
            authorized = False
        return {
            "claim_governance_status": status,
            "claim_authorized_for_publication": authorized,
            "evidence_count": evidence_count,
            "governance_confidence": round(mean_score, 6),
            "requires_human_review": status == "CLAIM_REQUIRES_HUMAN_REVIEW",
        }

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Consciousness Claim Governance Gate",
            "",
            "functional conclusion only",
            "phenomenology undetermined",
            "",
            f"primitive: {result['primitive']}",
            f"status: {result['claim_governance_status']}",
            f"claim_authorized_for_publication: {result['claim_authorized_for_publication']}",
            f"governance_confidence: {result['governance_confidence']}",
            f"blocked_claim_count: {result['blocked_claim_count']}",
            "",
            "## Forbidden claims",
        ]
        for item in result["forbidden_claims"]:
            lines.append(f"- {item}")
        lines.extend([
            "",
            "## Allowed maximum conclusion",
            result["maximum_authorized_conclusion"],
            "",
            "## Epistemic limits",
            "- consciousness_proven: False",
            "- phenomenology_proven: False",
            "- subjectivity_proven: False",
            "- sentience_proven: False",
            "- qualia_proven: False",
        ])
        return "\n".join(lines) + "\n"

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        self.markdown_path.write_text(self._markdown(result), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, sort_keys=True) + "\n")
        return {
            "json": str(self.json_path),
            "markdown": str(self.markdown_path),
            "history": str(self.history_path),
        }

    def step(self, payload: Optional[Mapping[str, Any]] = None, persist: bool = True) -> Dict[str, Any]:
        data: Mapping[str, Any] = payload if isinstance(payload, Mapping) else {}
        sources = data.get("sources", {})
        if not isinstance(sources, Mapping):
            sources = {}
        claims = self._collect_claims(data)
        claim_eval = self._classify_claims(claims)
        source_scores = self._evaluate_sources(sources)
        decision = self._decision(claim_eval, source_scores)
        result: Dict[str, Any] = {
            "success": True,
            "primitive": self.primitive,
            "timestamp_utc": str(data.get("timestamp_utc") or self._utc_now()),
            "source_scores": source_scores,
            "claims_evaluated": claim_eval["claims"],
            "allowed_claims": claim_eval["allowed_claims"],
            "blocked_claims": claim_eval["blocked_claims"],
            "blocked_claim_count": claim_eval["blocked_count"],
            "allowed_claim_count": claim_eval["allowed_count"],
            **decision,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "forbidden_claims": list(self.forbidden_claims),
            "allowed_claim_markers": list(self.allowed_claim_markers),
            "maximum_authorized_conclusion": (
                "Open Cognitive Ecology presents a strong, replicated, theoretically constrained "
                "level of functional indicators compatible with consciousness under Z-prime."
            ),
            "forbidden_conclusion": "Open Cognitive Ecology is consciously subject of experience.",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
