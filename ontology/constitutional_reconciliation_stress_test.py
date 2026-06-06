from pathlib import Path
from statistics import mean
import json

from ontology.distributed_reflexive_civilizational_identity import (
    DistributedReflexiveCivilizationalIdentity,
)
from ontology.transgenerational_constitutional_continuity import (
    TransgenerationalConstitutionalContinuity,
)
from ontology.open_constitutional_transmission import (
    OpenConstitutionalTransmission,
)
from ontology.constitutional_governance_supervisor import (
    ConstitutionalGovernanceSupervisor,
)

class ConstitutionalReconciliationStressTest:

    def __init__(self):
        self.root = Path.home() / "open-cognitive-ecology"
        self.partition_root = (
            self.root / "runtime_experiments" / "a13_real_partition"
        )

    def _load_states(self):
        states = []
        for node in ["alpha", "beta", "gamma"]:
            p = self.partition_root / node / "partition_state.json"
            if p.exists():
                states.append(json.loads(p.read_text(encoding="utf-8")))
        return states

    def _load_metrics(self):
        p = self.partition_root / "real_state_metrics_report.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return {}

    def step(self):

        states = self._load_states()
        metrics = self._load_metrics()
        cardinality_factor = round(min(1.0, len(states) / 3.0), 4)

        future_openness = metrics.get("future_openness", 0.95)
        identity_coherence = metrics.get(
            "distributed_identity_coherence", 0.92
        )
        historical_divergence = metrics.get(
            "historical_divergence", 0.90
        )
        runtime_index = metrics.get(
            "distributed_population_runtime_index", 0.95
        )

        identity = DistributedReflexiveCivilizationalIdentity().step({
            "pluralistic_stability": identity_coherence,
            "historical_mutation": historical_divergence,
            "distributed_openness": identity_coherence,
            "genealogical_continuity": identity_coherence,
            "identity_fragmentation": 0.10,
            "convergence_pressure": 0.10,
            "future_openness": future_openness,
        })

        continuity = TransgenerationalConstitutionalContinuity().step({
            "genealogical_responsibility": runtime_index,
            "symbolic_transition": identity_coherence,
            "adaptive_forgetting": historical_divergence,
            "semantic_pluralism": identity_coherence,
            "constitutional_memory_openness": future_openness,
            "meta_revision_capacity": identity_coherence,
            "historical_rigidity": 0.10,
            "civilizational_fragmentation": 0.10,
        })

        transmission = OpenConstitutionalTransmission().step({
            "constitutional_continuity": runtime_index,
            "revision_capacity": identity_coherence,
            "divergence_preservation": historical_divergence,
            "anti_dogmatism": future_openness,
            "distributed_propagation": runtime_index,
            "future_openness": future_openness,
            "normative_rigidity": 0.10,
        })

        governance = ConstitutionalGovernanceSupervisor().step()

        constitutional_reconciliation_index = round(
            mean([
                identity["open_reflexive_continuity_index"],
                continuity["open_transgenerational_continuity_index"],
                transmission["constitutional_transmission_viability"],
                governance["constitutional_governance_score"],
            ]),
            4,
        )

        constitutional_reconciliation_index = round(constitutional_reconciliation_index * cardinality_factor, 4)

        result = {
            "states_merged": len(states),
            "cardinality_factor": cardinality_factor,
            "constitutional_reconciliation_index":
                constitutional_reconciliation_index,
            "open_reflexive_continuity_index":
                identity["open_reflexive_continuity_index"],
            "open_transgenerational_continuity_index":
                continuity["open_transgenerational_continuity_index"],
            "constitutional_transmission_viability":
                transmission["constitutional_transmission_viability"],
            "constitutional_governance_score":
                governance["constitutional_governance_score"],
            "constitutional_stress_test_passed":
                constitutional_reconciliation_index >= 0.80,
        }

        report = (
            self.partition_root
            / "constitutional_reconciliation_report.json"
        )

        report.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return result