
from __future__ import annotations

from collections import defaultdict
from statistics import mean
from datetime import datetime

PRIMITIVE = "semantic_density_tracker"

DEPENDENCIES = [
    "semantic_field",
    "semantic_propagation",
    "semantic_collapse",
    "structural_attractor",
    "attractor_basin",
    "topological_pressure_monitor",
    "ontology_topology_governance",
]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class SemanticDensityTracker:

    def __init__(self):
        self.primitive = PRIMITIVE
        self.history = []

    def _cluster_modules(
        self,
        symbols,
    ):

        clusters = defaultdict(list)

        for symbol in symbols:

            if "_" in symbol:
                prefix = symbol.split("_")[0]
            else:
                prefix = "misc"

            clusters[prefix].append(symbol)

        return dict(clusters)

    def step(
        self,
        semantic_symbols=None,
    ):

        semantic_symbols = (
            semantic_symbols
            or []
        )

        clusters = self._cluster_modules(
            semantic_symbols
        )

        cluster_density = {}

        for cluster, members in (
            clusters.items()
        ):

            density = _bounded(
                len(members) / 50.0
            )

            cluster_density[
                cluster
            ] = round(
                density,
                4,
            )

        if cluster_density:

            mean_density = mean(
                cluster_density.values()
            )

            max_density = max(
                cluster_density.values()
            )

        else:

            mean_density = 0.0
            max_density = 0.0

        density_gradient = (
            max_density
            - mean_density
        )

        semantic_saturation = _bounded(
            (
                mean_density
                + max_density
            ) / 2.0
        )

        rigidity_risk = _bounded(
            (
                semantic_saturation
                + density_gradient
            ) / 2.0
        )

        critical_clusters = [
            cluster
            for cluster, density
            in cluster_density.items()
            if density >= 0.70
        ]

        local_closure_risk = (
            len(critical_clusters) > 0
        )

        openness_preservation = _bounded(
            1.0
            - rigidity_risk
        )

        state = {
            "timestamp":
                datetime.utcnow()
                .isoformat() + "Z",
            "semantic_saturation":
                semantic_saturation,
        }

        self.history.append(state)

        if len(self.history) > 500:
            self.history = self.history[-500:]

        longitudinal_density_drift = mean(
            [
                x["semantic_saturation"]
                for x in self.history
            ]
        )

        return {
            "primitive": PRIMITIVE,
            "tracking_active": True,
            "cluster_count":
                len(clusters),
            "cluster_density":
                cluster_density,
            "mean_density":
                round(
                    mean_density,
                    4,
                ),
            "max_density":
                round(
                    max_density,
                    4,
                ),
            "density_gradient":
                round(
                    density_gradient,
                    4,
                ),
            "semantic_saturation":
                round(
                    semantic_saturation,
                    4,
                ),
            "rigidity_risk":
                round(
                    rigidity_risk,
                    4,
                ),
            "critical_clusters":
                critical_clusters,
            "local_closure_risk":
                local_closure_risk,
            "openness_preservation":
                round(
                    openness_preservation,
                    4,
                ),
            "future_openness_preserved":
                openness_preservation
                >= 0.70,
            "longitudinal_density_drift":
                round(
                    longitudinal_density_drift,
                    4,
                ),
            "history_size":
                len(
                    self.history
                ),
        }


if __name__ == "__main__":

    engine = SemanticDensityTracker()

    sample = [
        "trajectory_navigation",
        "trajectory_memory",
        "trajectory_prediction",
        "semantic_field",
        "semantic_propagation",
        "semantic_collapse",
    ]

    print(
        engine.step(
            semantic_symbols=sample
        )
    )
