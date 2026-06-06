from statistics import mean

PRIMITIVE = "distributed_semantic_pluralism"

DEPENDENCIES = [
    "distributed_reflexive_civilizational_identity",
    "heterogeneous_node_coordination",
    "distributed_civilizational_viability",
    "distributed_symbolic_ecology",
    "distributed_open_ended_pluralistic_evolution",
    "trajectory_attractor_transition",
    "distributed_semantic_recycling",
    "multi_lineage_topology",
    "symbolic_fragmentation",
    "trajectory_exploration",
    "trajectory_exploration_exploitation_balance",
]


def _bounded(value):

    return max(
        0.0,
        min(
            1.0,
            float(value),
        ),
    )


class DistributedSemanticPluralism:

    def __init__(
        self,
        corridor_floor=0.35,
        ecological_gain=0.15,
    ):

        self.corridor_floor = corridor_floor
        self.ecological_gain = ecological_gain

    def step(
        self,
        semantic_diversity=0.5,
        corridor_density=0.5,
        inter_lineage_exchange=0.5,
        symbolic_fragmentation=0.5,
        convergence_pressure=0.5,
        exploration_capacity=0.5,
        ecological_openness=0.5,
        distributed_viability=0.5,
        civilizational_continuity=0.5,
    ):

        semantic_diversity = _bounded(
            semantic_diversity
        )

        corridor_density = _bounded(
            corridor_density
        )

        inter_lineage_exchange = _bounded(
            inter_lineage_exchange
        )

        symbolic_fragmentation = _bounded(
            symbolic_fragmentation
        )

        convergence_pressure = _bounded(
            convergence_pressure
        )

        exploration_capacity = _bounded(
            exploration_capacity
        )

        ecological_openness = _bounded(
            ecological_openness
        )

        distributed_viability = _bounded(
            distributed_viability
        )

        civilizational_continuity = _bounded(
            civilizational_continuity
        )

        semantic_isolation_risk = _bounded(
            (
                symbolic_fragmentation
                + convergence_pressure
                + (
                    1.0 - corridor_density
                )
            ) / 3.0
        )

        corridor_regeneration_capacity = (
            _bounded(
                (
                    corridor_density
                    + inter_lineage_exchange
                    + exploration_capacity
                ) / 3.0
            )
        )

        ecological_circulation_index = (
            _bounded(
                (
                    corridor_regeneration_capacity
                    + ecological_openness
                    + semantic_diversity
                ) / 3.0
            )
        )

        distributed_pluralistic_viability = (
            _bounded(
                mean(
                    [
                        ecological_circulation_index,
                        distributed_viability,
                        civilizational_continuity,
                    ]
                )
            )
        )

        anti_fragmentation_coordination = (
            _bounded(
                (
                    distributed_pluralistic_viability
                    + (
                        1.0
                        - semantic_isolation_risk
                    )
                ) / 2.0
            )
        )

        distributed_semantic_pluralism_index = (
            max(
                self.corridor_floor,
                _bounded(
                    (
                        anti_fragmentation_coordination
                        + corridor_regeneration_capacity
                        + ecological_circulation_index
                    ) / 3.0
                )
            )
        )

        regenerative_corridor_pressure = (
            _bounded(
                (
                    semantic_isolation_risk
                    - distributed_semantic_pluralism_index
                    + self.ecological_gain
                )
            )
        )

        distributed_semantic_pluralism_viable = (
            distributed_semantic_pluralism_index
            >= 0.70
        )

        return {
            "primitive": PRIMITIVE,
            "semantic_isolation_risk":
                round(
                    semantic_isolation_risk,
                    4,
                ),
            "corridor_regeneration_capacity":
                round(
                    corridor_regeneration_capacity,
                    4,
                ),
            "ecological_circulation_index":
                round(
                    ecological_circulation_index,
                    4,
                ),
            "distributed_pluralistic_viability":
                round(
                    distributed_pluralistic_viability,
                    4,
                ),
            "anti_fragmentation_coordination":
                round(
                    anti_fragmentation_coordination,
                    4,
                ),
            "distributed_semantic_pluralism_index":
                round(
                    distributed_semantic_pluralism_index,
                    4,
                ),
            "regenerative_corridor_pressure":
                round(
                    regenerative_corridor_pressure,
                    4,
                ),
            "distributed_semantic_pluralism_viable":
                distributed_semantic_pluralism_viable,
            "future_openness_preserved":
                (
                    distributed_semantic_pluralism_index
                    >= 0.70
                ),
        }


if __name__ == "__main__":

    engine = DistributedSemanticPluralism()

    result = engine.step(
        semantic_diversity=0.58,
        corridor_density=0.54,
        inter_lineage_exchange=0.63,
        symbolic_fragmentation=0.44,
        convergence_pressure=0.68,
        exploration_capacity=0.61,
        ecological_openness=0.72,
        distributed_viability=0.57,
        civilizational_continuity=0.62,
    )

    print(result)
