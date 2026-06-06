
from __future__ import annotations

PRIMITIVE = "anti_reconvergence_instrumentation"

DEPENDENCIES = [
    "distributed_pluralistic_stability",
    "distributed_meta_stability",
    "distributed_semantic_pluralism",
    "trajectory_metastability",
    "architectural_non_closure_index",
    "longitudinal_society_observatory",
    "constitutional_longitudinal_observatory",
    "civilizational_metrics_synthesizer",
]


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class AntiReconvergenceInstrumentation:

    def __init__(self):
        self.primitive = PRIMITIVE
        self.history = []

    def step(
        self,
        runtime_similarity: float = 0.5,
        scheduler_alignment: float = 0.5,
        trajectory_diversity: float = 0.5,
        topological_openness: float = 0.5,
    ) -> dict:

        runtime_similarity = _clamp(runtime_similarity)
        scheduler_alignment = _clamp(scheduler_alignment)
        trajectory_diversity = _clamp(trajectory_diversity)
        topological_openness = _clamp(topological_openness)

        scheduler_divergence_index = _clamp(
            1.0 - scheduler_alignment
        )

        runtime_ecological_diversity = _clamp(
            trajectory_diversity
        )

        cross_runtime_similarity = runtime_similarity

        canonicalization_pressure = _clamp(
            (
                runtime_similarity
                + scheduler_alignment
                + (1.0 - trajectory_diversity)
            ) / 3.0
        )

        closure_pressure_score = _clamp(
            (
                canonicalization_pressure
                + (1.0 - topological_openness)
            ) / 2.0
        )

        civilizational_reconvergence_risk = _clamp(
            (
                canonicalization_pressure
                + closure_pressure_score
            ) / 2.0
        )

        trajectory_branching_capacity = _clamp(
            (
                trajectory_diversity
                + topological_openness
                + scheduler_divergence_index
            ) / 3.0
        )

        if civilizational_reconvergence_risk >= 0.85:
            classification = "High Reconvergence Risk"

        elif civilizational_reconvergence_risk >= 0.65:
            classification = "Moderate Reconvergence Risk"

        elif trajectory_branching_capacity >= 0.80:
            classification = "Pluralistic Open Ecology"

        else:
            classification = "Transitional Runtime Ecology"

        snapshot = {
            "civilizational_reconvergence_risk":
                civilizational_reconvergence_risk,
            "runtime_ecological_diversity":
                runtime_ecological_diversity,
            "closure_pressure_score":
                closure_pressure_score,
            "trajectory_branching_capacity":
                trajectory_branching_capacity,
        }

        self.history.append(snapshot)

        return {
            "primitive": self.primitive,
            "scheduler_divergence_index":
                round(
                    scheduler_divergence_index,
                    4,
                ),
            "runtime_ecological_diversity":
                round(
                    runtime_ecological_diversity,
                    4,
                ),
            "cross_runtime_similarity":
                round(
                    cross_runtime_similarity,
                    4,
                ),
            "canonicalization_pressure":
                round(
                    canonicalization_pressure,
                    4,
                ),
            "closure_pressure_score":
                round(
                    closure_pressure_score,
                    4,
                ),
            "civilizational_reconvergence_risk":
                round(
                    civilizational_reconvergence_risk,
                    4,
                ),
            "trajectory_branching_capacity":
                round(
                    trajectory_branching_capacity,
                    4,
                ),
            "history_length":
                len(self.history),
            "classification":
                classification,
            "diagnostics": {
                "dependencies": DEPENDENCIES,
                "anti_reconvergence_monitoring": True,
            },
        }
