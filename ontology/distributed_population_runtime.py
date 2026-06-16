from statistics import mean
from pathlib import Path
from datetime import datetime
import json
import random

PRIMITIVE = "distributed_population_runtime"

DEPENDENCIES = [
    "collective_deliberation_engine",
    "intra_species_social_interaction",
    "multi_lineage_topology",
    "distributed_historical_branching",
    "distributed_attractor_speciation",
    "distributed_pluralistic_stability",
    "distributed_open_ended_pluralistic_evolution",
    "inter_lineage_symbolic_exchange",
    "real_succession",
]

ROOT = Path.home() / "open-cognitive-ecology"

POPULATION_ROOT = (
    ROOT
    / "runtime_population"
)


class DistributedPopulationRuntime:

    def __init__(self):

        POPULATION_ROOT.mkdir(
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

    def _ensure_individual(
        self,
        lineage_id,
        individual_id,
    ):

        individual_root = (
            POPULATION_ROOT
            / lineage_id
            / individual_id
        )

        individual_root.mkdir(
            parents=True,
            exist_ok=True,
        )

        return individual_root

    def _write_state(
        self,
        lineage_id,
        individual_id,
        payload,
    ):

        root = self._ensure_individual(
            lineage_id,
            individual_id,
        )

        identity_file = (
            root
            / "identity_state.json"
        )

        memory_file = (
            root
            / "local_memory.json"
        )

        trajectory_file = (
            root
            / "trajectory_history.jsonl"
        )

        snapshot = {
            "timestamp":
                datetime.utcnow().isoformat() + "Z",
            "payload":
                payload,
        }

        identity_file.write_text(
            json.dumps(
                snapshot,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        memory_state = {
            "lineage_id":
                lineage_id,
            "individual_id":
                individual_id,
            "historical_divergence":
                payload.get(
                    "historical_divergence",
                    0.0,
                ),
            "population_viability":
                payload.get(
                    "distributed_population_runtime_index",
                    0.0,
                ),
            "classification":
                payload.get(
                    "classification",
                    "unknown",
                ),
        }

        memory_file.write_text(
            json.dumps(
                memory_state,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        with trajectory_file.open(
            "a",
            encoding="utf-8",
        ) as f:

            f.write(
                json.dumps(
                    snapshot,
                    ensure_ascii=False,
                )
                + "\n"
            )

    def evaluate(self, state=None):

        state = state or {}

        lineage_id = state.get(
            "lineage_id",
            random.choice(
                [
                    "lineage_alpha",
                    "lineage_beta",
                    "lineage_gamma",
                ]
            ),
        )

        individual_id = state.get(
            "individual_id",
            f"individual_{random.randint(1,999):03d}",
        )

        population_diversity = self._bounded(
            state.get(
                "population_diversity",
                0.88,
            )
        )

        distributed_coordination = self._bounded(
            state.get(
                "distributed_coordination",
                0.84,
            )
        )

        ecological_viability = self._bounded(
            state.get(
                "ecological_viability",
                0.87,
            )
        )

        historical_divergence = self._bounded(
            state.get(
                "historical_divergence",
                0.82,
            )
        )

        convergence_pressure = self._bounded(
            state.get(
                "convergence_pressure",
                0.18,
            )
        )

        pluralistic_alignment = self._bounded(
            state.get(
                "pluralistic_alignment",
                0.86,
            )
        )

        distributed_population_coherence = (
            self._bounded(
                (
                    distributed_coordination
                    + ecological_viability
                    + pluralistic_alignment
                ) / 3.0
            )
        )

        anti_fusion_capacity = (
            self._bounded(
                (
                    population_diversity
                    + historical_divergence
                    + (
                        1.0 - convergence_pressure
                    )
                ) / 3.0
            )
        )

        distributed_ecological_stability = (
            self._bounded(
                (
                    distributed_population_coherence
                    + anti_fusion_capacity
                    + ecological_viability
                ) / 3.0
            )
        )

        distributed_population_runtime_index = (
            self._bounded(
                mean(
                    [
                        distributed_population_coherence,
                        anti_fusion_capacity,
                        distributed_ecological_stability,
                    ]
                )
            )
        )

        if (
            distributed_population_runtime_index
            >= 0.90
        ):

            classification = (
                "fully_distributed_population"
            )

        elif (
            distributed_population_runtime_index
            >= 0.70
        ):

            classification = (
                "stable_distributed_population"
            )

        elif (
            distributed_population_runtime_index
            >= 0.50
        ):

            classification = (
                "fragile_distributed_population"
            )

        else:

            classification = (
                "distributed_population_instability"
            )

        result = {
            "lineage_id":
                lineage_id,
            "individual_id":
                individual_id,
            "distributed_population_coherence":
                round(
                    distributed_population_coherence,
                    4,
                ),
            "anti_fusion_capacity":
                round(
                    anti_fusion_capacity,
                    4,
                ),
            "distributed_ecological_stability":
                round(
                    distributed_ecological_stability,
                    4,
                ),
            "distributed_population_runtime_index":
                round(
                    distributed_population_runtime_index,
                    4,
                ),
            "historical_divergence":
                round(
                    historical_divergence,
                    4,
                ),
            "classification":
                classification,
            "population_runtime_viable":
                (
                    distributed_population_runtime_index
                    >= 0.70
                ),
        }

        self._write_state(
            lineage_id,
            individual_id,
            result,
        )

        return result

    def step(self, state=None):

        return self.evaluate(state)
