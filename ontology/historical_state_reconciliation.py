from pathlib import Path
from statistics import mean
import json
from ontology.real_multi_machine_historical_divergence import RealMultiMachineHistoricalDivergence

class HistoricalStateReconciliation:
    def __init__(self):
        self.root = Path.home() / "open-cognitive-ecology"
        self.partition_root = self.root / "runtime_experiments" / "a13_real_partition"

    def _load_states(self):
        states = []
        for node in ["alpha","beta","gamma"]:
            path = self.partition_root / node / "partition_state.json"
            if path.exists():
                states.append(json.loads(path.read_text(encoding="utf-8")))
        return states

    def _load_real_metrics(self):
        path = self.partition_root / "real_state_metrics_report.json"
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        return {}

    def step(self):
        states = self._load_states()
        metrics = self._load_real_metrics()
        cardinality_factor = round(min(1.0, len(states) / 3.0), 4)

        state = {
            "historical_branch_diversity": min(1.0, 0.70 + (len(states) * 0.05)),
            "semantic_drift_capacity": metrics.get("semantic_drift_capacity", 0.90),
            "interoperability": metrics.get("interoperability", 0.95),
            "irreversibility": 0.90,
            "historical_openness": metrics.get("historical_openness", 0.95),
            "convergence_pressure": 0.10,
            "distributed_viability": metrics.get("distributed_population_runtime_index", 0.95),
        }

        divergence = RealMultiMachineHistoricalDivergence().evaluate(state)

        historical_alignment_score = round(mean([
            divergence["open_historical_viability"],
            divergence["multi_history_balance"],
        ]), 4)

        historical_reconciliation_index = round(mean([
            divergence["real_multi_machine_historical_divergence_index"],
            historical_alignment_score,
        ]), 4)

        civilizational_reconciliation_index = round(mean([
            historical_reconciliation_index,
            divergence["open_historical_viability"],
            divergence["multi_history_balance"],
        ]), 4)

        historical_reconciliation_index = round(historical_reconciliation_index * cardinality_factor, 4)
        civilizational_reconciliation_index = round(civilizational_reconciliation_index * cardinality_factor, 4)

        result = {
            "states_merged": len(states),
            "historical_alignment_score": historical_alignment_score,
            "historical_reconciliation_index": historical_reconciliation_index,
            "real_multi_machine_historical_divergence_index": divergence["real_multi_machine_historical_divergence_index"],
            "classification": divergence["classification"],
            "cardinality_factor": cardinality_factor,
            "civilizational_reconciliation_index": civilizational_reconciliation_index,
        }

        report = self.partition_root / "historical_reconciliation_report.json"
        report.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        return result
