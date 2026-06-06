from pathlib import Path
from statistics import mean
import json

from ontology.distributed_memory_continuity import DistributedMemoryContinuity
from ontology.civilizational_memory import CivilizationalMemory
from ontology.genealogical_continuity import GenealogicalContinuity
from ontology.civilizational_memory_archive import CivilizationalMemoryArchive


class DistributedMemoryReconciliation:

    def __init__(self):
        self.root = Path.home() / "open-cognitive-ecology"
        self.partition_root = self.root / "runtime_experiments" / "a13_real_partition"

    def _load_states(self):
        states = []
        for node in ["alpha", "beta", "gamma"]:
            path = self.partition_root / node / "partition_state.json"
            if path.exists():
                states.append(json.loads(path.read_text(encoding="utf-8")))
        return states

    def step(self):
        states = self._load_states()
        cardinality_factor = round(min(1.0, len(states) / 3.0), 4)

        continuity = DistributedMemoryContinuity().step()

        civilizational = CivilizationalMemory().evaluate({
            "knowledge_retention": 0.95,
            "educational_fidelity": 0.95,
            "cultural_reproduction": 0.95,
            "archival_integrity": 0.95,
        })

        genealogy = GenealogicalContinuity(
            inheritance_fidelity=0.95,
            cumulative_divergence=0.10,
            succession_stability=0.95,
        ).evaluate()

        memory_merge_integrity = round(
            mean([
                continuity["distributed_memory_index"],
                civilizational["civilizational_memory_index"],
                genealogy["lineage_integrity"],
            ]),
            4,
        )

        historical_integrity_preservation = round(
            genealogy["lineage_integrity"],
            4,
        )

        memory_reconciliation_success_rate = round(
            mean([
                memory_merge_integrity,
                historical_integrity_preservation,
            ]),
            4,
        )

        memory_merge_integrity = round(memory_merge_integrity * cardinality_factor, 4)

        memory_reconciliation_success_rate = round(memory_reconciliation_success_rate * cardinality_factor, 4)

        civilizational_reconciliation_index = round(
            mean([
                memory_merge_integrity,
                historical_integrity_preservation,
                memory_reconciliation_success_rate,
            ]),
            4,
        )

        merged_state = {
            "states_merged": len(states),
            "distributed_memory_index": continuity["distributed_memory_index"],
            "distributed_memory_continuity_index": continuity["distributed_memory_continuity_index"],
            "civilizational_memory_index": civilizational["civilizational_memory_index"],
            "lineage_integrity": genealogy["lineage_integrity"],
            "memory_merge_integrity": memory_merge_integrity,
            "historical_integrity_preservation": historical_integrity_preservation,
            "memory_reconciliation_success_rate": memory_reconciliation_success_rate,
            "civilizational_reconciliation_index": round(civilizational_reconciliation_index * cardinality_factor, 4),
            "cardinality_factor": cardinality_factor,
        }

        output = self.partition_root / "merged_civilizational_state.json"
        output.write_text(
            json.dumps(merged_state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        try:
            CivilizationalMemoryArchive().archive(
                category="a13_memory_reconciliation_v2",
                payload=merged_state,
            )
        except Exception:
            pass

        return merged_state