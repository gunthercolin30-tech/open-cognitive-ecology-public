from pathlib import Path
from statistics import mean
import json

from ontology.distributed_memory_reconciliation import (
    DistributedMemoryReconciliation,
)
from ontology.historical_state_reconciliation import (
    HistoricalStateReconciliation,
)
from ontology.constitutional_reconciliation_stress_test import (
    ConstitutionalReconciliationStressTest,
)
from ontology.longitudinal_recovery_observer import (
    LongitudinalRecoveryObserver,
)


class LongitudinalReconciliation:

    def __init__(self):
        self.root = Path.home() / "open-cognitive-ecology"
        self.partition_root = (
            self.root / "runtime_experiments" / "a13_real_partition"
        )

    def step(self, cycles=10):

        runs = []

        memory_engine = DistributedMemoryReconciliation()
        historical_engine = HistoricalStateReconciliation()
        constitutional_engine = (
            ConstitutionalReconciliationStressTest()
        )

        for _ in range(max(1, int(cycles))):

            memory = memory_engine.step()
            historical = historical_engine.step()
            constitutional = constitutional_engine.step()

            runs.append(
                {
                    "recovery_resilience_index": mean([
                        memory["memory_reconciliation_success_rate"],
                        historical["historical_reconciliation_index"],
                        constitutional["constitutional_reconciliation_index"],
                    ]),
                    "ecological_recovery_coherence": mean([
                        memory["civilizational_reconciliation_index"],
                        historical["civilizational_reconciliation_index"],
                        constitutional["constitutional_reconciliation_index"],
                    ]),
                    "collapse_frequency": 0.0,
                }
            )

        observer = LongitudinalRecoveryObserver()

        longitudinal = observer.step(runs)

        result = {
            "cycle_count": cycles,
            "longitudinal_recovery_index":
                longitudinal["longitudinal_recovery_index"],
            "recovery_drift":
                longitudinal["recovery_drift"],
            "recovery_stability":
                longitudinal["recovery_stability"],
            "ecological_recovery_continuity":
                longitudinal["ecological_recovery_continuity"],
            "civilizational_continuity":
                longitudinal["ecological_recovery_continuity"],
            "longitudinal_reconciliation_stability":
                longitudinal["recovery_stability"],
            "cumulative_reconciliation_drift":
                longitudinal["recovery_drift"],
            "recovery_class":
                longitudinal["recovery_class"],
        }

        report = (
            self.partition_root
            / "longitudinal_reconciliation_report.json"
        )

        report.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return result