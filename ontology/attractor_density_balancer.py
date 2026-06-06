from statistics import mean

PRIMITIVE = "attractor_density_balancer"

DEPENDENCIES = [
    "ontological_pressure_regulation",
    "closure_pressure_regulator",
    "semantic_density_tracker",
    "attractor_basin",
    "attractor_desaturation",
    "structural_attractor",
    "ontological_attractor_mapping",
    "trajectory_attractor_transition",
    "attractor_persistence_analyzer",
    "distributed_pluralistic_stability",
    "distributed_open_ended_pluralistic_evolution",
    "multi_lineage_topology",
    "distributed_attractor_speciation",
]

def _bounded(value):
    return max(0.0, min(1.0, float(value)))

class AttractorDensityBalancer:

    def __init__(
        self,
        balancing_gain=0.14,
        pluralism_floor=0.35,
    ):
        self.balancing_gain = balancing_gain
        self.pluralism_floor = pluralism_floor

    def step(
        self,
        attractor_strengths=None,
        attractor_persistence=0.5,
        semantic_saturation=0.5,
        convergence_pressure=0.5,
        lineage_diversity=0.5,
        bifurcation_capacity=0.5,
        metastability=0.5,
        topological_openness=0.5,
    ):

        attractor_strengths = attractor_strengths or {}

        if not attractor_strengths:
            return {
                "primitive": PRIMITIVE,
                "balancing_active": False,
            }

        dominant_attractor = max(
            attractor_strengths,
            key=attractor_strengths.get,
        )

        dominant_strength = attractor_strengths[
            dominant_attractor
        ]

        attractor_mean = mean(
            attractor_strengths.values()
        )

        attractor_dispersion = _bounded(
            dominant_strength - attractor_mean
        )

        monopolization_pressure = _bounded(
            (
                dominant_strength
                + attractor_persistence
                + convergence_pressure
            ) / 3.0
        )

        distributed_pluralism_capacity = _bounded(
            (
                lineage_diversity
                + bifurcation_capacity
                + metastability
                + topological_openness
                + (1.0 - semantic_saturation)
            ) / 5.0
        )

        balancing_pressure = _bounded(
            monopolization_pressure
            - distributed_pluralism_capacity
        )

        rebalanced_attractors = {}

        for attractor, strength in attractor_strengths.items():

            if attractor == dominant_attractor:

                adjusted = max(
                    self.pluralism_floor * 0.1,
                    strength
                    - (
                        balancing_pressure
                        * self.balancing_gain
                    ),
                )

            else:

                adjusted = min(
                    1.0,
                    strength
                    + (
                        distributed_pluralism_capacity
                        * 0.05
                    ),
                )

            rebalanced_attractors[
                attractor
            ] = round(adjusted, 4)

        distributed_topological_ecology = _bounded(
            (
                distributed_pluralism_capacity
                + (1.0 - monopolization_pressure)
                + (1.0 - attractor_dispersion)
            ) / 3.0
        )

        return {
            "primitive": PRIMITIVE,
            "balancing_active":
                balancing_pressure >= 0.15,
            "dominant_attractor":
                dominant_attractor,
            "attractor_dispersion":
                round(attractor_dispersion, 4),
            "monopolization_pressure":
                round(monopolization_pressure, 4),
            "distributed_pluralism_capacity":
                round(distributed_pluralism_capacity, 4),
            "balancing_pressure":
                round(balancing_pressure, 4),
            "distributed_topological_ecology":
                round(distributed_topological_ecology, 4),
            "rebalanced_attractors":
                rebalanced_attractors,
            "viable_pluralistic_ecology":
                distributed_topological_ecology >= 0.70,
        }

if __name__ == "__main__":

    engine = AttractorDensityBalancer()

    result = engine.step(
        attractor_strengths={
            "trajectory": 0.92,
            "semantic": 0.55,
            "civilizational": 0.48,
            "exploratory": 0.41,
        },
        attractor_persistence=0.87,
        semantic_saturation=0.81,
        convergence_pressure=0.84,
        lineage_diversity=0.62,
        bifurcation_capacity=0.66,
        metastability=0.58,
        topological_openness=0.44,
    )

    print(result)
