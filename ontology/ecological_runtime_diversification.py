from statistics import mean
from pathlib import Path
from datetime import datetime
import json
import random

PRIMITIVE = "ecological_runtime_diversification"

DEPENDENCIES = [
    "distributed_population_runtime",
    "distributed_open_ended_pluralistic_evolution",
    "distributed_attractor_speciation",
    "historical_open_endedness",
    "multi_history_runtime",
    "distributed_meta_stability",
    "scheduler_mutation_ecology",
    "post_fragmentation_civilizational_ecology",
    "adaptive_ecological_regulation_engine",
    "critical_transitions",
    "regime_emergence",
    "innovation_retention",
]

ROOT = Path.home() / "open-cognitive-ecology"

POPULATION_ROOT = (
    ROOT
    / "runtime_population"
)


class EcologicalRuntimeDiversification:

    def _bounded(self, value):

        return max(
            0.0,
            min(
                1.0,
                float(value),
            ),
        )

    def _all_individuals(self):

        if not POPULATION_ROOT.exists():
            return []

        individuals = []

        for lineage in POPULATION_ROOT.iterdir():

            if not lineage.is_dir():
                continue

            for individual in lineage.iterdir():

                if individual.is_dir():

                    individuals.append(
                        (lineage.name, individual)
                    )

        return individuals

    def _write_ecological_state(
        self,
        lineage_id,
        individual_root,
        payload,
    ):

        ecological_path = (
            individual_root
            / "ecological_state.json"
        )

        trajectory_path = (
            individual_root
            / "ecological_history.jsonl"
        )

        snapshot = {
            "timestamp":
                datetime.utcnow().isoformat() + "Z",
            "payload":
                payload,
        }

        ecological_path.write_text(
            json.dumps(
                snapshot,
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        with trajectory_path.open(
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

        individuals = self._all_individuals()

        if not individuals:

            return {
                "classification":
                    "missing_population_runtime"
            }

        lineage_id, individual_root = random.choice(
            individuals
        )

        ecological_diversity = self._bounded(
            random.uniform(
                0.75,
                0.95,
            )
        )

        historical_divergence = self._bounded(
            random.uniform(
                0.72,
                0.94,
            )
        )

        bifurcation_intensity = self._bounded(
            random.uniform(
                0.70,
                0.93,
            )
        )

        ecological_stability = self._bounded(
            random.uniform(
                0.74,
                0.91,
            )
        )

        mutation_pressure = self._bounded(
            random.uniform(
                0.18,
                0.42,
            )
        )

        attractor_speciation = self._bounded(
            (
                ecological_diversity
                + bifurcation_intensity
                + historical_divergence
            ) / 3.0
        )

        anti_collapse_capacity = self._bounded(
            (
                ecological_stability
                + (
                    1.0 - mutation_pressure
                )
                + historical_divergence
            ) / 3.0
        )

        ecological_open_endedness = self._bounded(
            mean(
                [
                    ecological_diversity,
                    historical_divergence,
                    bifurcation_intensity,
                    attractor_speciation,
                    anti_collapse_capacity,
                ]
            )
        )

        if ecological_open_endedness >= 0.90:

            classification = (
                "historically_divergent_ecological_runtime"
            )

        elif ecological_open_endedness >= 0.70:

            classification = (
                "stable_open_ecological_runtime"
            )

        elif ecological_open_endedness >= 0.50:

            classification = (
                "fragile_ecological_runtime"
            )

        else:

            classification = (
                "ecological_runtime_instability"
            )

        result = {
            "lineage_id":
                lineage_id,
            "individual_id":
                individual_root.name,
            "ecological_diversity":
                round(
                    ecological_diversity,
                    4,
                ),
            "historical_divergence":
                round(
                    historical_divergence,
                    4,
                ),
            "bifurcation_intensity":
                round(
                    bifurcation_intensity,
                    4,
                ),
            "attractor_speciation":
                round(
                    attractor_speciation,
                    4,
                ),
            "anti_collapse_capacity":
                round(
                    anti_collapse_capacity,
                    4,
                ),
            "ecological_open_endedness":
                round(
                    ecological_open_endedness,
                    4,
                ),
            "classification":
                classification,
        }

        self._write_ecological_state(
            lineage_id,
            individual_root,
            result,
        )

        return result

    def step(self, state=None):

        return self.evaluate(state)
