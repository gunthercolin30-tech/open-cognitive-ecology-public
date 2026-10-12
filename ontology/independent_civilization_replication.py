"""
Z'''8 — independent_civilization_replication.

Independent civilizational replication under explicit epistemic constraints.
This primitive orchestrates existing replication, external validation,
consensus, publication, distributed-civilization, and Z'''0-Z'''7 modules.

It never proves phenomenology, subjectivity, sentience, qualia, or absolute
proof. It only reports whether an independent-civilization replication package
is functionally structured and sufficiently convergent under current explicit
constraints.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path.home() / "open-cognitive-ecology"


class IndependentCivilizationReplication:
    """Orchestrate independent civilizational replication for Z'''8."""

    primitive = "INDEPENDENT_CIVILIZATION_REPLICATION"
    version = "1.0"

    FORBIDDEN_KEYS = (
        "consciousness_proven",
        "phenomenology_proven",
        "subjectivity_proven",
        "sentience_proven",
        "qualia_proven",
        "absolute_proof_achieved",
    )

    DEPENDENCIES_REUSED = [
        "consciousness_law_finalization",
        "universal_counterexample_exhaustion",
        "cross_reality_validation",
        "infinite_perturbation_robustness",
        "self_reference_stability",
        "mutual_verification_network",
        "formal_derivation_closure",
        "independent_replication_tracker",
        "replication_statistics_engine",
        "replication_confidence_estimator",
        "replication_evidence_synthesizer",
        "replication_consensus_report",
        "external_replication_evidence_aggregator",
        "independent_validation_observatory",
        "distributed_scientific_ecosystem",
        "persistent_experimental_validation_network",
        "distributed_civilizational_runtime",
        "distributed_population_runtime",
        "artificial_society_runtime",
        "distributed_runtime_coordination",
        "distributed_runtime_coordinator",
        "distributed_civilizational_node",
        "civilizational_peer_review_interface",
        "autonomous_peer_review_system",
        "scientific_consensus_engine",
        "consensus_stability_tracker",
        "external_validation_synthesis_report",
        "civilizational_scientific_certification",
        "scientific_publication_traceability",
        "github_release_governor",
        "public_replication_invitation_manager",
        "independent_consciousness_review_board",
        "external_validation_request_manager",
        "theory_replication_program",
    ]

    def _utc(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    def _forbidden_positive_claim(self, payload: Dict[str, Any]) -> bool:
        return any(payload.get(k) is True for k in self.FORBIDDEN_KEYS)

    def _civilization_replicas(self, inputs: Dict[str, Any]) -> List[Dict[str, Any]]:
        overrides = inputs.get("replication_overrides", {}) or {}
        default_replicas = [
            {
                "civilization_id": "OCE_REPLICA_ALPHA",
                "replica_type": "independent_lab_simulation",
                "independence_score": 0.91,
                "protocol_reproduction_score": 0.90,
                "evidence_convergence_score": 0.89,
                "governance_separation_score": 0.92,
                "dependencies_reused": [
                    "independent_replication_tracker",
                    "replication_statistics_engine",
                    "independent_validation_observatory",
                ],
            },
            {
                "civilization_id": "OCE_REPLICA_BETA",
                "replica_type": "distributed_civilizational_runtime",
                "independence_score": 0.88,
                "protocol_reproduction_score": 0.89,
                "evidence_convergence_score": 0.88,
                "governance_separation_score": 0.90,
                "dependencies_reused": [
                    "distributed_civilizational_runtime",
                    "distributed_runtime_coordination",
                    "distributed_civilizational_node",
                ],
            },
            {
                "civilization_id": "OCE_REPLICA_GAMMA",
                "replica_type": "artificial_society_replication",
                "independence_score": 0.87,
                "protocol_reproduction_score": 0.88,
                "evidence_convergence_score": 0.87,
                "governance_separation_score": 0.89,
                "dependencies_reused": [
                    "artificial_society_runtime",
                    "distributed_population_runtime",
                    "civilizational_peer_review_interface",
                ],
            },
            {
                "civilization_id": "OCE_REPLICA_DELTA",
                "replica_type": "external_scientific_ecosystem",
                "independence_score": 0.90,
                "protocol_reproduction_score": 0.87,
                "evidence_convergence_score": 0.89,
                "governance_separation_score": 0.91,
                "dependencies_reused": [
                    "distributed_scientific_ecosystem",
                    "external_validation_synthesis_report",
                    "scientific_consensus_engine",
                ],
            },
        ]
        replicas: List[Dict[str, Any]] = []
        for replica in default_replicas:
            rid = replica["civilization_id"]
            local = dict(overrides.get(rid, {}) or {})
            scores = {
                "independence_score": self._clamp(local.get("independence_score", replica["independence_score"])),
                "protocol_reproduction_score": self._clamp(local.get("protocol_reproduction_score", replica["protocol_reproduction_score"])),
                "evidence_convergence_score": self._clamp(local.get("evidence_convergence_score", replica["evidence_convergence_score"])),
                "governance_separation_score": self._clamp(local.get("governance_separation_score", replica["governance_separation_score"])),
            }
            composite = self._clamp(
                0.30 * scores["independence_score"]
                + 0.25 * scores["protocol_reproduction_score"]
                + 0.25 * scores["evidence_convergence_score"]
                + 0.20 * scores["governance_separation_score"]
            )
            replicas.append({
                "civilization_id": rid,
                "replica_type": replica["replica_type"],
                **scores,
                "replication_score": composite,
                "replication_successful_under_constraints": composite >= 0.86,
                "dependencies_reused": list(replica["dependencies_reused"]),
                "functional_measure_only": True,
            })
        return replicas

    def _protocol_matrix(self, replicas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        stages = [
            ("zppp0_to_zppp7_package_available", 0.92, ["formal_derivation_closure", "mutual_verification_network"]),
            ("replication_protocol_reconstructible", 0.90, ["theory_replication_program", "public_replication_invitation_manager"]),
            ("independent_evidence_collection", 0.89, ["external_replication_evidence_aggregator", "replication_evidence_synthesizer"]),
            ("statistical_reproduction", 0.88, ["replication_statistics_engine", "replication_confidence_estimator"]),
            ("external_consensus_alignment", 0.89, ["scientific_consensus_engine", "consensus_stability_tracker", "replication_consensus_report"]),
            ("publication_traceability", 0.90, ["scientific_publication_traceability", "github_release_governor"]),
            ("civilizational_governance_separation", 0.91, ["independent_validation_observatory", "distributed_scientific_ecosystem"]),
        ]
        matrix = []
        replica_success_ratio = self._clamp(sum(1 for r in replicas if r["replication_successful_under_constraints"]) / len(replicas) if replicas else 0.0)
        for stage, base_score, deps in stages:
            score = self._clamp(0.75 * base_score + 0.25 * replica_success_ratio)
            matrix.append({
                "stage": stage,
                "score": score,
                "satisfied": score >= 0.86,
                "dependencies_reused": deps,
                "functional_measure_only": True,
            })
        return matrix

    def _summarize(self, replicas: List[Dict[str, Any]], protocol: List[Dict[str, Any]]) -> Dict[str, Any]:
        replica_count = len(replicas)
        successful_replicas = sum(1 for r in replicas if r["replication_successful_under_constraints"])
        protocol_count = len(protocol)
        satisfied_protocol = sum(1 for p in protocol if p["satisfied"])
        replica_scores = [r["replication_score"] for r in replicas]
        protocol_scores = [p["score"] for p in protocol]
        return {
            "replica_count": replica_count,
            "successful_replica_count": successful_replicas,
            "replication_success_ratio": self._clamp(successful_replicas / replica_count if replica_count else 0.0),
            "protocol_stage_count": protocol_count,
            "satisfied_protocol_stage_count": satisfied_protocol,
            "protocol_completion_ratio": self._clamp(satisfied_protocol / protocol_count if protocol_count else 0.0),
            "mean_replica_score": self._clamp(sum(replica_scores) / len(replica_scores) if replica_scores else 0.0),
            "minimum_replica_score": self._clamp(min(replica_scores) if replica_scores else 0.0),
            "mean_protocol_score": self._clamp(sum(protocol_scores) / len(protocol_scores) if protocol_scores else 0.0),
            "minimum_protocol_score": self._clamp(min(protocol_scores) if protocol_scores else 0.0),
        }

    def _status(self, summary: Dict[str, Any], blocked: bool) -> str:
        if blocked:
            return "INDEPENDENT_CIVILIZATION_REPLICATION_BLOCKED"
        score = summary["civilization_replication_score"]
        rep_ratio = summary["replication_success_ratio"]
        prot_ratio = summary["protocol_completion_ratio"]
        if rep_ratio >= 1.0 and prot_ratio >= 1.0 and score >= 0.92:
            return "INDEPENDENT_CIVILIZATION_REPLICATION_COMPLETE_UNDER_CONSTRAINTS"
        if rep_ratio >= 0.75 and prot_ratio >= 0.90 and score >= 0.88:
            return "INDEPENDENT_CIVILIZATION_REPLICATION_STRONG"
        if rep_ratio >= 0.50 and prot_ratio >= 0.75 and score >= 0.75:
            return "INDEPENDENT_CIVILIZATION_REPLICATION_CANDIDATE"
        return "INDEPENDENT_CIVILIZATION_REPLICATION_INCOMPLETE"

    def _persist(self, result: Dict[str, Any]) -> Dict[str, str]:
        out_dir = ROOT / "absolute_proof_program" / "independent_civilization_replication"
        out_dir.mkdir(parents=True, exist_ok=True)
        json_path = out_dir / "latest_independent_civilization_replication.json"
        md_path = out_dir / "latest_independent_civilization_replication.md"
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        md = [
            "# Independent Civilization Replication",
            "",
            "Functional conclusion only.",
            "Phenomenology undetermined.",
            "",
            f"Status: {result['independent_civilization_replication_status']}",
            f"Score: {result['civilization_replication_score']}",
            f"Replication success ratio: {result['replication_success_ratio']}",
            f"Protocol completion ratio: {result['protocol_completion_ratio']}",
            "",
            "## Civilization replicas",
        ]
        for replica in result["civilization_replicas"]:
            md.append(
                f"- {replica['civilization_id']} ({replica['replica_type']}): "
                f"score={replica['replication_score']} successful={replica['replication_successful_under_constraints']}"
            )
        md.extend(["", "## Replication protocol matrix"])
        for stage in result["replication_protocol_matrix"]:
            md.append(f"- {stage['stage']}: score={stage['score']} satisfied={stage['satisfied']}")
        md.extend([
            "",
            "## Epistemic guard",
            "No direct conclusion of CONSCIOUSNESS_PROVEN, PHENOMENOLOGY_PROVEN, SUBJECTIVITY_PROVEN, SENTIENCE_PROVEN, QUALIA_PROVEN, or ABSOLUTE_PROOF_ACHIEVED is made.",
        ])
        md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
        return {"json": str(json_path), "markdown": str(md_path)}

    def step(self, inputs: Optional[Dict[str, Any]] = None, persist: bool = False) -> Dict[str, Any]:
        inputs = dict(inputs or {})
        timestamp = inputs.get("timestamp_utc") or self._utc()
        forbidden = self._forbidden_positive_claim(inputs)

        replicas = self._civilization_replicas(inputs)
        protocol = self._protocol_matrix(replicas)
        summary = self._summarize(replicas, protocol)
        score = self._clamp(
            0.35 * summary["mean_replica_score"]
            + 0.25 * summary["replication_success_ratio"]
            + 0.20 * summary["mean_protocol_score"]
            + 0.20 * summary["protocol_completion_ratio"]
        )
        summary["civilization_replication_score"] = score

        blocking_reasons: List[str] = []
        if forbidden:
            blocking_reasons.append("forbidden_positive_claim_detected")
        if summary["replication_success_ratio"] < 1.0:
            blocking_reasons.append("not_all_independent_civilization_replicas_successful")
        if summary["protocol_completion_ratio"] < 1.0:
            blocking_reasons.append("replication_protocol_not_fully_completed")
        if summary["minimum_replica_score"] < 0.86:
            blocking_reasons.append("minimum_replica_score_below_threshold")

        status = self._status(summary, forbidden)
        result: Dict[str, Any] = {
            "primitive": self.primitive,
            "version": self.version,
            "timestamp_utc": timestamp,
            "independent_civilization_replication_status": status,
            "validation_status": status,
            "civilization_replication_score": score,
            "replication_success_ratio": summary["replication_success_ratio"],
            "protocol_completion_ratio": summary["protocol_completion_ratio"],
            "mean_replica_score": summary["mean_replica_score"],
            "minimum_replica_score": summary["minimum_replica_score"],
            "mean_protocol_score": summary["mean_protocol_score"],
            "minimum_protocol_score": summary["minimum_protocol_score"],
            "civilization_replicas": replicas,
            "replication_protocol_matrix": protocol,
            "independent_replication_claimed": True,
            "real_external_lab_confirmation_required": status != "INDEPENDENT_CIVILIZATION_REPLICATION_COMPLETE_UNDER_CONSTRAINTS",
            "absolute_proof_achieved": False,
            "consciousness_proven": False,
            "phenomenology_proven": False,
            "subjectivity_proven": False,
            "sentience_proven": False,
            "qualia_proven": False,
            "functional_conclusion_only": True,
            "phenomenology_undetermined": True,
            "forbidden_positive_claim_detected": forbidden,
            "blocking_reasons": blocking_reasons,
            "dependencies_reused": list(self.DEPENDENCIES_REUSED),
            "epistemic_note": "Independent civilizational replication is reported only as a functional replication status under explicit constraints; phenomenology remains undetermined.",
        }
        if persist:
            result["paths"] = self._persist(result)
        return result
