from __future__ import annotations

PRIMITIVE = "constraint_fields"
DESCRIPTION = "Constraint fields."
DEPENDENCIES = []

"""
ontology/constraint_fields.py

Computational implementation of the ontological primitive CONSTRAINT_FIELDS.

This module formalizes constraints as distributed fields that locally modulate
the admissibility of trajectories, activations, and transitions. Constraints
are treated as active operators rather than static limitations.

Theoretical reference
---------------------
- Colin Gunther, Constraint Fields and the Dynamics of Constraints.
"""


from typing import Dict

from .constraint_fields_diagnostics import (
    ConstraintFieldsDiagnosticsMixin,
)
from .constraint_fields_utils import clamp


class ConstraintFieldsPrimitive(
    ConstraintFieldsDiagnosticsMixin,
):
    """
    Distributed field representation of interacting constraints.

    Parameters
    ----------
    weight:
        Global influence of the primitive.
    drift:
        Intrinsic field bias added to local intensity.
    stability:
        Persistence of the field. Higher values slightly reduce volatility.
    field_strength:
        Global multiplier applied to the local field intensity.
    minimum_admissibility:
        Minimum strictly positive admissibility guaranteed by the primitive.
    """

    PRIMITIVE_NAME = "CONSTRAINT_FIELDS"
    MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"

    def __init__(
        self,
        weight: float = 1.2,
        drift: float = 0.02,
        stability: float = 0.98,
        field_strength: float = 1.0,
        minimum_admissibility: float = 0.01,
        constraint_domain_gain: float = 1.0,
        trajectory_gain: float = 1.0,
        instability_gain: float = 1.0,
        closure_resistance: float = 1.0,
        dynamics_gain: float = 1.0,
        non_representability_gain: float = 1.0,
    ) -> None:
        self.weight = max(0.0, float(weight))
        self.drift = float(drift)
        self.stability = clamp(float(stability))
        self.field_strength = max(
            0.0,
            float(field_strength),
        )
        self.minimum_admissibility = clamp(
            float(minimum_admissibility),
            1e-12,
            1.0,
        )

        # Corpus-derived gains
        self.constraint_domain_gain = max(
            0.0,
            float(constraint_domain_gain),
        )
        self.trajectory_gain = max(
            0.0,
            float(trajectory_gain),
        )
        self.instability_gain = max(
            0.0,
            float(instability_gain),
        )
        self.closure_resistance = max(
            0.0,
            float(closure_resistance),
        )
        self.dynamics_gain = max(
            0.0,
            float(dynamics_gain),
        )
        self.non_representability_gain = max(
            0.0,
            float(non_representability_gain),
        )

    def local_intensity(
        self,
        constraint_density: float,
        environmental_pressure: float,
        coupling: float,
    ) -> float:
        """
        Compute the local intensity of the constraint field.
        """
        density = clamp(constraint_density)
        pressure = clamp(environmental_pressure)
        coupling = clamp(coupling)

        base = (
            density
            + pressure
            + coupling
        ) / 3.0

        # Stability reduces effective volatility.
        damping = 1.0 - 0.5 * self.stability

        intensity = (
            base
            * self.weight
            * self.field_strength
            * damping
            + self.drift
        )

        return clamp(intensity)

    def admissibility(
        self,
        constraint_density: float,
        environmental_pressure: float,
        coupling: float,
    ) -> float:
        """
        Compute the local admissibility coefficient.
        """
        intensity = self.local_intensity(
            constraint_density,
            environmental_pressure,
            coupling,
        )

        return max(
            self.minimum_admissibility,
            1.0 - intensity,
        )

    def modulate(
        self,
        activation: float,
        constraint_density: float,
        environmental_pressure: float,
        coupling: float,
    ) -> float:
        """
        Modulate an activation by local admissibility.
        """
        admissibility = self.admissibility(
            constraint_density,
            environmental_pressure,
            coupling,
        )

        return max(
            0.0,
            float(activation) * admissibility,
        )

    def combine(
        self,
        *intensities: float,
    ) -> float:
        """
        Combine multiple field intensities by arithmetic mean.
        """
        if not intensities:
            return 0.0

        values = [clamp(v) for v in intensities]

        return clamp(
            sum(values) / len(values)
        )

    def field_strength_metric(
        self,
        constraint_density: float = 0.5,
        environmental_pressure: float = 0.5,
        coupling: float = 0.5,
    ) -> float:
        """
        Scalar metric representing the effective strength of the field.

        This method is provided to satisfy the generic scientific
        specification requiring a field strength accessor.
        """
        return self.local_intensity(
            constraint_density,
            environmental_pressure,
            coupling,
        )

    def viability_gradient(
        self,
        constraint_density: float = 0.5,
        environmental_pressure: float = 0.5,
        coupling: float = 0.5,
    ) -> float:
        """
        Compute the local viability gradient.

        Positive values indicate a net increase in admissibility relative
        to a neutral baseline of 0.5.
        """
        admissibility = self.admissibility(
            constraint_density,
            environmental_pressure,
            coupling,
        )

        return admissibility - 0.5

    def step(
        self,
        activation: float = 1.0,
        constraint_density: float = 0.5,
        environmental_pressure: float = 0.5,
        coupling: float = 0.5,
    ) -> Dict[str, float]:
        """
        Evaluate the primitive for a given local configuration.

        Default values are provided so that the primitive can be
        executed by the global corpus simulation engine, which calls
        ``primitive.step()`` without arguments.
        """
        intensity = self.local_intensity(
            constraint_density,
            environmental_pressure,
            coupling,
        )

        admissibility = max(
            self.minimum_admissibility,
            1.0 - intensity,
        )

        modulated_activation = max(
            0.0,
            float(activation) * admissibility,
        )

        # EXISTENCE_AS_CONSTRAINT_INDUCED_DOMAIN
        constraint_induced_domain = (
            self.compute_constraint_induced_domain(
                admissibility,
                constraint_density,
            )
        )

        # TRAJECTORIES_WITHOUT_GLOBALITY
        trajectory_viability = (
            self.compute_trajectory_viability(
                admissibility,
                coupling,
            )
        )

        # UNSTABLE_CONFIGURATION_PRINCIPLE
        configurational_instability = (
            self.compute_configurational_instability(
                intensity,
                environmental_pressure,
                constraint_density,
                coupling,
            )
        )

        # IMPOSSIBILITY_OF_GLOBAL_CLOSURE
        global_closure_distance = (
            self.compute_global_closure_distance(
                admissibility,
            )
        )

        # CONSTRAINT_FIELDS_AND_DYNAMICS_OF_CONSTRAINTS
        constraint_dynamics = (
            self.compute_constraint_dynamics(
                intensity,
                constraint_density,
                environmental_pressure,
                coupling,
            )
        )

        # THEORY_OF_NON_REPRESENTABILITY
        non_representability_index = (
            self.compute_non_representability_index(
                global_closure_distance,
                configurational_instability,
                constraint_dynamics,
            )
        )

        return {
            "local_intensity": intensity,
            "admissibility": admissibility,
            "modulated_activation": modulated_activation,
            "constraint_induced_domain":
                constraint_induced_domain,
            "trajectory_viability":
                trajectory_viability,
            "configurational_instability":
                configurational_instability,
            "global_closure_distance":
                global_closure_distance,
            "constraint_dynamics":
                constraint_dynamics,
            "non_representability_index":
                non_representability_index,
        }

    def validate(self) -> Dict[str, object]:
        """
        Scientific validation of the CONSTRAINT_FIELDS primitive.

        Returns
        -------
        dict
            Standard validation payload compatible with validation.main.
        """
        try:
            result = self.step()

            field_strength = result["local_intensity"]
            viability_gradient = (
                result["admissibility"] - 0.5
            )

            in_viability_domain = (
                result["admissibility"]
                >= self.minimum_admissibility
            )

            valid = (
                0.0 <= field_strength <= 1.0
                and -0.5 <= viability_gradient <= 0.5
                and result["modulated_activation"] >= 0.0
                and in_viability_domain
            )

            diagnostics = {
                "primitive": self.PRIMITIVE_NAME,
                "maturity_level": self.MATURITY_LEVEL,
                "field_strength": field_strength,
                "viability_gradient": viability_gradient,
                "admissibility": result["admissibility"],
                "minimum_admissibility":
                    self.minimum_admissibility,
                "trajectory_viability":
                    result["trajectory_viability"],
                "constraint_induced_domain":
                    result["constraint_induced_domain"],
                "configurational_instability":
                    result["configurational_instability"],
                "global_closure_distance":
                    result["global_closure_distance"],
                "constraint_dynamics":
                    result["constraint_dynamics"],
                "non_representability_index":
                    result["non_representability_index"],
                "status":
                    "viable" if valid else "non_viable",
            }

            return {
                "valid": valid,
                "in_viability_domain":
                    in_viability_domain,
                "configuration_size":
                    len(result),
                "diagnostics":
                    diagnostics,
            }

        except Exception as exc:
            return {
                "valid": False,
                "in_viability_domain": False,
                "configuration_size": 0,
                "diagnostics": {
                    "primitive":
                        self.PRIMITIVE_NAME,
                    "maturity_level":
                        self.MATURITY_LEVEL,
                    "status": "error",
                    "error": str(exc),
                },
            }


if __name__ == "__main__":
    primitive = ConstraintFieldsPrimitive()

    result = primitive.step(
        activation=1.0,
        constraint_density=0.80,
        environmental_pressure=0.65,
        coupling=0.75,
    )

    print("CONSTRAINT_FIELDS evaluation")
    print("-" * 40)

    for key, value in result.items():
        print(f"{key:28s}: {value}")

    print("\nValidation")
    print("-" * 40)
    print(primitive.validate())
