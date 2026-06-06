PRIMITIVE = "non_representability"
DESCRIPTION = "Non representability."
DEPENDENCIES = []

# ontology/non_representability.py

"""
NON_REPRESENTABILITY Primitive
==============================

Fundamental ontological primitive implementing the principle that no
internal representation can fully capture the structure of the world.

This implementation preserves the existing scientific logic based on
residual complexity while adding the standardized ontology metadata
and validation interface required by the open-cognitive-ecology corpus.

Theoretical foundation:
    Colin Gunther, Theory of Non-Representability
    DOI: 10.5281/zenodo.19692733
"""


class NonRepresentabilityPrimitive:
    """
    Fundamental ontological primitive implementing the principle
    that no internal representation can fully capture the structure
    of the world.

    This primitive estimates the irreducible residual between the
    modeled complexity and the effective complexity encountered by
    a system. The residual acts as a structural source of opacity,
    innovation pressure, and instability of totalizing models.
    """

    PRIMITIVE_NAME = "NON_REPRESENTABILITY"
    MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"

    def __init__(
        self,
        residual_floor=0.05,
        instability_gain=1.0,
    ):
        self.residual_floor = max(
            0.0,
            float(residual_floor),
        )
        self.instability_gain = max(
            0.0,
            float(instability_gain),
        )

    # ------------------------------------------------------------------
    # Core scientific measures
    # ------------------------------------------------------------------

    def representability_gap(
        self,
        model_complexity=1.0,
        world_complexity=1.2,
        compression_ratio=1.0,
    ):
        """
        Return the raw complexity gap between world complexity and
        represented complexity.

        Positive values indicate that part of the world remains
        structurally unrepresented.
        """
        model_complexity = max(
            0.0,
            float(model_complexity),
        )

        world_complexity = max(
            0.0,
            float(world_complexity),
        )

        compression_ratio = max(
            0.0,
            float(compression_ratio),
        )

        represented_complexity = (
            model_complexity * compression_ratio
        )

        return (
            world_complexity - represented_complexity
        )

    def irreducible_remainder(
        self,
        model_complexity=1.0,
        world_complexity=1.2,
        compression_ratio=1.0,
    ):
        """
        Return the irreducible residual that cannot be eliminated.

        Even if the model matches the world exactly, a minimum residual
        remains, represented by residual_floor.
        """
        complexity_gap = self.representability_gap(
            model_complexity=model_complexity,
            world_complexity=world_complexity,
            compression_ratio=compression_ratio,
        )

        return max(
            self.residual_floor,
            complexity_gap,
        )

    # ------------------------------------------------------------------
    # Primitive interface
    # ------------------------------------------------------------------

    def step(
        self,
        model_complexity=1.0,
        world_complexity=1.2,
        compression_ratio=1.0,
    ):
        """
        Compute the residual complexity that escapes representation.

        Compatible with the global corpus simulation engine, which may
        invoke primitive.step() without arguments.
        """
        complexity_gap = self.representability_gap(
            model_complexity=model_complexity,
            world_complexity=world_complexity,
            compression_ratio=compression_ratio,
        )

        residual = self.irreducible_remainder(
            model_complexity=model_complexity,
            world_complexity=world_complexity,
            compression_ratio=compression_ratio,
        )

        opacity = residual

        innovation_pressure = (
            self.instability_gain * residual
        )

        representational_stability = (
            1.0 / (1.0 + innovation_pressure)
        )

        modulated_activation = (
            1.0 + innovation_pressure
        )

        return {
            "complexity_gap": complexity_gap,
            "representability_gap": complexity_gap,
            "residual": residual,
            "irreducible_remainder": residual,
            "opacity": opacity,
            "innovation_pressure": innovation_pressure,
            "representational_stability": (
                representational_stability
            ),
            "modulated_activation": (
                modulated_activation
            ),
        }

    def validate(
        self,
        model_complexity=1.0,
        world_complexity=1.2,
        compression_ratio=1.0,
    ):
        """
        Validation interface compatible with validation.main.

        The primitive is valid when an irreducible residual strictly
        greater than zero is present, which is guaranteed by the
        residual floor.
        """
        result = self.step(
            model_complexity=model_complexity,
            world_complexity=world_complexity,
            compression_ratio=compression_ratio,
        )

        residual = result["residual"]
        valid = residual > 0.0

        return {
            "valid": valid,
            "in_viability_domain": valid,
            "configuration_size": 1,
            "diagnostics": {
                "primitive": self.PRIMITIVE_NAME,
                "maturity_level": self.MATURITY_LEVEL,
                "residual_floor": self.residual_floor,
                "complexity_gap": result[
                    "complexity_gap"
                ],
                "residual": residual,
                "opacity": result["opacity"],
                "innovation_pressure": result[
                    "innovation_pressure"
                ],
                "status": (
                    "non_representable"
                    if valid
                    else "representable"
                ),
            },
        }


if __name__ == "__main__":
    primitive = NonRepresentabilityPrimitive()

    result = primitive.step(
        model_complexity=1.0,
        world_complexity=1.2,
        compression_ratio=1.0,
    )

    print("NON_REPRESENTABILITY evaluation")
    print("-" * 40)

    for key, value in result.items():
        print(f"{key:28s}: {value}")

    print("\nValidation")
    print("-" * 40)
    print(primitive.validate())