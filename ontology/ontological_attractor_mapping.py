
from __future__ import annotations

from collections import defaultdict
from statistics import mean
from datetime import datetime

PRIMITIVE = "ontological_attractor_mapping"

DEPENDENCIES = [
    "structural_attractor",
    "attractor_basin",
    "semantic_density_tracker",
    "topological_pressure_monitor",
    "ontology_topology_governance",
    "semantic_field",
    "graph_builders",
]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class OntologicalAttractorMapping:

    def __init__(self):
        self.primitive = PRIMITIVE
        self.mapping_history = []

    def _build_attractor_regions(
        self,
        symbols,
    ):

        regions = defaultdict(list)

        for symbol in symbols:

            if "_" in symbol:
                region = symbol.split("_")[0]
            else:
                region = "misc"

            regions[region].append(symbol)

        return dict(regions)

    def _compute_region_strength(
        self,
        members,
    ):

        return _bounded(
            len(members) / 50.0
        )

    def step(
        self,
        semantic_symbols=None,
    ):

        semantic_symbols = (
            semantic_symbols
            or []
        )

        attractor_regions = (
            self._build_attractor_regions(
                semantic_symbols
            )
        )

        region_strengths = {}

        for region, members in (
            attractor_regions.items()
        ):

            strength = (
                self._compute_region_strength(
                    members
                )
            )

            region_strengths[
                region
            ] = round(
                strength,
                4,
            )

        dominant_region = None

        if region_strengths:

            dominant_region = max(
                region_strengths,
                key=region_strengths.get,
            )

        attractor_routes = []

        ordered_regions = sorted(
            region_strengths.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        for i in range(
            len(ordered_regions) - 1
        ):

            source = ordered_regions[i][0]
            target = ordered_regions[i + 1][0]

            attractor_routes.append(
                {
                    "source": source,
                    "target": target,
                    "transition_weight":
                        round(
                            (
                                ordered_regions[i][1]
                                + ordered_regions[i + 1][1]
                            ) / 2.0,
                            4,
                        ),
                }
            )

        regional_density = (
            mean(
                region_strengths.values()
            )
            if region_strengths
            else 0.0
        )

        attractor_capture_risk = _bounded(
            max(
                region_strengths.values()
            )
            if region_strengths
            else 0.0
        )

        ontological_singularity_detected = (
            attractor_capture_risk >= 0.90
        )

        topological_navigation_openness = _bounded(
            1.0
            - attractor_capture_risk
        )

        state = {
            "timestamp":
                datetime.utcnow()
                .isoformat() + "Z",
            "capture_risk":
                attractor_capture_risk,
        }

        self.mapping_history.append(state)

        if len(self.mapping_history) > 500:
            self.mapping_history = (
                self.mapping_history[-500:]
            )

        longitudinal_capture_drift = mean(
            [
                x["capture_risk"]
                for x in self.mapping_history
            ]
        )

        return {
            "primitive": PRIMITIVE,
            "mapping_active": True,
            "region_count":
                len(attractor_regions),
            "region_strengths":
                region_strengths,
            "dominant_region":
                dominant_region,
            "attractor_routes":
                attractor_routes,
            "regional_density":
                round(
                    regional_density,
                    4,
                ),
            "attractor_capture_risk":
                round(
                    attractor_capture_risk,
                    4,
                ),
            "ontological_singularity_detected":
                ontological_singularity_detected,
            "topological_navigation_openness":
                round(
                    topological_navigation_openness,
                    4,
                ),
            "future_openness_preserved":
                topological_navigation_openness
                >= 0.70,
            "longitudinal_capture_drift":
                round(
                    longitudinal_capture_drift,
                    4,
                ),
            "history_size":
                len(
                    self.mapping_history
                ),
        }


if __name__ == "__main__":

    engine = OntologicalAttractorMapping()

    sample = [
        "trajectory_navigation",
        "trajectory_prediction",
        "semantic_field",
        "semantic_propagation",
        "civilizational_memory",
        "civilizational_resilience",
    ]

    print(
        engine.step(
            semantic_symbols=sample
        )
    )
