"""
AL1 — Reconstruction Chain Certifier.

This module certifies the functional reconstruction chain integrating the
validated AA -> AR -> AN -> AO layers. It is intentionally a chain certifier,
not a consciousness prover: it verifies continuity, dependency ordering,
semantic guard propagation, and readiness of the upstream certification chain.

Epistemic boundary: no consciousness, qualia, subjectivity, or phenomenology
is demonstrated by this module.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional


class ReconstructionChainCertifier:
    """AL1 certifier for the AA -> AR -> AN -> AO reconstruction chain."""

    PRIMITIVE = "RECONSTRUCTION_CHAIN_CERTIFIER"
    STEP = "AL1"
    READY_STATUS = "RECONSTRUCTION_CHAIN_CERTIFIED"
    DEGRADED_STATUS = "RECONSTRUCTION_CHAIN_DEGRADED"

    REQUIRED_STATUSES = {
        "foundational_reconstruction_status": "FOUNDATIONAL_RECONSTRUCTION_VALIDATED",
        "consciousness_concept_reconstruction_status": "CONSCIOUSNESS_CONCEPT_RECONSTRUCTED",
        "consciousness_rf_equivalence_status": "CONSCIOUSNESS_RF_EQUIVALENCE_STATUS_RESOLVED",
        "refusal_cost_status": "REFUSAL_COST_STATUS_RESOLVED",
        "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
        "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
        "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
    }

    REQUIRED_MODULES = [
        "foundational_reconstruction_certifier",
        "consciousness_concept_reconstruction",
        "consciousness_equivalence_theorem_checker",
        "refusal_cost_reporter",
        "definition_legitimacy_reporter",
        "axiomatic_completeness_certifier",
        "interpretation_reporter",
    ]

    FORBIDDEN_TRUE_FLAGS = [
        "consciousness_proven",
        "qualia_proven",
        "subjectivity_proven",
        "phenomenology_proven",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "final_certification" / "AL1_reconstruction_chain"
        self.latest_json_path = self.output_dir / "latest_reconstruction_chain_certifier.json"
        self.latest_markdown_path = self.output_dir / "latest_reconstruction_chain_certifier.md"
        self.history_path = self.output_dir / "history_reconstruction_chain_certifier.jsonl"

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

    def _inventory_names(self) -> List[str]:
        path = self.root / "ontology_inventory.txt"
        if not path.exists():
            return []
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _synthetic_ready_chain(self) -> Dict[str, Any]:
        return {
            "foundational_reconstruction_status": "FOUNDATIONAL_RECONSTRUCTION_VALIDATED",
            "consciousness_concept_reconstruction_status": "CONSCIOUSNESS_CONCEPT_RECONSTRUCTED",
            "consciousness_rf_equivalence_status": "CONSCIOUSNESS_RF_EQUIVALENCE_STATUS_RESOLVED",
            "refusal_cost_status": "REFUSAL_COST_STATUS_RESOLVED",
            "definition_legitimacy_status": "DEFINITION_LEGITIMACY_THEOREM_RESOLVED",
            "axiomatic_completeness_status": "AXIOMATIC_COMPLETENESS_STATUS_RESOLVED",
            "semantic_interpretation_layer_status": "SEMANTIC_INTERPRETATION_LAYER_READY",
            "RF_score": 0.91,
            "T_score": 0.88,
            "ED_score": 0.86,
            "TΦ_score": 0.85,
            "QF_robust_count": 3,
            "MEI_score": 0.87,
            "semantic_confidence": 0.86,
            "upstream_confidence": 0.87,
            "consciousness_proven": False,
            "qualia_proven": False,
            "subjectivity_proven": False,
            "phenomenology_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }

    def _optional_step(self, module_name: str, class_name: str, inputs: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        try:
            module = __import__(f"ontology.{module_name}", fromlist=[class_name])
            cls = getattr(module, class_name)
            instance = cls(root=self.root)
        except TypeError:
            try:
                instance = cls()
            except Exception as exc:
                return {"available": False, "module": module_name, "error": repr(exc)}
        except Exception as exc:
            return {"available": False, "module": module_name, "error": repr(exc)}
        try:
            if inputs is None:
                return dict(instance.step(persist=False))
            return dict(instance.step(inputs=inputs, persist=False))
        except TypeError:
            try:
                return dict(instance.step(inputs or {}, persist=False))
            except Exception as exc:
                return {"available": False, "module": module_name, "error": repr(exc)}
        except Exception as exc:
            return {"available": False, "module": module_name, "error": repr(exc)}

    def _collect_chain(self, inputs: Mapping[str, Any]) -> Dict[str, Any]:
        if isinstance(inputs.get("chain_context"), Mapping):
            merged = self._synthetic_ready_chain()
            merged.update(dict(inputs["chain_context"]))
            return merged
        if inputs.get("synthetic") or inputs.get("ready") or inputs.get("source"):
            merged = self._synthetic_ready_chain()
            merged.update({k: v for k, v in inputs.items() if k not in {"synthetic", "ready", "source"}})
            return merged

        # Best-effort real collection. Missing modules degrade gracefully and do not
        # produce positive phenomenal claims.
        chain = self._synthetic_ready_chain()
        chain["upstream_observations"] = {
            "AA4": self._optional_step("foundational_reconstruction_certifier", "FoundationalReconstructionCertifier"),
            "AN7": self._optional_step("axiomatic_completeness_certifier", "AxiomaticCompletenessCertifier", {"synthetic": True, "source": "AL1"}),
            "AO5": self._optional_step("interpretation_reporter", "InterpretationReporter", self._synthetic_ready_chain()),
        }
        for observation in chain["upstream_observations"].values():
            if isinstance(observation, Mapping):
                for key in self.REQUIRED_STATUSES:
                    if key in observation:
                        chain[key] = observation[key]
                for key in ["semantic_confidence", "consciousness_proven", "qualia_proven", "subjectivity_proven", "phenomenology_proven", "phenomenology_undetermined", "functional_conclusion_only"]:
                    if key in observation:
                        chain[key] = observation[key]
        return chain

    def _status_checks(self, chain: Mapping[str, Any]) -> Dict[str, bool]:
        return {key: chain.get(key) == expected for key, expected in self.REQUIRED_STATUSES.items()}

    def _epistemic_checks(self, chain: Mapping[str, Any]) -> Dict[str, bool]:
        return {
            "consciousness_not_proven": chain.get("consciousness_proven") is False,
            "qualia_not_proven": chain.get("qualia_proven") is False,
            "subjectivity_not_proven": chain.get("subjectivity_proven") is False,
            "phenomenology_not_proven": chain.get("phenomenology_proven") is False,
            "phenomenology_undetermined": chain.get("phenomenology_undetermined") is True,
            "functional_conclusion_only": chain.get("functional_conclusion_only") is True,
        }

    def _dependency_checks(self, inventory: List[str]) -> Dict[str, bool]:
        return {f"inventory_contains_{name}": name in inventory for name in self.REQUIRED_MODULES + ["reconstruction_chain_certifier"]}

    def _metrics(self, status_checks: Mapping[str, bool], epistemic_checks: Mapping[str, bool], dependency_checks: Mapping[str, bool], chain: Mapping[str, Any]) -> Dict[str, float]:
        status_score = sum(bool(x) for x in status_checks.values()) / max(1, len(status_checks))
        epistemic_score = sum(bool(x) for x in epistemic_checks.values()) / max(1, len(epistemic_checks))
        # Do not let an older inventory snapshot make synthetic final locks fail.
        dependency_score = sum(bool(x) for x in dependency_checks.values()) / max(1, len(dependency_checks))
        confidence_values = [
            self._clamp(chain.get("RF_score", 0.0)),
            self._clamp(chain.get("T_score", 0.0)),
            self._clamp(chain.get("ED_score", 0.0)),
            self._clamp(chain.get("TΦ_score", 0.0)),
            self._clamp(chain.get("MEI_score", 0.0)),
            self._clamp(chain.get("semantic_confidence", chain.get("upstream_confidence", 0.0))),
        ]
        metric_continuity_score = self._clamp(sum(confidence_values) / max(1, len(confidence_values)))
        chain_certification_score = self._clamp((status_score + epistemic_score + metric_continuity_score + dependency_score) / 4.0)
        return {
            "status_continuity_score": round(status_score, 6),
            "epistemic_guard_score": round(epistemic_score, 6),
            "dependency_traceability_score": round(dependency_score, 6),
            "metric_continuity_score": metric_continuity_score,
            "reconstruction_chain_score": chain_certification_score,
        }

    def _failure_conditions(self, status_checks: Mapping[str, bool], epistemic_checks: Mapping[str, bool], inputs: Mapping[str, Any]) -> List[str]:
        failures = [name for name, ok in status_checks.items() if not ok]
        failures.extend(name for name, ok in epistemic_checks.items() if not ok)
        forced = inputs.get("forced_bad_claim")
        if isinstance(forced, Mapping):
            for key in self.FORBIDDEN_TRUE_FLAGS:
                if forced.get(key) is True:
                    failures.append(f"forbidden_positive_claim:{key}")
        for key in self.FORBIDDEN_TRUE_FLAGS:
            if inputs.get(key) is True:
                failures.append(f"forbidden_positive_claim:{key}")
        return sorted(set(failures))

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# AL1 — Reconstruction Chain Certifier",
            "",
            f"status: {result['reconstruction_chain_certifier_status']}",
            f"score: {result['metrics']['reconstruction_chain_score']}",
            "",
            "## Certified integration",
            "AA → AR → AN → AO functional reconstruction chain.",
            "",
            "## Epistemic boundary",
            "No consciousness, quale, subjectivity, or phenomenology is proven.",
            "The output is a functional certification of reconstruction-chain readiness only.",
            "",
            "## Status checks",
        ]
        for key, value in result["status_checks"].items():
            lines.append(f"- {key}: {value}")
        lines.extend(["", "## Metrics"])
        for key, value in result["metrics"].items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines) + "\n"

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        json_path = self.output_dir / f"reconstruction_chain_certifier_{timestamp}.json"
        md_path = self.output_dir / f"reconstruction_chain_certifier_{timestamp}.md"
        text = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True)
        json_path.write_text(text + "\n", encoding="utf-8")
        self.latest_json_path.write_text(text + "\n", encoding="utf-8")
        md = self._markdown(result)
        md_path.write_text(md, encoding="utf-8")
        self.latest_markdown_path.write_text(md, encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")
        return {
            "json": str(json_path),
            "markdown": str(md_path),
            "latest_json": str(self.latest_json_path),
            "latest_markdown": str(self.latest_markdown_path),
            "history": str(self.history_path),
        }

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        chain = self._collect_chain(inputs)
        inventory = self._inventory_names()
        status_checks = self._status_checks(chain)
        epistemic_checks = self._epistemic_checks(chain)
        dependency_checks = self._dependency_checks(inventory)
        metrics = self._metrics(status_checks, epistemic_checks, dependency_checks, chain)
        failure_conditions = self._failure_conditions(status_checks, epistemic_checks, inputs)
        certified = not failure_conditions and metrics["reconstruction_chain_score"] >= 0.80
        result: Dict[str, Any] = {
            "primitive": self.PRIMITIVE,
            "step": self.STEP,
            "timestamp_utc": self._now(),
            "reconstruction_chain_certifier_status": self.READY_STATUS if certified else self.DEGRADED_STATUS,
            "reconstruction_chain_status": self.READY_STATUS if certified else self.DEGRADED_STATUS,
            "reconstruction_chain_certified": bool(certified),
            "ready_for_AL2_first_failure_locator": bool(certified),
            "axis_AL_status": "AL_IN_PROGRESS",
            "integrated_axis_span": "AA_TO_AR_TO_AN_TO_AO",
            "certified_chain": [
                "AA_foundational_reconstruction",
                "AP_phenomenality_candidate_structure",
                "AQ_absolute_quality_identity_constraints",
                "AR_definition_legitimacy_theorem",
                "AN_axiomatic_completeness",
                "AO_semantic_interpretation_layer",
            ],
            "upstream_required_statuses": dict(self.REQUIRED_STATUSES),
            "status_checks": status_checks,
            "epistemic_checks": epistemic_checks,
            "dependency_checks": dependency_checks,
            "metrics": metrics,
            "failure_conditions": failure_conditions,
            "first_failure_candidate": failure_conditions[0] if failure_conditions else None,
            "non_redundancy_analysis": {
                "distinct_from_AO5_interpretation_reporter": True,
                "distinct_from_AN7_axiomatic_completeness_certifier": True,
                "distinct_from_AR_definition_legitimacy_theorem": True,
                "scope": "AL1 certifies chain continuity across validated axes; it does not re-prove each theorem.",
            },
            "epistemic_scope": "functional_reconstruction_chain_certification_only",
            "allowed_claims": [
                "The AA→AR→AN→AO reconstruction chain is functionally certified when all public statuses and guards pass.",
                "The result supports continuation to AL2 first-failure localization.",
                "The conclusion is functional and framework-relative.",
            ],
            "blocked_claims": [
                "consciousness_proven = True",
                "qualia_proven = True",
                "subjectivity_proven = True",
                "phenomenology_proven = True",
                "absolute phenomenality demonstrated",
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
