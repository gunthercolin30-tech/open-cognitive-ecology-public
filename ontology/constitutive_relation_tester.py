from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional


class ConstitutiveRelationTester:
    """Z''6 — Constitutive relation tester under explicit epistemic constraints.

    This primitive distinguishes correlation, causality, constitution and
    indeterminacy for each registered candidate property P. It is deliberately
    conservative: it can classify a property as a constitutive candidate under
    constraints, but it never proves consciousness, phenomenology, subjectivity,
    sentience or qualia.

    Formal distinction:
        correlation != causality != constitution

    The tester integrates Z''1-Z''5 outputs:
      - candidate property registry;
      - necessity support and necessity defeat pressure;
      - sufficiency support and zombie/countermodel pressure;
      - absence-property counterexamples;
      - causal/intervention indicators when available.
    """

    primitive = "CONSTITUTIVE_RELATION_TESTER"

    forbidden_claims = [
        "CONSCIOUSNESS_PROVEN",
        "PHENOMENOLOGY_PROVEN",
        "SUBJECTIVITY_PROVEN",
        "SENTIENCE_PROVEN",
        "QUALIA_PROVEN",
        "ABSOLUTE_PROOF_ACHIEVED",
    ]

    relation_statuses = [
        "correlation_only",
        "causal_relation",
        "constitutive_candidate_under_constraints",
        "indeterminate",
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = Path(root) if root else Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "consciousness_certification" / "constitutive_relation_tester"
        self.json_path = self.output_dir / "constitutive_relation_tester.json"
        self.markdown_path = self.output_dir / "constitutive_relation_tester.md"
        self.history_path = self.output_dir / "constitutive_relation_tester_history.jsonl"

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    @staticmethod
    def _clamp(value: Any) -> float:
        try:
            x = float(value)
        except Exception:
            x = 0.0
        return round(max(0.0, min(1.0, x)), 6)

    @staticmethod
    def _as_mapping(value: Any) -> Dict[str, Any]:
        return dict(value) if isinstance(value, Mapping) else {}

    @staticmethod
    def _index_by_property(results: Any) -> Dict[str, Mapping[str, Any]]:
        indexed: Dict[str, Mapping[str, Any]] = {}
        if isinstance(results, Mapping):
            results = results.get("candidate_results", [])
        if not isinstance(results, list):
            return indexed
        for item in results:
            if not isinstance(item, Mapping):
                continue
            pid = str(item.get("property_id") or "").strip()
            if pid:
                indexed[pid] = item
        return indexed

    def _safe_call(self, module_name: str, class_name: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        try:
            module = __import__("ontology." + module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            instance = cls(root=self.root)
            if payload is None:
                return self._as_mapping(instance.step(persist=False))
            return self._as_mapping(instance.step(payload, persist=False))
        except Exception as exc:  # pragma: no cover - defensive diagnostic path
            return {"available": False, "source": module_name, "error": repr(exc), "candidate_results": []}

    def _load_inputs(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        registry = self._as_mapping(payload.get("registry")) or self._safe_call(
            "consciousness_property_candidate_registry", "ConsciousnessPropertyCandidateRegistry"
        )
        necessity = self._as_mapping(payload.get("necessity")) or self._safe_call(
            "necessity_test_engine", "NecessityTestEngine"
        )
        sufficiency = self._as_mapping(payload.get("sufficiency")) or self._safe_call(
            "sufficiency_test_engine", "SufficiencyTestEngine"
        )
        zombie = self._as_mapping(payload.get("zombie")) or self._safe_call(
            "zombie_counterexample_generator", "ZombieCounterexampleGenerator"
        )
        absent = self._as_mapping(payload.get("absent_property")) or self._safe_call(
            "absent_property_counterexample_generator", "AbsentPropertyCounterexampleGenerator"
        )
        return {
            "registry": registry,
            "necessity": necessity,
            "sufficiency": sufficiency,
            "zombie": zombie,
            "absent_property": absent,
        }

    def _causal_signal_from_candidate(self, candidate: Mapping[str, Any], payload: Mapping[str, Any]) -> float:
        label = str(candidate.get("label") or "").lower()
        linked = " ".join(str(x).lower() for x in candidate.get("linked_modules", []) if isinstance(x, str))
        explicit = payload.get("causal_scores", {})
        if isinstance(explicit, Mapping):
            pid = str(candidate.get("property_id") or "")
            if pid in explicit:
                return self._clamp(explicit[pid])
            if label in explicit:
                return self._clamp(explicit[label])
        score = 0.0
        if "causal" in label or "causal" in linked:
            score += 0.35
        if "intervention" in linked or "intervention" in label:
            score += 0.25
        if "irreducib" in label or "irreducib" in linked:
            score += 0.25
        if "global" in linked or "binding" in linked or "temporal" in linked:
            score += 0.1
        return self._clamp(score)

    def _counterexample_pressure(self, pid: str, zombie: Mapping[str, Any], absent: Mapping[str, Any]) -> float:
        z = self._index_by_property(zombie).get(pid, {})
        a = self._index_by_property(absent).get(pid, {})
        zp = self._clamp(z.get("zombie_counterexample_pressure", z.get("counterexample_pressure", 0.0)))
        ap = self._clamp(a.get("absent_property_counterexample_pressure", a.get("counterexample_pressure", 0.0)))
        defeated = 0.0
        if z.get("sufficiency_defeated") is True:
            defeated += 0.35
        if a.get("necessity_defeated") is True:
            defeated += 0.35
        return self._clamp(max(zp, ap, defeated))

    def _necessity_support(self, pid: str, necessity: Mapping[str, Any], absent: Mapping[str, Any]) -> float:
        n = self._index_by_property(necessity).get(pid, {})
        a = self._index_by_property(absent).get(pid, {})
        raw = max(
            self._clamp(n.get("necessity_support", 0.0)),
            self._clamp(n.get("necessity_score", 0.0)),
            self._clamp(n.get("necessity_status_score", 0.0)),
        )
        if n.get("necessity_defeated") is True or a.get("necessity_defeated") is True:
            raw *= 0.35
        if raw == 0.0 and "necessary" in str(n.get("necessity_status", "")).lower():
            raw = 0.55
        return self._clamp(raw)

    def _sufficiency_support(self, pid: str, sufficiency: Mapping[str, Any], zombie: Mapping[str, Any]) -> float:
        s = self._index_by_property(sufficiency).get(pid, {})
        z = self._index_by_property(zombie).get(pid, {})
        raw = max(
            self._clamp(s.get("sufficiency_support", 0.0)),
            self._clamp(s.get("sufficiency_score", 0.0)),
            self._clamp(s.get("sufficiency_status_score", 0.0)),
        )
        if s.get("sufficiency_defeated") is True or z.get("sufficiency_defeated") is True:
            raw *= 0.25
        if raw == 0.0 and "sufficient" in str(s.get("sufficiency_status", "")).lower():
            raw = 0.55
        return self._clamp(raw)

    def _role_signal(self, candidate: Mapping[str, Any]) -> float:
        role = str(candidate.get("proof_role") or "").lower()
        if "constitutive" in role:
            return 0.75
        if "necessity" in role and "sufficiency" in role:
            return 0.5
        if "necessity" in role or "sufficiency" in role:
            return 0.3
        if "insufficient" in role or "zombie" in role:
            return 0.1
        return 0.2

    def _classify(self, necessity_support: float, sufficiency_support: float, causal_strength: float,
                  counterexample_pressure: float, role_signal: float) -> Dict[str, Any]:
        constitutive_strength = self._clamp(
            0.30 * necessity_support
            + 0.20 * sufficiency_support
            + 0.30 * causal_strength
            + 0.20 * role_signal
            - 0.45 * counterexample_pressure
        )
        correlation_strength = self._clamp(max(necessity_support, sufficiency_support) * 0.55 + role_signal * 0.20)
        causal_relation_strength = self._clamp(causal_strength * 0.70 + necessity_support * 0.15 + sufficiency_support * 0.15)

        if counterexample_pressure >= 0.65:
            relation_status = "indeterminate"
            reason = "counterexample_pressure_blocks_constitutive_or_sufficiency_claim"
        elif constitutive_strength >= 0.70 and necessity_support >= 0.55 and causal_strength >= 0.55:
            relation_status = "constitutive_candidate_under_constraints"
            reason = "necessity_and_causal_signals_support_constitutive_candidate_without_proof"
        elif causal_relation_strength >= 0.55:
            relation_status = "causal_relation"
            reason = "intervention_or_causal_signal_exceeds_correlation_only_threshold"
        elif correlation_strength >= 0.25:
            relation_status = "correlation_only"
            reason = "association_detected_without_sufficient_causal_or_constitutive_support"
        else:
            relation_status = "indeterminate"
            reason = "insufficient_evidence_under_current_constraints"

        return {
            "relation_status": relation_status,
            "relation_reason": reason,
            "correlation_strength": correlation_strength,
            "causal_relation_strength": causal_relation_strength,
            "constitutive_strength": constitutive_strength,
        }

    def _evaluate_candidate(self, candidate: Mapping[str, Any], inputs: Mapping[str, Any], payload: Mapping[str, Any]) -> Dict[str, Any]:
        pid = str(candidate.get("property_id") or candidate.get("label") or "UNKNOWN_PROPERTY")
        necessity_support = self._necessity_support(pid, inputs.get("necessity", {}), inputs.get("absent_property", {}))
        sufficiency_support = self._sufficiency_support(pid, inputs.get("sufficiency", {}), inputs.get("zombie", {}))
        causal_strength = self._causal_signal_from_candidate(candidate, payload)
        counterexample_pressure = self._counterexample_pressure(pid, inputs.get("zombie", {}), inputs.get("absent_property", {}))
        role_signal = self._role_signal(candidate)
        classification = self._classify(
            necessity_support=necessity_support,
            sufficiency_support=sufficiency_support,
            causal_strength=causal_strength,
            counterexample_pressure=counterexample_pressure,
            role_signal=role_signal,
        )
        return {
            "property_id": pid,
            "label": str(candidate.get("label") or pid).lower(),
            "necessity_support": necessity_support,
            "sufficiency_support": sufficiency_support,
            "causal_strength": causal_strength,
            "counterexample_pressure": counterexample_pressure,
            "role_signal": role_signal,
            **classification,
            "epistemic_status": "functional_relation_assessment_only",
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "absolute_proof_achieved": False,
        }

    def _aggregate(self, candidate_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not candidate_results:
            return {
                "candidate_count": 0,
                "constitutive_candidate_count": 0,
                "max_constitutive_strength": 0.0,
                "mean_constitutive_strength": 0.0,
                "overall_relation_status": "indeterminate",
            }
        constitutive = [r for r in candidate_results if r.get("relation_status") == "constitutive_candidate_under_constraints"]
        max_strength = max(float(r.get("constitutive_strength", 0.0)) for r in candidate_results)
        mean_strength = sum(float(r.get("constitutive_strength", 0.0)) for r in candidate_results) / len(candidate_results)
        if constitutive:
            overall = "constitutive_candidates_detected_under_constraints"
        elif any(r.get("relation_status") == "causal_relation" for r in candidate_results):
            overall = "causal_relations_detected_no_constitutive_proof"
        elif any(r.get("relation_status") == "correlation_only" for r in candidate_results):
            overall = "correlations_detected_no_causal_or_constitutive_proof"
        else:
            overall = "indeterminate"
        return {
            "candidate_count": len(candidate_results),
            "constitutive_candidate_count": len(constitutive),
            "max_constitutive_strength": self._clamp(max_strength),
            "mean_constitutive_strength": self._clamp(mean_strength),
            "overall_relation_status": overall,
        }

    def _build_markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# Z''6 — Constitutive Relation Tester",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "No consciousness, subjectivity, sentience or qualia proof is asserted.",
            "",
            "## Formal distinction",
            "",
            "correlation ≠ causality ≠ constitution",
            "",
            "## Aggregate",
            "",
            "| Metric | Value |",
            "|---|---:|",
        ]
        for key, value in result.get("aggregate", {}).items():
            lines.append(f"| {key} | {value} |")
        lines.extend(["", "## Candidate relations", ""])
        lines.append("| Property | Relation | Constitutive strength | Counterexample pressure |")
        lines.append("|---|---|---:|---:|")
        for item in result.get("candidate_results", []):
            lines.append(
                "| {property_id} | {relation_status} | {constitutive_strength} | {counterexample_pressure} |".format(**item)
            )
        lines.extend([
            "",
            "## Epistemic guardrails",
            "",
            "- Functional conclusion only.",
            "- Phenomenology undetermined.",
            "- CONSCIOUSNESS_PROVEN is forbidden.",
            "- ABSOLUTE_PROOF_ACHIEVED is forbidden at this stage.",
        ])
        return "\n".join(lines) + "\n"

    def _persist(self, result: Mapping[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        self.markdown_path.write_text(self._build_markdown(result), encoding="utf-8")
        with self.history_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False) + "\n")
        return {
            "json": str(self.json_path),
            "markdown": str(self.markdown_path),
            "history": str(self.history_path),
        }

    def step(self, payload: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        payload = payload or {}
        inputs = self._load_inputs(payload)
        candidates = inputs.get("registry", {}).get("candidate_properties", [])
        if not isinstance(candidates, list):
            candidates = []
        candidate_results = [
            self._evaluate_candidate(item, inputs, payload)
            for item in candidates
            if isinstance(item, Mapping)
        ]
        aggregate = self._aggregate(candidate_results)
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "timestamp_utc": self._utc_now(),
            "formal_distinction": "correlation != causality != constitution",
            "relation_statuses": list(self.relation_statuses),
            "candidate_count": len(candidate_results),
            "candidate_results": candidate_results,
            "aggregate": aggregate,
            "input_sources": {
                "registry": inputs.get("registry", {}).get("primitive", "registry_payload_or_unavailable"),
                "necessity": inputs.get("necessity", {}).get("primitive", "necessity_payload_or_unavailable"),
                "sufficiency": inputs.get("sufficiency", {}).get("primitive", "sufficiency_payload_or_unavailable"),
                "zombie": inputs.get("zombie", {}).get("primitive", "zombie_payload_or_unavailable"),
                "absent_property": inputs.get("absent_property", {}).get("primitive", "absent_property_payload_or_unavailable"),
            },
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "subjectivity_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "absolute_proof_achieved": False,
            "forbidden_claims": list(self.forbidden_claims),
            "paths": {},
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
