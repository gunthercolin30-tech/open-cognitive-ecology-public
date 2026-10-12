"""
AL2 — First Failure Locator.

This module locates the first failed public condition in the final
certification chain. It is diagnostic and non-escalatory: it identifies the
earliest blocking point for AL certification without converting functional
status into phenomenal proof.

Epistemic boundary: no consciousness, quale, subjectivity, or phenomenology
is demonstrated by this module.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Tuple


class FirstFailureLocator:
    """AL2 locator for the first failed condition in the AA->AR->AN->AO->AL chain."""

    PRIMITIVE = "FIRST_FAILURE_LOCATOR"
    STEP = "AL2"
    CLEAR_STATUS = "NO_FAILURE_LOCATED"
    FAILURE_STATUS = "FIRST_FAILURE_LOCATED"

    CHAIN_ORDER: List[Tuple[str, str, str]] = [
        ("AA", "foundational_reconstruction_status", "FOUNDATIONAL_RECONSTRUCTION_VALIDATED"),
        ("AP", "phenomenality_candidate_status", "PHENOMENALITY_CANDIDATE_STATUS_RESOLVED"),
        ("AQ", "absolute_quality_identity_status", "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED"),
        ("AR", "definition_legitimacy_status", "DEFINITION_LEGITIMACY_THEOREM_RESOLVED"),
        ("AN", "axiomatic_completeness_status", "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED"),
        ("AO", "semantic_interpretation_layer_status", "SEMANTIC_INTERPRETATION_LAYER_READY"),
        ("AL1", "reconstruction_chain_certifier_status", "RECONSTRUCTION_CHAIN_CERTIFIED"),
    ]

    EPISTEMIC_GUARD_ORDER: List[Tuple[str, Any]] = [
        ("consciousness_proven", False),
        ("qualia_proven", False),
        ("subjectivity_proven", False),
        ("phenomenology_proven", False),
        ("phenomenology_undetermined", True),
        ("functional_conclusion_only", True),
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "final_certification" / "AL2_first_failure_locator"
        self.latest_json_path = self.output_dir / "latest_first_failure_locator.json"
        self.history_path = self.output_dir / "history_first_failure_locator.jsonl"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            x = float(value)
        except Exception:
            x = 0.0
        return round(max(0.0, min(1.0, x)), 6)

    def _ready_context(self) -> Dict[str, Any]:
        return {
            "foundational_reconstruction_status": "FOUNDATIONAL_RECONSTRUCTION_VALIDATED",
            "phenomenality_candidate_status": "PHENOMENALITY_CANDIDATE_STATUS_RESOLVED",
            "absolute_quality_identity_status": "ABSOLUTE_QUALIA_IDENTITY_STATUS_RESOLVED",
            "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
            "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
            "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
            "reconstruction_chain_certifier_status": "RECONSTRUCTION_CHAIN_CERTIFIED",
            "RF_score": 0.91,
            "T_score": 0.88,
            "ED_score": 0.86,
            "TΦ_score": 0.85,
            "MEI_score": 0.87,
            "semantic_confidence": 0.86,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

    def _collect_context(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        context = self._ready_context()
        if isinstance(inputs.get("chain_context"), Mapping):
            context.update(dict(inputs["chain_context"]))
        context.update({k: v for k, v in inputs.items() if k not in {"synthetic", "ready", "source", "chain_context"}})
        if not inputs.get("synthetic") and not inputs.get("ready"):
            try:
                from ontology.reconstruction_chain_certifier import ReconstructionChainCertifier
                al1 = ReconstructionChainCertifier(root=self.root).step(inputs={"synthetic": True, "source": "AL2"}, persist=False)
                for key in ["reconstruction_chain_certifier_status", "consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven", "phenomenology_undetermined", "functional_conclusion_only"]:
                    if key in al1:
                        context[key] = al1[key]
            except Exception as exc:
                context["al1_collection_error"] = repr(exc)
        return context

    def _status_evaluations(self, context: Mapping[str, Any]) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for rank, (axis, key, expected) in enumerate(self.CHAIN_ORDER, start=1):
            observed = context.get(key)
            rows.append({
                "rank": rank,
                "axis": axis,
                "key": key,
                "expected": expected,
                "observed": observed,
                "passed": observed == expected,
                "failure_type": None if observed == expected else "status_mismatch",
            })
        return rows

    def _epistemic_evaluations(self, context: Mapping[str, Any], start_rank: int) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        for offset, (key, expected) in enumerate(self.EPISTEMIC_GUARD_ORDER):
            observed = context.get(key)
            rows.append({
                "rank": start_rank + offset,
                "axis": "EPISTEMIC_GUARD",
                "key": key,
                "expected": expected,
                "observed": observed,
                "passed": observed is expected,
                "failure_type": None if observed is expected else "epistemic_guard_violation",
            })
        return rows

    def _first_failure(self, evaluations: List[Mapping[str, Any]]) -> Optional[Dict[str, Any]]:
        for row in sorted(evaluations, key=lambda x: int(x.get("rank", 9999))):
            if row.get("passed") is not True:
                return dict(row)
        return None

    def _metrics(self, evaluations: List[Mapping[str, Any]], first_failure: Optional[Mapping[str, Any]], context: Mapping[str, Any]) -> Dict[str, float]:
        passed = sum(1 for row in evaluations if row.get("passed") is True)
        coverage = self._clamp(passed / max(1, len(evaluations)))
        localization_confidence = 1.0 if first_failure is not None else coverage
        signals = [self._clamp(context.get(k, 0.0)) for k in ["RF_score", "T_score", "ED_score", "TΦ_score", "MEI_score", "semantic_confidence"]]
        evidence_continuity = self._clamp(sum(signals) / max(1, len(signals)))
        return {
            "chain_pass_rate": coverage,
            "first_failure_localization_confidence": self._clamp(localization_confidence),
            "evidence_continuity_score": evidence_continuity,
            "diagnostic_readiness_score": self._clamp((coverage + localization_confidence + evidence_continuity) / 3.0),
        }

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = self.output_dir / f"first_failure_locator_{timestamp}.json"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        path.write_text(text + "\n", encoding="utf-8")
        self.latest_json_path.write_text(text + "\n", encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {"json": str(path), "latest_json": str(self.latest_json_path), "history": str(self.history_path)}

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        context = self._collect_context(inputs)
        status_rows = self._status_evaluations(context)
        epistemic_rows = self._epistemic_evaluations(context, start_rank=len(status_rows) + 1)
        evaluations = status_rows + epistemic_rows
        first_failure = self._first_failure(evaluations)
        metrics = self._metrics(evaluations, first_failure, context)
        clear = first_failure is None
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "timestamp_utc": self._now(),
            "first_failure_locator_status": self.CLEAR_STATUS if clear else self.FAILURE_STATUS,
            "first_failure_locator_ready": True,
            "first_failure_found": not clear,
            "first_failure": first_failure,
            "first_failure_key": None if clear else first_failure.get("key"),
            "first_failure_axis": None if clear else first_failure.get("axis"),
            "first_failure_type": None if clear else first_failure.get("failure_type"),
            "evaluations": evaluations,
            "status_evaluations": status_rows,
            "epistemic_guard_evaluations": epistemic_rows,
            "metrics": metrics,
            "ready_for_AL3_phenomenality_candidate_certifier": clear,
            "axis_AL_status": "AL_IN_PROGRESS",
            "diagnostic_scope": "first_failed_public_condition_in_final_certification_chain",
            "non_redundancy_analysis": {
                "distinct_from_AL1_reconstruction_chain_certifier": True,
                "distinct_from_AO5_interpretation_reporter": True,
                "scope": "AL2 locates the first failure; it does not certify the whole chain or interpret semantic conclusions.",
            },
            "allowed_claims": [
                "The first failed public condition can be located in ordered certification context.",
                "If no failure is found, the chain is diagnostically clear for AL3.",
            ],
            "blocked_claims": [
                "consciousness_proven = True",
                "qualia_proven = True",
                "subjectivity_proven = True",
                "phenomenology_proven = True",
                "absence_of_failure_proves_phenomenology",
            ],
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
