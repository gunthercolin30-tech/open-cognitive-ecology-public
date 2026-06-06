from pathlib import Path
from statistics import mean
import json

EXPECTED_STATES = 3

class RealStateMetricsExtraction:

    def __init__(self):
        self.root = Path.home() / "open-cognitive-ecology"
        self.partition_root = self.root / "runtime_experiments" / "a13_real_partition"

    def _load_states(self):
        states = []
        for node in ["alpha","beta","gamma"]:
            p = self.partition_root / node / "partition_state.json"
            if p.exists():
                states.append(json.loads(p.read_text(encoding="utf-8")))
        return states

    def step(self):
        states = self._load_states()
        cardinality_factor = len(states) / EXPECTED_STATES if EXPECTED_STATES else 1.0

        identity = []
        runtime = []
        divergence = []

        for state in states:
            payload = state.get("state", {})
            identity.append(payload.get("identity", {}).get("distributed_identity_coherence", 0.0))
            runtime.append(payload.get("population", {}).get("distributed_population_runtime_index", 0.0))
            divergence.append(payload.get("population", {}).get("historical_divergence", 0.0))

        report = {
            "states_loaded": len(states),
            "cardinality_factor": round(cardinality_factor,4),
            "distributed_identity_coherence": round(mean(identity),4) * cardinality_factor if identity else 0.0,
            "distributed_population_runtime_index": round(mean(runtime),4) * cardinality_factor if runtime else 0.0,
            "historical_divergence": round(mean(divergence),4) * cardinality_factor if divergence else 0.0,
        }

        out = self.partition_root / "real_state_metrics_report.json"
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report