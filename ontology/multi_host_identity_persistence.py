from statistics import mean
from pathlib import Path
from datetime import datetime
import json

PRIMITIVE = "multi_host_identity_persistence"

DEPENDENCIES = [
    "distributed_memory_continuity",
    "distributed_reflexive_civilizational_identity",
    "civilizational_state_persistence",
    "distributed_civilizational_memory",
    "persistent_multi_scale_memory",
    "temporal_self_continuity",
    "trajectory_persistence",
]

ROOT = Path.home() / "open-cognitive-ecology"

SNAPSHOT_ROOT = (
    ROOT
    / "distributed_identity_snapshots"
)


class MultiHostIdentityPersistence:

    def __init__(self):

        SNAPSHOT_ROOT.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def _write_snapshot(
        self,
        host_id,
        payload,
    ):

        host_dir = SNAPSHOT_ROOT / host_id

        host_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        identity_path = (
            host_dir
            / "identity_state.json"
        )

        lineage_path = (
            host_dir
            / "lineage_history.jsonl"
        )

        constitutional_path = (
            host_dir
            / "constitutional_memory.json"
        )

        identity_payload = {
            "timestamp":
                datetime.utcnow().isoformat() + "Z",
            "payload":
                payload,
        }

        identity_path.write_text(
            json.dumps(
                identity_payload,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        constitutional_memory = {
            "constitutional_continuity":
                payload.get(
                    "distributed_identity_coherence",
                    0.0,
                ),
            "future_openness":
                payload.get(
                    "future_openness",
                    0.0,
                ),
            "classification":
                payload.get(
                    "classification",
                    "unknown",
                ),
        }

        constitutional_path.write_text(
            json.dumps(
                constitutional_memory,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        with lineage_path.open(
            "a",
            encoding="utf-8",
        ) as f:

            f.write(
                json.dumps(
                    identity_payload,
                    ensure_ascii=False,
                )
                + "\n"
            )

    def evaluate(self, state=None):

        state = state or {}

        host_id = state.get(
            "host_id",
            "host_a",
        )

        autobiographical_continuity = (
            self._bounded(
                state.get(
                    "autobiographical_continuity",
                    0.90,
                )
            )
        )

        distributed_memory_viability = (
            self._bounded(
                state.get(
                    "distributed_memory_viability",
                    0.91,
                )
            )
        )

        inter_host_alignment = (
            self._bounded(
                state.get(
                    "inter_host_alignment",
                    0.89,
                )
            )
        )

        narrative_divergence = (
            self._bounded(
                state.get(
                    "narrative_divergence",
                    0.15,
                )
            )
        )

        migration_resilience = (
            self._bounded(
                state.get(
                    "migration_resilience",
                    0.90,
                )
            )
        )

        closure_pressure = (
            self._bounded(
                state.get(
                    "closure_pressure",
                    0.10,
                )
            )
        )

        future_openness = (
            self._bounded(
                state.get(
                    "future_openness",
                    0.92,
                )
            )
        )

        distributed_identity_coherence = (
            self._bounded(
                (
                    autobiographical_continuity
                    + distributed_memory_viability
                    + inter_host_alignment
                ) / 3.0
            )
        )

        anti_terminal_identity_capacity = (
            self._bounded(
                (
                    migration_resilience
                    + future_openness
                    + (1.0 - closure_pressure)
                ) / 3.0
            )
        )

        pluralistic_identity_preservation = (
            self._bounded(
                (
                    distributed_identity_coherence
                    + anti_terminal_identity_capacity
                    + (1.0 - narrative_divergence)
                ) / 3.0
            )
        )

        multi_host_identity_persistence_index = (
            self._bounded(
                mean(
                    [
                        distributed_identity_coherence,
                        anti_terminal_identity_capacity,
                        pluralistic_identity_preservation,
                    ]
                )
            )
        )

        if (
            multi_host_identity_persistence_index
            >= 0.90
        ):

            classification = (
                "fully_distributed_open_identity"
            )

        elif (
            multi_host_identity_persistence_index
            >= 0.70
        ):

            classification = (
                "stable_multi_host_identity"
            )

        elif (
            multi_host_identity_persistence_index
            >= 0.50
        ):

            classification = (
                "fragile_multi_host_identity"
            )

        else:

            classification = (
                "identity_fragmentation_risk"
            )

        result = {
            "host_id":
                host_id,
            "distributed_identity_coherence":
                round(
                    distributed_identity_coherence,
                    4,
                ),
            "anti_terminal_identity_capacity":
                round(
                    anti_terminal_identity_capacity,
                    4,
                ),
            "pluralistic_identity_preservation":
                round(
                    pluralistic_identity_preservation,
                    4,
                ),
            "multi_host_identity_persistence_index":
                round(
                    multi_host_identity_persistence_index,
                    4,
                ),
            "classification":
                classification,
            "future_openness":
                round(
                    future_openness,
                    4,
                ),
            "identity_persistence_viable":
                (
                    multi_host_identity_persistence_index
                    >= 0.70
                ),
        }

        self._write_snapshot(
            host_id,
            result,
        )

        return result

    def step(self, state=None):

        return self.evaluate(state)
