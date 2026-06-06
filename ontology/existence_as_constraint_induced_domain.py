PRIMITIVE = "existence_as_constraint_induced_domain"
DESCRIPTION = "Existence as constraint induced domain."
DEPENDENCIES = []

from ontology.constraint_fields import ConstraintFieldsPrimitive


class ExistenceAsConstraintInducedDomainPrimitive:
    """
    Existence emerges as a viable domain induced by local constraint
    organization.
    """

    PRINCIPLE = "EXISTENCE_AS_CONSTRAINT_INDUCED_DOMAIN"

    def __init__(self):
        self.constraint_fields = ConstraintFieldsPrimitive()
        self.history = []

    @staticmethod
    def _clip(value, lower=0.0, upper=1.0):
        return max(lower, min(upper, float(value)))

    def step(
        self,
        local_constraint_strength=1.0,
        adaptive_capacity=0.8,
        representational_coherence=0.65,
        openness_factor=0.75,
    ):
        """
        Execute one evaluation step.

        Default values are provided so that the primitive is compatible
        with the global corpus simulation engine, which invokes
        primitive.step() without arguments.
        """
        diagnostics = self.constraint_fields.step(
            local_constraint_strength,
            adaptive_capacity,
            representational_coherence,
            openness_factor,
        )

        existence_domain_extent = self._clip(
            diagnostics.get("constraint_induced_domain", 0.0)
        )

        existential_viability = self._clip(
            diagnostics.get("trajectory_viability", 0.0)
        )

        existential_openness = self._clip(
            diagnostics.get("global_closure_distance", 0.0)
        )

        existential_non_representability = self._clip(
            diagnostics.get("non_representability_index", 0.0)
        )

        existential_intensity = self._clip(
            (
                existence_domain_extent
                * existential_viability
                * existential_openness
                * existential_non_representability
            )
            ** 0.25
        )

        existential_stability = self._clip(
            0.5 * existential_viability
            + 0.3 * existence_domain_extent
            + 0.2 * existential_openness
        )

        existential_fragility = self._clip(
            1.0 - existential_stability
        )

        domain_emergence_threshold = 0.5
        domain_exists = (
            existential_intensity
            >= domain_emergence_threshold
        )

        result = {
            "principle": self.PRINCIPLE,
            "constraint_fields_diagnostics": diagnostics,
            "existence_domain_extent": existence_domain_extent,
            "existential_viability": existential_viability,
            "existential_openness": existential_openness,
            "existential_non_representability": (
                existential_non_representability
            ),
            "existential_intensity": existential_intensity,
            "existential_stability": existential_stability,
            "existential_fragility": existential_fragility,
            "domain_emergence_threshold": (
                domain_emergence_threshold
            ),
            "domain_exists": domain_exists,
        }

        self.history.append(result)

        return result

    def last(self):
        if not self.history:
            return None
        return self.history[-1]

    def reset(self):
        self.history = []


if __name__ == "__main__":
    primitive = ExistenceAsConstraintInducedDomainPrimitive()

    result = primitive.step(
        local_constraint_strength=1.0,
        adaptive_capacity=0.8,
        representational_coherence=0.65,
        openness_factor=0.75,
    )

    print("\n--- existence as constraint-induced domain ---")
    for key, value in result.items():
        print(f"{key}: {value}")