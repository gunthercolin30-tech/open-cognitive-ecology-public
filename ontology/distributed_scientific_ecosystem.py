
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

from ontology.autonomous_external_collaboration_network import AutonomousExternalCollaborationNetwork
from ontology.persistent_replication_network import PersistentReplicationNetwork


class DistributedScientificEcosystem:
    primitive = "distributed_scientific_ecosystem"

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path.home() / "open-cognitive-ecology"
        self.output_dir = self.root / "external_validation" / "distributed_scientific_ecosystem"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path: Path) -> dict[str, Any]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def step(self, persist: bool = True) -> dict[str, Any]:
        collaboration = AutonomousExternalCollaborationNetwork(self.root).step(persist=persist)
        replication = PersistentReplicationNetwork(self.root).step(persist=persist)

        certification = self._read_json(
            self.root / "external_validation" / "civilizational_scientific_certification" / "latest_civilizational_scientific_certification.json"
        )
        observatory = self._read_json(
            self.root / "external_validation" / "independent_validation_observatory" / "latest_independent_validation_observatory.json"
        )

        certification_readiness = float(certification.get("certification_readiness", 0.0) or 0.0)
        certification_confidence = float(certification.get("certification_confidence", 0.0) or 0.0)
        validation_stability_index = float(observatory.get("validation_stability_index", 0.0) or 0.0)
        external_replication_count = max(
            int(collaboration.get("external_replication_count", 0) or 0),
            int(replication.get("external_replication_count", 0) or 0),
            int(observatory.get("external_replication_count", 0) or 0),
        )

        external_collaboration_density = float(collaboration.get("external_collaboration_density", 0.0) or 0.0)
        distributed_scientific_activity = mean([
            float(collaboration.get("distributed_scientific_activity", 0.0) or 0.0),
            min(1.0, float(replication.get("replication_link_count", 0) or 0) / 50.0),
            min(1.0, external_replication_count / 3.0),
        ])
        ecosystem_resilience_index = mean([
            float(replication.get("network_resilience_index", 0.0) or 0.0),
            validation_stability_index,
            certification_readiness,
            1.0 if external_replication_count > 0 else 0.5,
        ])
        ecosystem_maturity = mean([
            external_collaboration_density,
            distributed_scientific_activity,
            ecosystem_resilience_index,
            certification_confidence,
        ])

        result = {
            "primitive": self.primitive,
            "success": True,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "stage": "H20",
            "distributed_scientific_ecosystem_ready": True,
            "external_collaboration_density": round(external_collaboration_density, 6),
            "distributed_scientific_activity": round(distributed_scientific_activity, 6),
            "ecosystem_resilience_index": round(ecosystem_resilience_index, 6),
            "ecosystem_maturity": round(ecosystem_maturity, 6),
            "external_replication_count": external_replication_count,
            "certification_readiness": round(certification_readiness, 6),
            "certification_confidence": round(certification_confidence, 6),
            "validation_stability_index": round(validation_stability_index, 6),
            "ecosystem_status": "distributed_scientific_ecosystem_operational" if ecosystem_maturity >= 0.5 else "distributed_scientific_ecosystem_emerging",
            "phenomenological_claim_authorized": False,
            "epistemic_scope": "functional_indicators_only",
            "collaboration_state_path": collaboration.get("state_path"),
            "replication_state_path": replication.get("state_path"),
            "diagnostics": {
                "non_closure_compliant": True,
                "open_scientific_governance": True,
                "requires_continued_independent_replication": external_replication_count <= 1,
                "h20_role": "stabilize_distributed_scientific_ecosystem_without_claiming_phenomenology",
            },
        }

        if persist:
            state_path = self.output_dir / "latest_distributed_scientific_ecosystem.json"
            state_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
            history_path = self.output_dir / "distributed_scientific_ecosystem.jsonl"
            with history_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            result["state_path"] = str(state_path)
            result["history_path"] = str(history_path)

        return result
