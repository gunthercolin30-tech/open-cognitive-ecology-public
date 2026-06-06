PRIMITIVE = "morphogenesis_under_constraints"
DESCRIPTION = "Morphogenesis under constraints."
DEPENDENCIES = []

"""
Morphogenesis Under Constraints Primitive
========================================

This module formalizes the principle:

    MORPHOGENESIS_UNDER_CONSTRAINTS

Core idea
---------
Whenever a configuration remains structurally unstable while still
subject to constraints, it continuously generates new forms, patterns
and organizations.

The primitive relies exclusively on:

    UnstableConfigurationPrinciplePrimitive

Returned diagnostics
--------------------
The step() method returns:

    - morphogenetic_activity
    - structural_emergence
    - pattern_generation
    - morphogenesis_under_constraints

This primitive provides a computational foundation for future modules
dedicated to:

    - form generation,
    - bifurcations,
    - structural transitions,
    - evolutionary dynamics of intelligences.
"""

from ontology.unstable_configuration_principle import (
    UnstableConfigurationPrinciplePrimitive,
)


class MorphogenesisUnderConstraintsPrimitive:
    """
    Formalization of the principle:

        MORPHOGENESIS_UNDER_CONSTRAINTS

    Structural instability maintained under constraints drives the
    continuous production of new forms and structural organizations.
    """

    PRINCIPLE_NAME = "MORPHOGENESIS_UNDER_CONSTRAINTS"

    def __init__(self):
        """
        Initialize the primitive and its underlying principle.
        """
        self.unstable_configuration_principle = (
            UnstableConfigurationPrinciplePrimitive()
        )

    def step(
        self,
        intensity=1.0,
        coherence=0.8,
        coupling=0.65,
        stability=0.75,
    ):
        """
        Execute one morphogenetic step.

        Parameters
        ----------
        intensity : float
            Overall activation intensity.
        coherence : float
            Degree of local consistency.
        coupling : float
            Degree of interaction coupling.
        stability : float
            Constraint-induced stability.

        Returns
        -------
        dict
            Diagnostics of morphogenesis under constraints.
        """

        # The underlying primitive currently exposes a parameterless API.
        diagnostics = self.unstable_configuration_principle.step()

        configuration_instability = diagnostics.get(
            "configuration_instability",
            0.0,
        )
        transformation_potential = diagnostics.get(
            "transformation_potential",
            0.0,
        )
        structural_tension = diagnostics.get(
            "structural_tension",
            0.0,
        )
        unstable_configuration_principle = diagnostics.get(
            "unstable_configuration_principle",
            False,
        )

        # Local modulation based on optional external parameters.
        modulation = (
            intensity
            * coherence
            * coupling
            * stability
        )

        # Intensity of form-producing dynamics.
        morphogenetic_activity = (
            configuration_instability
            * transformation_potential
            * modulation
        )

        # Degree to which coherent structures emerge.
        structural_emergence = (
            morphogenetic_activity
            * structural_tension
        )

        # Capacity to generate recurrent motifs and organizations.
        pattern_generation = (
            structural_emergence
            * transformation_potential
        )

        # Activation criterion adapted to the very small numerical
        # scales produced by upstream primitives.
        morphogenesis_under_constraints = (
            unstable_configuration_principle
            and morphogenetic_activity > 1e-12
            and structural_emergence > 1e-14
        )

        return {
            "principle": self.PRINCIPLE_NAME,
            "unstable_configuration_principle_diagnostics": diagnostics,
            "morphogenetic_activity": morphogenetic_activity,
            "structural_emergence": structural_emergence,
            "pattern_generation": pattern_generation,
            "morphogenesis_under_constraints": (
                morphogenesis_under_constraints
            ),
        }


if __name__ == "__main__":
    primitive = MorphogenesisUnderConstraintsPrimitive()

    diagnostics = primitive.step()

    print("\n--- morphogenesis under constraints ---")

    for key, value in diagnostics.items():
        print(f"{key}: {value}")