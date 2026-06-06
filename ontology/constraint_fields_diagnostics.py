from __future__ import annotations

PRIMITIVE = "constraint_fields_diagnostics"
DESCRIPTION = "Constraint fields diagnostics."
DEPENDENCIES = []

"""
Diagnostics for the ConstraintFieldsPrimitive.

This module groups the theoretical diagnostics derived from the
constraint-based ontological corpus.
"""


from .constraint_fields_utils import clamp


class ConstraintFieldsDiagnosticsMixin:
    """
    Additional diagnostics derived from the theoretical corpus.
    """

    def compute_constraint_induced_domain(
        self,
        admissibility: float,
        constraint_density: float,
    ) -> float:
        """
        EXISTENCE_AS_CONSTRAINT_INDUCED_DOMAIN

        Effective domain of existence produced by constraints.
        """
        return clamp(
            admissibility
            * (1.0 - 0.5 * clamp(constraint_density))
            * self.constraint_domain_gain
        )

    def compute_trajectory_viability(
        self,
        admissibility: float,
        coupling: float,
    ) -> float:
        """
        TRAJECTORIES_WITHOUT_GLOBALITY

        Local viability without requiring global structure.
        """
        return clamp(
            admissibility
            * (1.0 - abs(clamp(coupling) - 0.5))
            * self.trajectory_gain
        )

    def compute_configurational_instability(
        self,
        intensity: float,
        environmental_pressure: float,
        constraint_density: float,
        coupling: float,
    ) -> float:
        """
        UNSTABLE_CONFIGURATION_PRINCIPLE

        Sensitivity increases when pressure and density are both high.
        """
        return clamp(
            (
                0.5 * intensity
                + 0.3 * clamp(environmental_pressure)
                + 0.2 * clamp(constraint_density) * clamp(coupling)
            )
            * self.instability_gain
        )

    def compute_global_closure_distance(
        self,
        admissibility: float,
    ) -> float:
        """
        IMPOSSIBILITY_OF_GLOBAL_CLOSURE

        Distance to complete closure. Remains strictly positive when
        some openness persists.
        """
        return max(
            self.minimum_admissibility,
            clamp(
                admissibility
                * (1.0 - 0.5 * self.stability)
                * self.closure_resistance
            ),
        )

    def compute_constraint_dynamics(
        self,
        intensity: float,
        constraint_density: float,
        environmental_pressure: float,
        coupling: float,
    ) -> float:
        """
        CONSTRAINT_FIELDS_AND_DYNAMICS_OF_CONSTRAINTS

        Effective variation of the constraint field.
        """
        density = clamp(constraint_density)
        pressure = clamp(environmental_pressure)
        coupled = clamp(coupling)

        variability = (
            abs(density - pressure)
            + abs(pressure - coupled)
            + abs(coupled - density)
        ) / 3.0

        return clamp(
            (
                0.6 * intensity
                + 0.4 * variability
            )
            * self.dynamics_gain
        )

    def compute_non_representability_index(
        self,
        global_closure_distance: float,
        configurational_instability: float,
        constraint_dynamics: float,
    ) -> float:
        """
        THEORY_OF_NON_REPRESENTABILITY

        Residual irreducibility of the current configuration.
        """
        return clamp(
            (
                0.4 * global_closure_distance
                + 0.3 * configurational_instability
                + 0.3 * constraint_dynamics
            )
            * self.non_representability_gain
        )
