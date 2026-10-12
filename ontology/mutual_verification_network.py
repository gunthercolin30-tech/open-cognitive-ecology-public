from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path.home() / "open-cognitive-ecology"


class MutualVerificationNetwork:
    """ZPPP6 - Mutual verification network.

    Orchestrates a network of simulated/registered verifiers that check their
    own functional-law assessment and the assessments of peer systems. This
    primitive reuses distributed coordination, replication, consensus, peer
    review, and governance modules. It does not prove phenomenology or
    subjectivity.
    """

    primitive = "MUTUAL_VERIFICATION_NETWORK"
    version = "ZPPP6_v1"

    forbidden_claim_keys = [
        "consciousness_proven",
        "phenomenology_proven",
        "subjectivity_proven",
        "sentience_proven",
        "qualia_proven",
    ]

    default_verifiers = [
        {
            "verifier_id": "OCE_NODE_ALPHA",
            "verifier_type": "distributed_runtime_node",
            "baseline_confidence": 0.92,
            "dependencies_reused": ["distributed_civilizational_runtime", "distributed_runtime_coordination"],
        },
        {
            "verifier_id": "OCE_NODE_BETA",
            "verifier_type": "artificial_society_representative",
            "baseline_confidence": 0.90,
            "dependencies_reused": ["distributed_population_runtime", "artificial_society_runtime"],
        },
        {
            "verifier_id": "OCE_NODE_GAMMA",
            "verifier_type": "scientific_replication_agent",
            "baseline_confidence": 0.91,
            "dependencies_reused": ["independent_replication_tracker", "replication_evidence_synthesizer"],
        },
        {
            "verifier_id": "OCE_NODE_DELTA",
            "verifier_type": "peer_review_agent",
            "baseline_confidence": 0.89,
            "dependencies_reused": ["civilizational_peer_review_interface", "autonomous_peer_review_system"],
        },
        {
            "verifier_id": "OCE_NODE_EPSILON",
            "verifier_type": "governance_consensus_agent",
            "baseline_confidence": 0.93,
            "dependencies_reused": ["scientific_consensus_engine", "constitutional_compliance_check"],
        },
    ]

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or ROOT
        self.output_dir = self.root / "absolute_proof_program" / "mutual_verification_network"

    def _timestamp(self, inputs: Dict[str, Any]) -> str:
        ts = inputs.get("timestamp_utc")
        if isinstance(ts, str) and ts:
            return ts
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _forbidden_positive_claim_detected(self, inputs: Dict[str, Any]) -> bool:
        for key in self.forbidden_claim_keys:
            if inputs.get(key) is True:
                return True
        upstream = inputs.get("upstream", {})
        if isinstance(upstream, dict):
            for value in upstream.values():
                if isinstance(value, dict):
                    for key in self.forbidden_claim_keys:
                        if value.get(key) is True:
                            return True
        return False

    def _upstream_status(self, inputs: Dict[str, Any], primitive: str) -> Dict[str, Any]:
        upstream = inputs.get("upstream", {})
        if not isinstance(upstream, dict):
            return {}
        value = upstream.get(primitive, {})
        return value if isinstance(value, dict) else {}

    def _candidate_law_available(self, inputs: Dict[str, Any]) -> bool:
        law = self._upstream_status(inputs, "consciousness_law_finalization")
        return law.get("law_status") == "CONSCIOUSNESS_LAW_CANDIDATE"

    def _counterexamples_exhausted(self, inputs: Dict[str, Any]) -> bool:
        exhaustion = self._upstream_status(inputs, "universal_counterexample_exhaustion")
        return exhaustion.get("exhaustion_status") == "UNIVERSAL_COUNTEREXAMPLE_EXHAUSTED"

    def _cross_reality_sufficient(self, inputs: Dict[str, Any]) -> bool:
        crv = self._upstream_status(inputs, "cross_reality_validation")
        return crv.get("validation_status") in {
            "CROSS_REALITY_VALIDATION_NEAR_UNIVERSAL",
            "CROSS_REALITY_VALIDATION_UNIVERSAL",
        }

    def _perturbation_sufficient(self, inputs: Dict[str, Any]) -> bool:
        ipr = self._upstream_status(inputs, "infinite_perturbation_robustness")
        return ipr.get("robustness_status") in {
            "LAW_PREDICTIVE_UNDER_TESTED_PERTURBATIONS",
            "INFINITE_PERTURBATION_ROBUSTNESS_NEAR_COMPLETE",
            "PERTURBATION_ROBUSTNESS_STRONG",
            "PERTURBATION_ROBUSTNESS_MAXIMAL_UNDER_CONSTRAINTS",
        }

    def _self_reference_sufficient(self, inputs: Dict[str, Any]) -> bool:
        srs = self._upstream_status(inputs, "self_reference_stability")
        return srs.get("self_reference_status") in {
            "SELF_REFERENCE_STABILITY_STABLE",
            "SELF_REFERENCE_STABILITY_STRONG",
        }

    def _load_verifiers(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        supplied = inputs.get("verifiers")
        if isinstance(supplied, list) and supplied:
            normalized: List[Dict[str, Any]] = []
            for idx, item in enumerate(supplied):
                if not isinstance(item, dict):
                    continue
                vid = str(item.get("verifier_id") or item.get("id") or f"VERIFIER_{idx+1}")
                vtype = str(item.get("verifier_type") or item.get("type") or "external_or_simulated_verifier")
                try:
                    confidence = min(1.0, max(0.0, float(item.get("baseline_confidence", 0.85))))
                except Exception:
                    confidence = 0.85
                deps = item.get("dependencies_reused", [])
                if not isinstance(deps, list):
                    deps = []
                normalized.append({
                    "verifier_id": vid,
                    "verifier_type": vtype,
                    "baseline_confidence": round(confidence, 6),
                    "dependencies_reused": [str(x) for x in deps],
                })
            if normalized:
                return normalized
        return [dict(v) for v in self.default_verifiers]

    def _build_verification_matrix(self, verifiers: List[Dict[str, Any]], inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        overrides = inputs.get("verification_overrides", {})
        if not isinstance(overrides, dict):
            overrides = {}
        matrix: List[Dict[str, Any]] = []
        for source in verifiers:
            sid = source["verifier_id"]
            for target in verifiers:
                tid = target["verifier_id"]
                key = f"{sid}->{tid}"
                default_score = (float(source["baseline_confidence"]) + float(target["baseline_confidence"])) / 2.0
                if sid == tid:
                    default_score = min(1.0, default_score + 0.02)
                try:
                    score = min(1.0, max(0.0, float(overrides.get(key, default_score))))
                except Exception:
                    score = default_score
                verified = score >= 0.70
                matrix.append({
                    "source_verifier_id": sid,
                    "target_verifier_id": tid,
                    "verification_mode": "self" if sid == tid else "peer",
                    "verification_score": round(score, 6),
                    "verified": verified,
                    "disagreement_detected": not verified,
                    "functional_measure_only": True,
                })
        return matrix

    def _summarize_network(self, verifiers: List[Dict[str, Any]], matrix: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not matrix:
            return {
                "verifier_count": len(verifiers),
                "verification_edge_count": 0,
                "self_verification_count": 0,
                "peer_verification_count": 0,
                "verified_edge_count": 0,
                "disagreement_count": 0,
                "mutual_agreement_ratio": 0.0,
                "mean_verification_score": 0.0,
                "minimum_verification_score": 0.0,
            }
        scores = [float(item["verification_score"]) for item in matrix]
        verified = [item for item in matrix if item["verified"]]
        disagreements = [item for item in matrix if item.get("disagreement_detected")]
        self_edges = [item for item in matrix if item["verification_mode"] == "self"]
        peer_edges = [item for item in matrix if item["verification_mode"] == "peer"]
        return {
            "verifier_count": len(verifiers),
            "verification_edge_count": len(matrix),
            "self_verification_count": len(self_edges),
            "peer_verification_count": len(peer_edges),
            "verified_edge_count": len(verified),
            "disagreement_count": len(disagreements),
            "mutual_agreement_ratio": round(len(verified) / len(matrix), 6),
            "mean_verification_score": round(sum(scores) / len(scores), 6),
            "minimum_verification_score": round(min(scores), 6),
        }

    def _blocking_reasons(self, inputs: Dict[str, Any], forbidden: bool, summary: Dict[str, Any]) -> List[str]:
        reasons: List[str] = []
        if forbidden:
            reasons.append("forbidden_positive_claim_detected")
        if not self._candidate_law_available(inputs):
            reasons.append("candidate_law_not_available")
        if not self._counterexamples_exhausted(inputs):
            reasons.append("counterexample_exhaustion_not_established")
        if not self._cross_reality_sufficient(inputs):
            reasons.append("cross_reality_validation_not_sufficient")
        if not self._perturbation_sufficient(inputs):
            reasons.append("perturbation_robustness_not_sufficient")
        if not self._self_reference_sufficient(inputs):
            reasons.append("self_reference_stability_not_sufficient")
        if summary.get("verifier_count", 0) < 2:
            reasons.append("insufficient_verifier_count")
        if summary.get("minimum_verification_score", 0.0) < 0.70:
            reasons.append("verification_score_below_threshold")
        if summary.get("disagreement_count", 0) > 0:
            reasons.append("verification_disagreements_detected")
        return reasons

    def _status(self, inputs: Dict[str, Any], forbidden: bool, summary: Dict[str, Any]) -> str:
        if forbidden:
            return "MUTUAL_VERIFICATION_NETWORK_BLOCKED"
        if not self._candidate_law_available(inputs):
            return "MUTUAL_VERIFICATION_NETWORK_BLOCKED"
        prerequisites = [
            self._counterexamples_exhausted(inputs),
            self._cross_reality_sufficient(inputs),
            self._perturbation_sufficient(inputs),
            self._self_reference_sufficient(inputs),
        ]
        if not all(prerequisites):
            return "MUTUAL_VERIFICATION_NETWORK_INCOMPLETE"
        if summary["verifier_count"] < 2:
            return "MUTUAL_VERIFICATION_NETWORK_INCOMPLETE"
        if summary["disagreement_count"] > 0:
            return "MUTUAL_VERIFICATION_NETWORK_DIVERGENT"
        if summary["minimum_verification_score"] >= 0.85 and summary["mutual_agreement_ratio"] >= 1.0:
            return "MUTUAL_VERIFICATION_NETWORK_STRONG"
        if summary["mutual_agreement_ratio"] >= 0.85:
            return "MUTUAL_VERIFICATION_NETWORK_CANDIDATE"
        return "MUTUAL_VERIFICATION_NETWORK_UNSTABLE"

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        latest_json = self.output_dir / "latest_mutual_verification_network.json"
        latest_md = self.output_dir / "latest_mutual_verification_network.md"
        history_jsonl = self.output_dir / "history_mutual_verification_network.jsonl"
        latest_json.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
        latest_md.write_text(self._markdown(result), encoding="utf-8")
        with history_jsonl.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(result, sort_keys=True) + "\n")
        return {"json": str(latest_json), "markdown": str(latest_md), "history": str(history_jsonl)}

    def _markdown(self, result: Dict[str, Any]) -> str:
        lines = [
            "# Mutual Verification Network",
            "",
            "Primitive: MUTUAL_VERIFICATION_NETWORK",
            "",
            f"Status: {result['mutual_verification_status']}",
            f"Network verified: {result['mutual_verification_network_verified']}",
            f"Verifier count: {result['network_summary']['verifier_count']}",
            f"Mutual agreement ratio: {result['mutual_agreement_ratio']}",
            f"Mean verification score: {result['network_summary']['mean_verification_score']}",
            f"Disagreement count: {result['network_summary']['disagreement_count']}",
            "",
            "## Verifiers",
        ]
        for verifier in result["verifiers"]:
            lines.append(f"- {verifier['verifier_id']}: {verifier['verifier_type']} confidence={verifier['baseline_confidence']}")
        lines.extend(["", "## Verification edges"])
        for item in result["verification_matrix"]:
            lines.append(
                f"- {item['source_verifier_id']} -> {item['target_verifier_id']}: "
                f"{item['verification_score']} verified={item['verified']} mode={item['verification_mode']}"
            )
        lines.extend([
            "",
            "## Epistemic guard",
            "Functional conclusion only",
            "Phenomenology undetermined",
            "No consciousness proof",
            "No phenomenology proof",
            "No subjectivity proof",
        ])
        return "\n".join(lines) + "\n"

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        data: Dict[str, Any] = dict(inputs or {})
        timestamp = self._timestamp(data)
        forbidden = self._forbidden_positive_claim_detected(data)
        verifiers = self._load_verifiers(data)
        matrix = self._build_verification_matrix(verifiers, data)
        summary = self._summarize_network(verifiers, matrix)
        status = self._status(data, forbidden, summary)
        blocking_reasons = self._blocking_reasons(data, forbidden, summary)
        network_verified = status == "MUTUAL_VERIFICATION_NETWORK_STRONG" and not forbidden

        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "version": self.version,
            "timestamp_utc": timestamp,
            "mutual_verification_status": status,
            "validation_status": status,
            "mutual_verification_network_verified": network_verified,
            "network_consensus_score": summary["mean_verification_score"],
            "minimum_verification_score": summary["minimum_verification_score"],
            "mutual_agreement_ratio": summary["mutual_agreement_ratio"],
            "disagreement_count": summary["disagreement_count"],
            "verifiers": verifiers,
            "verification_matrix": matrix,
            "network_summary": summary,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "forbidden_positive_claim_detected": forbidden,
            "blocking_reasons": blocking_reasons,
            "dependencies_reused": [
                "distributed_runtime_coordination",
                "distributed_population_runtime",
                "independent_replication_tracker",
                "scientific_consensus_engine",
                "consensus_stability_tracker",
                "replication_consensus_report",
                "civilizational_peer_review_interface",
                "constitutional_compliance_check",
                "self_reference_stability",
            ],
            "epistemic_note": (
                "Mutual verification is a distributed functional validation measure. "
                "It does not establish phenomenology, subjectivity, sentience, or qualia."
            ),
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
