from pathlib import Path
import json

from ontology.constitutional_dashboard_integration import (
    ConstitutionalDashboardIntegration,
)
from ontology.constitutional_longitudinal_observatory import (
    ConstitutionalLongitudinalObservatory,
)
from ontology.constitutional_evolution_gate import (
    ConstitutionalEvolutionGate,
)
from ontology.constitutional_self_modification_protocol import (
    ConstitutionalSelfModificationProtocol,
)


class ConstitutionalGovernanceSupervisor:

    def __init__(self):
        self.root = Path.home() / "open-cognitive-ecology"
        self.partition_root = (
            self.root / "runtime_experiments" / "a13_real_partition"
        )

    def _load_metrics(self):
        p = self.partition_root / "real_state_metrics_report.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return {}

    def _load_historical(self):
        p = self.partition_root / "historical_reconciliation_report.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return {}

    def _load_constitutional(self):
        p = self.partition_root / "constitutional_reconciliation_report.json"
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
        return {}

    def step(
        self,
        dashboard_result=None,
        observatory_result=None,
        gate_result=None,
        protocol_result=None,
    ):

        metrics = self._load_metrics()
        historical = self._load_historical()
        constitutional = self._load_constitutional()

        dashboard = ConstitutionalDashboardIntegration().step(
            integrity_result={
                "constitutional_integrity_index":
                    constitutional.get(
                        "constitutional_reconciliation_index",
                        0.90,
                    )
            },
            benchmark_result={
                "constitutional_benchmark_score":
                    metrics.get(
                        "distributed_identity_coherence",
                        0.90,
                    )
            },
            runtime_result={
                "constitutional_compliance_score":
                    metrics.get(
                        "distributed_population_runtime_index",
                        0.90,
                    )
            },
            stress_result={
                "stress_resilience_score":
                    historical.get(
                        "historical_reconciliation_index",
                        0.90,
                    )
            },
        )

        observatory = ConstitutionalLongitudinalObservatory().step(
            dashboard_result=dashboard,
            consciousness_result={
                "unified_consciousness_composite_index":
                    metrics.get(
                        "future_openness",
                        0.90,
                    )
            },
        )

        gate = ConstitutionalEvolutionGate().step(
            observatory_result=observatory,
            runtime_result={
                "constitutional_compliance_score":
                    metrics.get(
                        "distributed_population_runtime_index",
                        0.90,
                    )
            },
        )

        protocol = ConstitutionalSelfModificationProtocol().step(
            gate_result=gate,
            mutation_descriptor={
                "source": "A13-R.4"
            },
        )

        states_merged = max(1, len([p for p in ["alpha","beta","gamma"] if (self.partition_root / p / "partition_state.json").exists()]))
        cardinality_factor = round(min(1.0, states_merged / 3.0), 4)

        governance_score = (
            dashboard[
                "constitutional_dashboard_composite_score"
            ]
            + observatory[
                "constitutional_consciousness_coupling"
            ]
            + gate[
                "evolutionary_confidence_score"
            ]
            + (
                1.0
                if protocol["mutation_recorded"]
                else 0.8
            )
        ) / 4.0

        governance_score *= cardinality_factor

        if governance_score >= 0.95:
            verdict = "Constitutionally Exemplary"
        elif governance_score >= 0.90:
            verdict = "Constitutionally Robust"
        elif governance_score >= 0.80:
            verdict = "Constitutionally Stable"
        elif governance_score >= 0.70:
            verdict = "Constitutionally Fragile"
        else:
            verdict = "Constitutionally Non-Compliant"

        return {
            "primitive":
                "CONSTITUTIONAL_GOVERNANCE_SUPERVISOR",
            "constitutional_governance_score":
                round(governance_score, 4),
            "cardinality_factor": cardinality_factor,
            "governance_verdict":
                verdict,
            "mutation_authorized":
                gate["mutation_authorized"],
            "system_constitutionally_viable":
                governance_score >= 0.80,
            "diagnostics": {
                "dashboard":
                    dashboard,
                "observatory":
                    observatory,
                "gate":
                    gate,
                "protocol":
                    protocol,
            },
        }
