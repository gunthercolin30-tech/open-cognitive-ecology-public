from __future__ import annotations

from statistics import mean

PRIMITIVE = "reflexive_topology_self_revision"

DEPENDENCIES = [
    "ontology_topology_governance",
    "topological_pressure_monitor",
    "implicit_duplication_control",
    "distributed_semantic_pluralism",
    "ontological_pressure_regulation",
    "trajectory_self_correction",
    "constitutional_self_modification_protocol",
    "adaptive_constitutional_evolution",
    "multi_lineage_topology",
    "phenomenological_topology",
    "anti_closure_metaconstraint",
]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class ReflexiveTopologySelfRevision:

    def __init__(
        self,
        revision_gain: float = 0.14,
        pluralism_floor: float = 0.35,
        anti_centralization_floor: float = 0.40,
    ):
        self.revision_gain = revision_gain
        self.pluralism_floor = pluralism_floor
        self.anti_centralization_floor = (
            anti_centralization_floor
        )

    def step(
        self,
        topological_pressure: float = 0.5,
        convergence_risk: float = 0.5,
        historical_drift: float = 0.5,
        hidden_convergence_pressure: float = 0.5,
        pluralism_index: float = 0.5,
        distributed_openness: float = 0.5,
        reversibility_index: float = 0.5,
    ):

        topological_pressure = _bounded(
            topological_pressure
        )

        convergence_risk = _bounded(
            convergence_risk
        )

        historical_drift = _bounded(
            historical_drift
        )

        hidden_convergence_pressure = _bounded(
            hidden_convergence_pressure
        )

        pluralism_index = _bounded(
            pluralism_index
        )

        distributed_openness = _bounded(
            distributed_openness
        )

        reversibility_index = _bounded(
            reversibility_index
        )

        historical_reconvergence_risk = (
            _bounded(
                mean(
                    [
                        convergence_risk,
                        historical_drift,
                        hidden_convergence_pressure,
                    ]
                )
            )
        )

        topological_revision_pressure = (
            _bounded(
                historical_reconvergence_risk
                - pluralism_index
                + self.revision_gain
            )
        )

        pluralistic_revision_capacity = (
            max(
                self.pluralism_floor,
                _bounded(
                    mean(
                        [
                            pluralism_index,
                            distributed_openness,
                            reversibility_index,
                        ]
                    )
                )
            )
        )

        distributed_revision_viability = (
            _bounded(
                mean(
                    [
                        pluralistic_revision_capacity,
                        (
                            1.0
                            - historical_reconvergence_risk
                        ),
                        distributed_openness,
                    ]
                )
            )
        )

        anti_centralization_index = (
            max(
                self.anti_centralization_floor,
                _bounded(
                    (
                        distributed_openness
                        + reversibility_index
                        + (
                            1.0
                            - convergence_risk
                        )
                    ) / 3.0
                )
            )
        )

        local_revision_recommendations = []

        if topological_revision_pressure >= 0.55:

            local_revision_recommendations.extend(
                [
                    "increase_local_bifurcations",
                    "diversify_semantic_corridors",
                    "reduce_attractor_overlap",
                    "increase_lineage_separation",
                    "preserve_reversibility",
                ]
            )

        if hidden_convergence_pressure >= 0.70:

            local_revision_recommendations.append(
                "activate_distributed_desaturation"
            )

        if historical_drift >= 0.70:

            local_revision_recommendations.append(
                "increase_historical_divergence"
            )

        reflexive_revision_active = (
            topological_revision_pressure
            >= 0.45
        )

        future_openness_preserved = (
            distributed_revision_viability
            >= 0.70
        )

        return {
            "primitive": PRIMITIVE,
            "reflexive_revision_active":
                reflexive_revision_active,
            "historical_reconvergence_detected":
                historical_reconvergence_risk
                >= 0.65,
            "historical_reconvergence_risk":
                round(
                    historical_reconvergence_risk,
                    4,
                ),
            "topological_revision_pressure":
                round(
                    topological_revision_pressure,
                    4,
                ),
            "pluralistic_revision_capacity":
                round(
                    pluralistic_revision_capacity,
                    4,
                ),
            "distributed_revision_viability":
                round(
                    distributed_revision_viability,
                    4,
                ),
            "anti_centralization_index":
                round(
                    anti_centralization_index,
                    4,
                ),
            "local_revision_recommendations":
                local_revision_recommendations,
            "future_openness_preserved":
                future_openness_preserved,
        }
