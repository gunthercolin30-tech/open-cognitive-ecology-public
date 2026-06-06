
class MultiIndividualCivilizationalEcology:

    def __init__(self):
        pass

    def evaluate_ecology(self, state):

        agents = state.get("agents", [])

        if not agents:
            return {
                "ecological_diversity": 0.0,
                "fragmentation_risk": 1.0,
                "coordination_viability": 0.0,
                "closure_pressure": 1.0,
                "civilizational_openness_index": 0.0,
                "ecological_viability": False,
            }

        diversity_values = [
            a.get("trajectory_diversity", 0.0)
            for a in agents
        ]

        ecological_diversity = (
            sum(diversity_values) / len(diversity_values)
        )

        fragmentation_risk = state.get(
            "fragmentation_index",
            0.0,
        )

        coordination_viability = state.get(
            "coordination_stability",
            0.0,
        )

        closure_pressure = state.get(
            "closure_pressure",
            0.0,
        )

        openness = (
            ecological_diversity
            * coordination_viability
            * (1.0 - fragmentation_risk)
            * (1.0 - closure_pressure)
        )

        ecological_viability = openness >= 0.25

        return {
            "ecological_diversity": round(
                ecological_diversity,
                4,
            ),
            "fragmentation_risk": round(
                fragmentation_risk,
                4,
            ),
            "coordination_viability": round(
                coordination_viability,
                4,
            ),
            "closure_pressure": round(
                closure_pressure,
                4,
            ),
            "civilizational_openness_index": round(
                openness,
                4,
            ),
            "ecological_viability": ecological_viability,
        }
