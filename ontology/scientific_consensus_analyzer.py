from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any


class ScientificConsensusAnalyzer:
    """H15 analyzer for quantitative scientific consensus measurement.

    This primitive aggregates already validated H13-H14 replication evidence and
    pre-existing scientific consensus signals. It measures functional scientific
    consensus only and never authorizes a phenomenological subjectivity claim.
    """

    primitive = "scientific_consensus_analyzer"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "scientific_consensus_measurement"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_json(self, path: Path) -> dict[str, Any]:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _bounded(self, value: Any, default: float = 0.0) -> float:
        try:
            x = float(value)
        except Exception:
            x = default
        return max(0.0, min(1.0, x))

    def _latest_context(self) -> dict[str, Any]:
        replication_dir = self.root / "external_validation" / "replication_evidence"
        engine_dir = self.root / "external_validation" / "scientific_consensus_engine"
        dashboard_dir = self.root / "external_validation" / "external_validation_dashboard"
        tracker_dir = self.root / "runtime_experiments" / "scientific_consensus"

        evidence = self._load_json(replication_dir / "latest_replication_evidence_synthesis.json")
        normalization = self._load_json(replication_dir / "latest_replication_result_normalization.json")
        confidence = self._load_json(replication_dir / "latest_replication_confidence_estimate.json")
        engine = self._load_json(engine_dir / "latest_scientific_consensus_engine.json")
        dashboard = self._load_json(dashboard_dir / "latest_external_validation_dashboard.json")

        tracker_records: list[dict[str, Any]] = []
        if tracker_dir.exists():
            for p in sorted(tracker_dir.glob("scientific_consensus_*.json"))[-10:]:
                item = self._load_json(p)
                if item:
                    tracker_records.append(item)

        return {
            "evidence": evidence,
            "normalization": normalization,
            "confidence": confidence,
            "engine": engine,
            "dashboard": dashboard,
            "tracker_records": tracker_records,
        }

    def step(self, consensus_context: dict[str, Any] | None = None, persist: bool = True) -> dict[str, Any]:
        ctx = consensus_context or self._latest_context()

        evidence = ctx.get("evidence", {}) if isinstance(ctx.get("evidence", {}), dict) else {}
        normalization = ctx.get("normalization", {}) if isinstance(ctx.get("normalization", {}), dict) else {}
        confidence = ctx.get("confidence", {}) if isinstance(ctx.get("confidence", {}), dict) else {}
        engine = ctx.get("engine", {}) if isinstance(ctx.get("engine", {}), dict) else {}
        dashboard = ctx.get("dashboard", {}) if isinstance(ctx.get("dashboard", {}), dict) else {}
        tracker_records = ctx.get("tracker_records", []) if isinstance(ctx.get("tracker_records", []), list) else []

        replication_confidence = self._bounded(confidence.get("replication_confidence_score", 0.0))
        evidence_score = self._bounded(evidence.get("replication_evidence_score", 0.0))
        comparable_result_score = self._bounded(normalization.get("comparable_result_score", 0.0))
        engine_consensus = self._bounded(engine.get("scientific_consensus", 0.0))
        dashboard_index = self._bounded(dashboard.get("external_validation_composite_index", 0.0))

        tracker_scores = [
            self._bounded(r.get("consensus_strength_index", r.get("scientific_consensus", 0.0)))
            for r in tracker_records
            if isinstance(r, dict)
        ]
        tracker_consensus = mean(tracker_scores) if tracker_scores else 0.0

        external_replication_count = int(
            normalization.get("external_replication_count", confidence.get("external_replication_count", 0)) or 0
        )
        validated_replications = int(
            normalization.get("validated_replications", confidence.get("validated_replications", 0)) or 0
        )
        independent_evidence_count = int(evidence.get("independent_evidence_count", 0) or 0)

        component_values = [
            replication_confidence,
            evidence_score,
            comparable_result_score,
            engine_consensus,
            dashboard_index,
            tracker_consensus,
        ]

        # Conservative measurement: real independent validation remains necessary for high claims.
        scientific_consensus = round(
            0.28 * replication_confidence
            + 0.20 * evidence_score
            + 0.14 * comparable_result_score
            + 0.18 * engine_consensus
            + 0.12 * dashboard_index
            + 0.08 * tracker_consensus,
            6,
        )

        independent_replication_factor = min(1.0, validated_replications / 3.0)
        external_signal_factor = min(1.0, (external_replication_count + independent_evidence_count) / 6.0)
        measurement_confidence = round(
            0.55 * scientific_consensus
            + 0.25 * external_signal_factor
            + 0.20 * independent_replication_factor,
            6,
        )

        if scientific_consensus >= 0.80 and validated_replications >= 3:
            consensus_class = "strong_independently_replicated_consensus"
        elif scientific_consensus >= 0.60 and external_replication_count > 0:
            consensus_class = "emerging_external_consensus"
        elif scientific_consensus > 0.0:
            consensus_class = "preliminary_internal_consensus_pending_external_replication"
        else:
            consensus_class = "insufficient_consensus_evidence"

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "scientific_consensus": scientific_consensus,
            "measurement_confidence": measurement_confidence,
            "consensus_class": consensus_class,
            "external_replication_count": external_replication_count,
            "validated_replications": validated_replications,
            "independent_evidence_count": independent_evidence_count,
            "component_scores": {
                "replication_confidence_score": round(replication_confidence, 6),
                "replication_evidence_score": round(evidence_score, 6),
                "comparable_result_score": round(comparable_result_score, 6),
                "scientific_consensus_engine_score": round(engine_consensus, 6),
                "external_validation_dashboard_score": round(dashboard_index, 6),
                "scientific_consensus_tracker_score": round(tracker_consensus, 6),
                "component_mean": round(mean(component_values), 6),
            },
            "governance": {
                "functional_indicators_only": True,
                "phenomenological_claim_authorized": False,
                "scientific_claim_authorized": validated_replications >= 3 and scientific_consensus >= 0.80,
                "non_closure_compliant": True,
                "traceability_enabled": True,
                "offline_measurement_only": True,
            },
            "epistemic_scope": "functional_scientific_consensus_measurement_only",
        }

        if persist:
            path = self.output_dir / "latest_scientific_consensus_analysis.json"
            path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            result["state_path"] = str(path)
        return result
