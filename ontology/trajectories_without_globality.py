PRIMITIVE = "trajectories_without_globality"
DESCRIPTION = "Trajectories without globality."
DEPENDENCIES = []

from ontology.existence_as_constraint_induced_domain import (
    ExistenceAsConstraintInducedDomainPrimitive,
)


class TrajectoriesWithoutGlobalityPrimitive:
    """
    Formalization of the principle TRAJECTORIES_WITHOUT_GLOBALITY.

    This primitive models the possibility of locally viable trajectories
    in the absence of any globally closed structure or total representation
    of the system.

    The primitive is built directly upon
    ExistenceAsConstraintInducedDomainPrimitive.

    Conceptual interpretation
    -------------------------
    A trajectory can remain viable if:
    - a local existence domain is sufficiently extended,
    - existential viability is maintained,
    - openness remains high,
    - global representability remains impossible.

    The absence of globality is therefore not an obstacle to navigation,
    but a structural condition enabling situated trajectories.
    """

    PRINCIPLE = "TRAJECTORIES_WITHOUT_GLOBALITY"

    def __init__(self):
        self.existence_domain = (
            ExistenceAsConstraintInducedDomainPrimitive()
        )

    @staticmethod
    def _clamp(value):
        """
        Clamp a numerical value to the interval [0, 1].
        """
        return max(0.0, min(1.0, value))

    def step(
        self,
        local_intensity=1.0,
        admissibility=0.8,
        openness=0.65,
        non_representability=0.75,
    ):
        """
        Compute the dynamics of trajectories without globality.

        Parameters
        ----------
        local_intensity : float
            Local constraint activation intensity.
        admissibility : float
            Degree of local admissibility.
        openness : float
            Structural openness.
        non_representability : float
            Degree to which total representation is impossible.

        Returns
        -------
        dict
            Diagnostics including:
            - local_trajectory_viability
            - globality_absence
            - navigation_capacity
            - trajectory_without_globality

            plus all diagnostics returned by the underlying primitive.

        Notes
        -----
        Default values are provided so that the primitive is compatible
        with the global corpus simulation engine, which invokes
        primitive.step() without arguments.
        """

        # Compute the underlying existence domain.
        domain = self.existence_domain.step(
            local_intensity,
            admissibility,
            openness,
            non_representability,
        )

        # Extract diagnostics.
        extent = domain["existence_domain_extent"]
        viability = domain["existential_viability"]
        existential_openness = domain["existential_openness"]
        non_repr = domain["existential_non_representability"]
        intensity = domain["existential_intensity"]
        domain_exists = domain["domain_exists"]

        # Local trajectory viability depends on:
        # - the extent of the viable domain,
        # - local viability,
        # - existential intensity.
        local_trajectory_viability = self._clamp(
            extent * viability * intensity
        )

        # Globality absence reflects:
        # - openness,
        # - non-representability.
        globality_absence = self._clamp(
            existential_openness * non_repr
        )

        # Navigation capacity measures the ability to move through
        # locally viable states despite the absence of global closure.
        navigation_capacity = self._clamp(
            local_trajectory_viability * globality_absence
        )

        # Final principle activation requires:
        # - an existing domain,
        # - local trajectory viability,
        # - absence of globality,
        # - effective navigation capacity.
        trajectory_without_globality = (
            domain_exists and navigation_capacity > 0.0
        )

        return {
            **domain,
            "principle": self.PRINCIPLE,
            "local_trajectory_viability": (
                local_trajectory_viability
            ),
            "globality_absence": globality_absence,
            "navigation_capacity": navigation_capacity,
            "trajectory_without_globality": (
                trajectory_without_globality
            ),
        }


if __name__ == "__main__":
    primitive = TrajectoriesWithoutGlobalityPrimitive()

    diagnostics = primitive.step(
        local_intensity=1.0,
        admissibility=0.8,
        openness=0.65,
        non_representability=0.75,
    )

    print("\n--- trajectories without globality ---")
    print("principle:", diagnostics["principle"])
    print(
        "local_trajectory_viability:",
        diagnostics["local_trajectory_viability"],
    )
    print(
        "globality_absence:",
        diagnostics["globality_absence"],
    )
    print(
        "navigation_capacity:",
        diagnostics["navigation_capacity"],
    )
    print(
        "trajectory_without_globality:",
        diagnostics["trajectory_without_globality"],
    )
    print(
        "domain_exists:",
        diagnostics["domain_exists"],
    )