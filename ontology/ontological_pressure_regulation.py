from __future__ import annotations

PRIMITIVE = "ontological_pressure_regulation"

DEPENDENCIES = [
    "anti_closure_metaconstraint",
    "topological_pressure_monitor",
    "semantic_density_tracker",
    "attractor_desaturation",
    "trajectory_convergence",
    "distributed_symbolic_ecology",
    "non_convergent_intelligence_dynamics",
    "openness_preservation_supervisor",
    "selective_pressure",
]


def _bounded(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


class OntologicalPressureRegulation:

    def __init__(
        self,
        regulation_gain: float = 0.12,
        pluralism_floor: float = 0.35,
        viable_convergence_floor: float = 0.22,
    ):
        self.regulation_gain = regulation_gain
        self.pluralism_floor = pluralism_floor
        self.viable_convergence_floor = viable_convergence_floor

    def step(
        self,
        topological_pressure: float = 0.5,
        convergence_pressure: float = 0.5,
        semantic_density: float = 0.5,
        openness_score: float = 0.5,
        attractor_rigidity: float = 0.5,
        selective_pressure: float = 0.5,
    ):

        topological_pressure = _bounded(topological_pressure)
        convergence_pressure = _bounded(convergence_pressure)
        semantic_density = _bounded(semantic_density)
        openness_score = _bounded(openness_score)
        attractor_rigidity = _bounded(attractor_rigidity)
        selective_pressure = _bounded(selective_pressure)

        hierarchical_concentration_risk = _bounded(
            (
                topological_pressure
                + convergence_pressure
                + attractor_rigidity
                + selective_pressure
            ) / 4.0
        )

        latent_convergence_pressure = _bounded(
            (
                semantic_density
                + convergence_pressure
                + selective_pressure
            ) / 3.0
        )

        semantic_dispersion_index = _bounded(
            (1.0 - semantic_density)
            + openness_score * 0.5
        )

        anti_closure_regulation_strength = _bounded(
            (
                openness_score
                + semantic_dispersion_index
                + (1.0 - hierarchical_concentration_risk)
            ) / 3.0
        )

        distributed_pressure_balance = _bounded(
            (
                anti_closure_regulation_strength
                + (1.0 - latent_convergence_pressure)
            ) / 2.0
        )

        topological_pluralism_score = max(
            self.pluralism_floor,
            _bounded(
                (
                    semantic_dispersion_index
                    + openness_score
                ) / 2.0
            )
        )

        regulation_pressure = _bounded(
            (
                hierarchical_concentration_risk
                + latent_convergence_pressure
            ) / 2.0
        )

        regulation_active = (
            regulation_pressure >= 0.45
        )

        corrected_pressure = max(
            self.viable_convergence_floor,
            regulation_pressure
            - self.regulation_gain
        )

        distributed_viability_preservation = _bounded(
            (
                topological_pluralism_score
                + distributed_pressure_balance
                + (1.0 - corrected_pressure)
            ) / 3.0
        )

        anti_monopolization_index = _bounded(
            (
                1.0
                - hierarchical_concentration_risk
            ) * topological_pluralism_score
        )

        return {
            "primitive": PRIMITIVE,
            "regulation_active": regulation_active,
            "hierarchical_concentration_risk": round(
                hierarchical_concentration_risk,
                4,
            ),
            "latent_convergence_pressure": round(
                latent_convergence_pressure,
                4,
            ),
            "semantic_dispersion_index": round(
                semantic_dispersion_index,
                4,
            ),
            "anti_closure_regulation_strength": round(
                anti_closure_regulation_strength,
                4,
            ),
            "distributed_pressure_balance": round(
                distributed_pressure_balance,
                4,
            ),
            "topological_pluralism_score": round(
                topological_pluralism_score,
                4,
            ),
            "anti_monopolization_index": round(
                anti_monopolization_index,
                4,
            ),
            "regulation_pressure": round(
                regulation_pressure,
                4,
            ),
            "corrected_pressure": round(
                corrected_pressure,
                4,
            ),
            "distributed_viability_preserved": (
                distributed_viability_preservation >= 0.70
            ),
            "distributed_viability_preservation": round(
                distributed_viability_preservation,
                4,
            ),
        }


if __name__ == "__main__":

    engine = OntologicalPressureRegulation()

    result = engine.step(
        topological_pressure=0.82,
        convergence_pressure=0.77,
        semantic_density=0.81,
        openness_score=0.42,
        attractor_rigidity=0.79,
        selective_pressure=0.74,
    )

    print(result)
