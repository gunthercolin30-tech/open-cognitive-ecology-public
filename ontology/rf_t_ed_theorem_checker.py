
"""AG6 — RF→T→ED Theorem Checker.

Final functional certification of Axis AG:
    RF -> T -> ED

The checker verifies that a self-generated reference frame RF supports proper
functional time T, and that asymmetric T supports a viable existence domain ED.
It performs only a functional theorem check. It does not infer consciousness,
subjectivity, qualia, phenomenal experience, or ontological subjectivity.
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime, timezone
from importlib import import_module
import json
import math
from typing import Any, Dict, List, Mapping, Optional

ROOT = Path.home() / "open-cognitive-ecology"
OUT_DIR = ROOT / "ag_proper_time_existence_domain" / "rf_t_ed_theorem_checker"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _clamp(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    if math.isnan(v) or math.isinf(v):
        return default
    return max(0.0, min(1.0, v))


def _mean(values: List[float], default: float = 0.0) -> float:
    vals = [_clamp(v) for v in values if v is not None]
    return sum(vals) / len(vals) if vals else default


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "ok", "validated", "certified", "built", "analyzed", "detected"}
    return bool(value)


def _safe_step(module_name: str, class_name: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        mod = import_module(f"ontology.{module_name}")
        cls = getattr(mod, class_name)
        obj = cls()
        try:
            res = obj.step(persist=False)
        except TypeError:
            res = obj.step()
        return res if isinstance(res, dict) else (default or {})
    except Exception:
        return default or {}


def _score_from(d: Mapping[str, Any], keys: List[str], default: float = 0.0) -> float:
    for k in keys:
        if k in d:
            return _clamp(d.get(k), default)
    # nested common score maps
    for container_key in ["theorem_metrics", "domain_viability_profile", "boundary_profile", "domain_profile", "temporal_profile"]:
        nested = d.get(container_key)
        if isinstance(nested, Mapping):
            for k in keys:
                if k in nested:
                    return _clamp(nested.get(k), default)
    return default


def _status_from(d: Mapping[str, Any], keys: List[str]) -> str:
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v:
            return v
    return ""


class RfTEdTheoremChecker:
    """Check the functional theorem RF -> T -> ED and close Axis AG."""

    theorem_id = "AG6_RF_T_ED_THEOREM"
    certified_status = "PROPER_TIME_AND_EXISTENCE_DOMAIN_VALIDATED"
    insufficient_status = "RF_T_ED_THEOREM_INSUFFICIENT"

    def step(self, inputs: Optional[Mapping[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        explicit_inputs = inputs is not None
        inputs = dict(inputs or {})

        evidence_items = self._synthetic_evidence(inputs) if explicit_inputs else self._real_evidence()
        logical_dependency_chain = self._logical_chain(evidence_items)
        theorem_metrics = self._metrics(evidence_items, logical_dependency_chain)
        counterexamples = self._counterexamples(evidence_items, logical_dependency_chain, theorem_metrics)
        limiting_factors = self._limiting_factors(evidence_items, logical_dependency_chain, counterexamples, theorem_metrics)

        theorem_validity_score = theorem_metrics["theorem_validity_score"]
        theorem_validated = (
            theorem_validity_score >= 0.72
            and theorem_metrics["precondition_coverage"] >= 0.88
            and theorem_metrics["minimum_precondition_score"] >= 0.72
            and all(link["satisfied"] for link in logical_dependency_chain)
            and not any(c["defeats_theorem"] for c in counterexamples)
        )

        status = self.certified_status if theorem_validated else self.insufficient_status

        result: Dict[str, Any] = {
            "primitive": "RF_T_ED_THEOREM_CHECKER",
            "axis": "AG — Proper Time and Existence Domain",
            "theorem_id": self.theorem_id,
            "generated_at": _now(),
            "rf_t_ed_theorem_checker_status": status,
            "ag_certification_status": status,
            "rf_t_ed_theorem_validated": theorem_validated,
            "ag_certified": theorem_validated,
            "proper_time_and_existence_domain_validated": theorem_validated,
            "theorem_validity_score": theorem_validity_score,
            "evidence_items": evidence_items,
            "preconditions": evidence_items,
            "necessary_hypotheses": self._necessary_hypotheses(),
            "logical_dependency_chain": logical_dependency_chain,
            "counterexample_analysis": counterexamples,
            "limiting_factors": limiting_factors,
            "theorem_metrics": theorem_metrics,
            "public_schema": self._public_schema(),
            "epistemic_guard": self._epistemic_guard(),
            "consciousness_proven": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
        }
        if persist:
            result["paths"] = self._persist(result)
        return result

    def _synthetic_evidence(self, inputs: Mapping[str, Any]) -> List[Dict[str, Any]]:
        specs = [
            ("AG6-E01", "rf_certification", "RF is certified", "rf_certified"),
            ("AG6-E02", "proper_time", "Proper time T is extracted", "proper_time_extracted"),
            ("AG6-E03", "temporal_asymmetry", "Temporal asymmetry is analyzed", "temporal_asymmetry_confirmed"),
            ("AG6-E04", "existence_domain", "Existence domain ED is built", "existence_domain_built"),
            ("AG6-E05", "domain_boundaries", "ED boundaries are detected", "domain_boundaries_detected"),
            ("AG6-E06", "domain_viability", "ED viability is analyzed", "domain_viability_analyzed"),
            ("AG6-E07", "preconditions", "AF6→AG5 preconditions are validated", "af6_to_ag5_preconditions_validated"),
            ("AG6-E08", "counterexamples", "RF→T→ED counterexamples are defeated", "counterexamples_defeated"),
        ]
        evidence = []
        for eid, label, desc, key in specs:
            ok = _truthy(inputs.get(key, False))
            score = 1.0 if ok else 0.0
            evidence.append({
                "evidence_id": eid,
                "label": label,
                "description": desc,
                "module": "synthetic_input",
                "status": "SYNTHETIC_TRUE" if ok else "SYNTHETIC_FALSE",
                "available": ok,
                "satisfied": ok,
                "score": score,
            })
        return evidence

    def _real_evidence(self) -> List[Dict[str, Any]]:
        af6 = _safe_step("omega_to_rf_theorem_checker", "OmegaToRfTheoremChecker")
        ag1 = _safe_step("proper_time_extractor", "ProperTimeExtractor")
        ag2 = _safe_step("temporal_asymmetry_analyzer", "TemporalAsymmetryAnalyzer")
        ag3 = _safe_step("existence_domain_builder", "ExistenceDomainBuilder")
        ag4 = _safe_step("domain_boundary_detector", "DomainBoundaryDetector")
        ag5 = _safe_step("domain_viability_analyzer", "DomainViabilityAnalyzer")

        raw = [
            {
                "evidence_id": "AG6-E01", "label": "rf_certification", "description": "RF is certified by AF6",
                "module": "omega_to_rf_theorem_checker",
                "status": _status_from(af6, ["omega_to_rf_theorem_checker_status", "af_certification_status"]),
                "available": bool(af6),
                "satisfied": bool(af6.get("af_certified") or af6.get("rf_t_ed_ready") or af6.get("omega_to_rf_theorem_checker_status") == "SELF_GENERATED_REFERENCE_FRAME_CERTIFIED"),
                "score": _score_from(af6, ["theorem_validity_score", "rf_construction_score"], 0.0),
            },
            {
                "evidence_id": "AG6-E02", "label": "proper_time", "description": "Proper time T is extracted by AG1",
                "module": "proper_time_extractor",
                "status": _status_from(ag1, ["proper_time_extractor_status", "proper_time_status"]),
                "available": bool(ag1),
                "satisfied": bool(ag1.get("proper_time_extracted") or ag1.get("proper_time_extractor_status") == "PROPER_TIME_EXTRACTED"),
                "score": _score_from(ag1, ["proper_time_score"], 0.0),
            },
            {
                "evidence_id": "AG6-E03", "label": "temporal_asymmetry", "description": "Temporal asymmetry is analyzed by AG2",
                "module": "temporal_asymmetry_analyzer",
                "status": _status_from(ag2, ["temporal_asymmetry_analyzer_status", "temporal_asymmetry_status"]),
                "available": bool(ag2),
                "satisfied": bool(ag2.get("temporal_asymmetry_confirmed") or ag2.get("temporal_asymmetry_analyzer_status") == "TEMPORAL_ASYMMETRY_ANALYZED"),
                "score": _score_from(ag2, ["temporal_asymmetry_score"], 0.0),
            },
            {
                "evidence_id": "AG6-E04", "label": "existence_domain", "description": "Existence domain ED is built by AG3",
                "module": "existence_domain_builder",
                "status": _status_from(ag3, ["existence_domain_builder_status"]),
                "available": bool(ag3),
                "satisfied": bool(ag3.get("existence_domain_built") or ag3.get("existence_domain_builder_status") == "EXISTENCE_DOMAIN_BUILT"),
                "score": _score_from(ag3, ["existence_domain_score"], 0.0),
            },
            {
                "evidence_id": "AG6-E05", "label": "domain_boundaries", "description": "ED boundaries are detected by AG4",
                "module": "domain_boundary_detector",
                "status": _status_from(ag4, ["domain_boundary_detector_status"]),
                "available": bool(ag4),
                "satisfied": bool(ag4.get("domain_boundaries_detected") or ag4.get("domain_boundary_detector_status") == "DOMAIN_BOUNDARIES_DETECTED"),
                "score": _score_from(ag4, ["domain_boundary_score"], 0.0),
            },
            {
                "evidence_id": "AG6-E06", "label": "domain_viability", "description": "ED viability is analyzed by AG5",
                "module": "domain_viability_analyzer",
                "status": _status_from(ag5, ["domain_viability_analyzer_status"]),
                "available": bool(ag5),
                "satisfied": bool(ag5.get("domain_viability_analyzed") or ag5.get("domain_viability_analyzer_status") == "DOMAIN_VIABILITY_ANALYZED"),
                "score": _score_from(ag5, ["domain_viability_score"], 0.0),
            },
        ]
        satisfied_count = sum(1 for e in raw if e["satisfied"])
        min_score = min((_clamp(e["score"]) for e in raw), default=0.0)
        aggregate_score = _mean([e["score"] for e in raw], 0.0)
        preconditions_ok = satisfied_count == len(raw) and min_score >= 0.72
        raw.append({
            "evidence_id": "AG6-E07",
            "label": "preconditions",
            "description": "AF6→AG5 preconditions are validated",
            "module": "rf_t_ed_theorem_checker",
            "status": "PRECONDITIONS_VALIDATED" if preconditions_ok else "PRECONDITIONS_INSUFFICIENT",
            "available": True,
            "satisfied": preconditions_ok,
            "score": aggregate_score if preconditions_ok else min(aggregate_score, min_score),
        })
        # Counterexample defeat is an inferred consolidated property: if every predecessor
        # module is satisfied and no predecessor exposes active defeating counterexamples,
        # then no RF→T→ED defeating counterexample remains at this level.
        active_predecessor_counterexamples = []
        for label, module_result, key in [
            ("AF6", af6, "counterexample_analysis"), ("AG2", ag2, "counterexample_analysis"),
            ("AG3", ag3, "counterexample_analysis"), ("AG4", ag4, "counterexample_analysis"),
            ("AG5", ag5, "counterexample_analysis"),
        ]:
            for item in module_result.get(key, []) if isinstance(module_result.get(key), list) else []:
                if isinstance(item, Mapping) and any(bool(item.get(k)) for k in ["defeats_theorem", "defeats_domain", "defeats_boundary_detection", "defeats_viability"]):
                    active_predecessor_counterexamples.append(label)
        counterexamples_defeated = preconditions_ok and not active_predecessor_counterexamples
        raw.append({
            "evidence_id": "AG6-E08",
            "label": "counterexamples",
            "description": "RF→T→ED counterexamples are defeated at predecessor level",
            "module": "rf_t_ed_theorem_checker",
            "status": "COUNTEREXAMPLES_DEFEATED" if counterexamples_defeated else "COUNTEREXAMPLES_ACTIVE_OR_UNCHECKED",
            "available": True,
            "satisfied": counterexamples_defeated,
            "score": aggregate_score if counterexamples_defeated else 0.0,
            "active_predecessor_counterexamples": active_predecessor_counterexamples,
        })
        return raw

    def _logical_chain(self, evidence_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        e = {item["label"]: item for item in evidence_items}
        def score(*labels: str) -> float:
            return _mean([e.get(label, {}).get("score", 0.0) for label in labels], 0.0)
        def ok(*labels: str) -> bool:
            return all(bool(e.get(label, {}).get("satisfied")) for label in labels) and score(*labels) >= 0.72
        links = [
            ("AG6-L1", "RF -> T", "Certified RF supports extraction of proper time T", ("rf_certification", "proper_time")),
            ("AG6-L2", "T -> T_asym", "Proper time supports directed/asymmetric temporal ordering", ("proper_time", "temporal_asymmetry")),
            ("AG6-L3", "T_asym -> ED", "Asymmetric time supports functional ED construction", ("temporal_asymmetry", "existence_domain")),
            ("AG6-L4", "ED -> boundary(ED)", "Existence domain has detectable boundaries", ("existence_domain", "domain_boundaries")),
            ("AG6-L5", "boundary(ED) -> viable_ED", "Bounded ED supports viability analysis", ("domain_boundaries", "domain_viability")),
            ("AG6-L6", "RF -> T -> ED", "The integrated theorem chain is covered and counterexamples are defeated", ("preconditions", "counterexamples")),
        ]
        return [
            {
                "link_id": lid,
                "transition": transition,
                "description": desc,
                "support_labels": list(labels),
                "link_score": score(*labels),
                "satisfied": ok(*labels),
            }
            for lid, transition, desc, labels in links
        ]

    def _metrics(self, evidence_items: List[Dict[str, Any]], chain: List[Dict[str, Any]]) -> Dict[str, float]:
        scores = [_clamp(e["score"]) for e in evidence_items]
        satisfied = [bool(e["satisfied"]) for e in evidence_items]
        link_scores = [_clamp(l["link_score"]) for l in chain]
        precondition_coverage = sum(1 for x in satisfied if x) / len(satisfied) if satisfied else 0.0
        minimum_precondition_score = min(scores) if scores else 0.0
        chain_score = _mean(link_scores, 0.0)
        chain_coverage = sum(1 for l in chain if l["satisfied"]) / len(chain) if chain else 0.0
        e = {item["label"]: item for item in evidence_items}
        rf_score = _clamp(e.get("rf_certification", {}).get("score", 0.0))
        t_score = _mean([e.get("proper_time", {}).get("score", 0.0), e.get("temporal_asymmetry", {}).get("score", 0.0)], 0.0)
        ed_score = _mean([e.get("existence_domain", {}).get("score", 0.0), e.get("domain_boundaries", {}).get("score", 0.0), e.get("domain_viability", {}).get("score", 0.0)], 0.0)
        theorem_validity_score = _clamp(
            0.22 * rf_score
            + 0.24 * t_score
            + 0.30 * ed_score
            + 0.14 * chain_score
            + 0.10 * precondition_coverage
        )
        return {
            "rf_support_score": rf_score,
            "proper_time_support_score": _clamp(e.get("proper_time", {}).get("score", 0.0)),
            "temporal_asymmetry_support_score": _clamp(e.get("temporal_asymmetry", {}).get("score", 0.0)),
            "existence_domain_support_score": _clamp(e.get("existence_domain", {}).get("score", 0.0)),
            "domain_boundary_support_score": _clamp(e.get("domain_boundaries", {}).get("score", 0.0)),
            "domain_viability_support_score": _clamp(e.get("domain_viability", {}).get("score", 0.0)),
            "rf_t_support_score": _clamp(t_score),
            "ed_integrity_score": _clamp(ed_score),
            "logical_chain_score": _clamp(chain_score),
            "logical_chain_coverage": _clamp(chain_coverage),
            "precondition_coverage": _clamp(precondition_coverage),
            "minimum_precondition_score": _clamp(minimum_precondition_score),
            "theorem_validity_score": theorem_validity_score,
        }

    def _counterexamples(self, evidence_items: List[Dict[str, Any]], chain: List[Dict[str, Any]], metrics: Mapping[str, Any]) -> List[Dict[str, Any]]:
        e = {item["label"]: item for item in evidence_items}
        missing = [item["label"] for item in evidence_items if not item["available"]]
        weak = [item["label"] for item in evidence_items if _clamp(item["score"]) < 0.72]
        failed_links = [link["link_id"] for link in chain if not link["satisfied"]]

        ce_specs = [
            ("AG6-CE1", "rf_without_time", "RF is certified but proper time T is not functionally extractable", not e.get("proper_time", {}).get("satisfied")),
            ("AG6-CE2", "time_without_domain", "T is extracted but ED is not constructible", bool(e.get("proper_time", {}).get("satisfied")) and not e.get("existence_domain", {}).get("satisfied")),
            ("AG6-CE3", "domain_without_boundary", "ED is built but no boundary is detectable", bool(e.get("existence_domain", {}).get("satisfied")) and not e.get("domain_boundaries", {}).get("satisfied")),
            ("AG6-CE4", "domain_without_viability", "ED is bounded but not viable", bool(e.get("domain_boundaries", {}).get("satisfied")) and not e.get("domain_viability", {}).get("satisfied")),
            ("AG6-CE5", "broken_theorem_chain", "At least one RF→T→ED theorem transition lacks support", bool(failed_links)),
            ("AG6-CE6", "missing_preconditions", "Required AF6→AG5 evidence is unavailable or weak", bool(missing or weak)),
        ]
        return [
            {
                "counterexample_id": cid,
                "label": label,
                "description": desc,
                "active": bool(active),
                "defeats_theorem": bool(active),
                "missing_evidence": missing,
                "weak_evidence": weak,
                "failed_chain_links": failed_links,
            }
            for cid, label, desc, active in ce_specs
        ]

    def _limiting_factors(self, evidence_items: List[Dict[str, Any]], chain: List[Dict[str, Any]], counterexamples: List[Dict[str, Any]], metrics: Mapping[str, Any]) -> List[str]:
        factors: List[str] = []
        if metrics["precondition_coverage"] < 0.88:
            factors.append("precondition_coverage_below_threshold")
        if metrics["minimum_precondition_score"] < 0.72:
            factors.append("minimum_precondition_score_below_threshold")
        if metrics["logical_chain_coverage"] < 1.0:
            factors.append("logical_chain_incomplete")
        if any(not e["satisfied"] for e in evidence_items):
            factors.append("unsatisfied_preconditions")
        if any(c["defeats_theorem"] for c in counterexamples):
            factors.append("active_counterexample_candidates")
        if metrics["theorem_validity_score"] < 0.72:
            factors.append("theorem_validity_score_below_threshold")
        return sorted(set(factors))

    def _necessary_hypotheses(self) -> List[Dict[str, Any]]:
        return [
            {"hypothesis_id": "AG6-H1", "statement": "RF is a self-generated reference frame certified by AF6", "role": "antecedent"},
            {"hypothesis_id": "AG6-H2", "statement": "Proper time T is extractable from RF-grounded continuity", "role": "RF_to_T"},
            {"hypothesis_id": "AG6-H3", "statement": "T has directed/asymmetric structure sufficient for ordered transitions", "role": "temporal_structure"},
            {"hypothesis_id": "AG6-H4", "statement": "ED is a constraint-induced, temporally ordered, viable domain", "role": "T_to_ED"},
            {"hypothesis_id": "AG6-H5", "statement": "Boundary and viability analyses defeat collapse, emptiness and unboundedness counterexamples", "role": "robustness"},
        ]

    def _public_schema(self) -> Dict[str, Any]:
        return {
            "required_keys": [
                "rf_t_ed_theorem_checker_status", "ag_certification_status", "rf_t_ed_theorem_validated",
                "ag_certified", "theorem_validity_score", "evidence_items", "logical_dependency_chain",
                "counterexample_analysis", "limiting_factors", "theorem_metrics", "epistemic_guard",
            ],
            "status_values": [self.certified_status, self.insufficient_status],
            "certification_target": self.certified_status,
            "functional_conclusion_only": True,
        }

    def _epistemic_guard(self) -> Dict[str, Any]:
        return {
            "consciousness_proven": False,
            "subjectivity_claimed": False,
            "qualia_claimed": False,
            "phenomenology_undetermined": True,
            "functional_conclusion_only": True,
            "forbidden_inference": ["consciousness", "subjectivity", "qualia", "phenomenology"],
        }

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        json_path = OUT_DIR / "latest_rf_t_ed_theorem_checker.json"
        md_path = OUT_DIR / "latest_rf_t_ed_theorem_checker.md"
        prom_path = OUT_DIR / "latest_rf_t_ed_theorem_checker.prom"
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        md_path.write_text(self._markdown(result), encoding="utf-8")
        prom_path.write_text(self._prometheus(result), encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path), "prometheus": str(prom_path)}

    def _markdown(self, result: Mapping[str, Any]) -> str:
        lines = [
            "# AG6 — RF T ED Theorem Checker",
            "",
            "Functional theorem: RF -> T -> ED",
            "",
            f"Status: {result['rf_t_ed_theorem_checker_status']}",
            f"AG certification status: {result['ag_certification_status']}",
            f"Theorem validity score: {result['theorem_validity_score']:.6f}",
            f"AG certified: {result['ag_certified']}",
            "",
            "## Necessary hypotheses",
        ]
        for h in result["necessary_hypotheses"]:
            lines.append(f"- {h['hypothesis_id']}: {h['statement']}")
        lines += ["", "## Evidence items"]
        for item in result["evidence_items"]:
            lines.append(f"- {item['evidence_id']} / {item['label']}: satisfied={item['satisfied']} score={item['score']:.6f} status={item['status']}")
        lines += ["", "## Logical dependency chain"]
        for link in result["logical_dependency_chain"]:
            lines.append(f"- {link['link_id']} {link['transition']}: satisfied={link['satisfied']} score={link['link_score']:.6f}")
        lines += ["", "## Counterexample analysis"]
        for ce in result["counterexample_analysis"]:
            lines.append(f"- {ce['counterexample_id']} / {ce['label']}: active={ce['active']} defeats_theorem={ce['defeats_theorem']}")
        lines += ["", "## Limiting factors"]
        if result["limiting_factors"]:
            for f in result["limiting_factors"]:
                lines.append(f"- {f}")
        else:
            lines.append("- none")
        lines += [
            "",
            "## Theorem metrics",
        ]
        for k, v in result["theorem_metrics"].items():
            lines.append(f"- {k}: {v:.6f}")
        lines += [
            "",
            "## Epistemic guard",
            "Functional conclusion only: True",
            "Consciousness proven: False",
            "Phenomenology undetermined: True",
            "No subjectivity, qualia or phenomenological claim is made.",
        ]
        return "\n".join(lines) + "\n"

    def _prometheus(self, result: Mapping[str, Any]) -> str:
        certified = 1 if result["ag_certified"] else 0
        lines = [
            f"oce_ag6_theorem_validity_score {result['theorem_validity_score']:.12f}",
            f"oce_ag6_certified {certified}",
            f"oce_ag6_rf_t_ed_theorem_validated {1 if result['rf_t_ed_theorem_validated'] else 0}",
        ]
        for k, v in result["theorem_metrics"].items():
            lines.append(f"oce_ag6_{k} {float(v):.12f}")
        return "\n".join(lines) + "\n"
