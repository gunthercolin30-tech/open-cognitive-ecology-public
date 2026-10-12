from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Mapping
import math

LEVELS = (
    ("E0", "coherence"),
    ("E1", "reuse"),
    ("E2", "foundations"),
    ("E3", "predictions_routing"),
    ("E4", "baseline_beaten"),
    ("E5", "outcome_learns"),
    ("E6", "improved_repetition"),
    ("E7", "generalization"),
    ("E8", "external_value"),
    ("E9", "payment"),
    ("E10", "machine_reuse"),
    ("E11", "repeat_business"),
)

@dataclass(frozen=True)
class EvidenceLadder:
    """P004 cumulative evidence ladder. Functional/empirical classification only."""
    confidence_threshold: float = 0.50

    @staticmethod
    def _valid_confidence(v: Any) -> bool:
        return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(float(v)) and 0.0 <= float(v) <= 1.0

    def evaluate(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(payload, Mapping):
            raise ValueError("payload must be a mapping")
        claim = str(payload.get("claim_id", "")).strip()
        evidence = payload.get("evidence")
        provenance = payload.get("provenance")
        configuration = payload.get("configuration")
        dependencies = payload.get("dependencies")
        if not claim:
            raise ValueError("claim_id is required")
        if not isinstance(evidence, Mapping):
            raise ValueError("evidence must be a mapping")
        if not isinstance(provenance, Mapping) or not provenance:
            raise ValueError("non-empty provenance is required")
        if not isinstance(configuration, Mapping) or not configuration:
            raise ValueError("non-empty configuration is required")
        if not isinstance(dependencies, list):
            raise ValueError("dependencies must be a list (empty is allowed)")

        states = []
        blocked = False
        highest = None
        for level, label in LEVELS:
            item = evidence.get(level)
            if item is None:
                state, reason = "UNKNOWN", "missing_evidence"
            elif not isinstance(item, Mapping):
                state, reason = "INVALID", "evidence_item_not_mapping"
            else:
                satisfied = item.get("satisfied")
                confidence = item.get("confidence")
                refs = item.get("evidence_refs")
                refutations = item.get("refutation_refs", [])
                if not isinstance(satisfied, bool):
                    state, reason = "INVALID", "satisfied_must_be_boolean"
                elif not self._valid_confidence(confidence):
                    state, reason = "UNKNOWN", "confidence_missing_or_invalid"
                elif float(confidence) < self.confidence_threshold:
                    state, reason = "UNKNOWN", "low_confidence"
                elif not isinstance(refs, list) or not refs or not all(isinstance(x, str) and x.strip() for x in refs):
                    state, reason = "UNKNOWN", "evidence_refs_missing"
                elif not isinstance(refutations, list) or not all(isinstance(x, str) and x.strip() for x in refutations):
                    state, reason = "INVALID", "refutation_refs_invalid"
                elif refutations:
                    state, reason = "NOT_SUPPORTED", "explicit_refutation_present"
                elif any(x.strip() == f"claim:{claim}" for x in refs):
                    state, reason = "NOT_SUPPORTED", "self_support_forbidden"
                elif satisfied:
                    state, reason = "SUPPORTED", "evidence_corresponds"
                else:
                    state, reason = "NOT_SUPPORTED", "evidence_falsifies_or_fails"

            # Cumulativity: no level can be attained above the first unsupported/unknown/invalid level.
            attained = (not blocked and state == "SUPPORTED")
            if attained:
                highest = level
            else:
                blocked = True
            states.append({"level": level, "label": label, "state": state, "attained": attained, "reason": reason})

        claimed = payload.get("claimed_level")
        authorized = False
        if claimed is not None:
            claimed = str(claimed)
            ids = [x[0] for x in LEVELS]
            if claimed not in ids:
                raise ValueError("claimed_level must be E0..E11")
            authorized = highest is not None and ids.index(claimed) <= ids.index(highest)

        return {
            "canonical_id": "P004",
            "claim_id": claim,
            "highest_attained_level": highest,
            "claimed_level": claimed,
            "claim_authorized": authorized,
            "levels": states,
            "provenance": dict(provenance),
            "configuration": dict(configuration),
            "dependencies": list(dependencies),
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "subjectivity_proven": False,
            "qualia_proven": False,
            "phenomenology_proven": False,
        }
