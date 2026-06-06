from __future__ import annotations


PRIMITIVE = "non_closure"
DESCRIPTION = "Non closure."
DEPENDENCIES = []

"""
ontology/non_closure.py

Computational implementation of the ontological primitive NON_CLOSURE.

This module formalizes the principle that no system can reach complete and
final closure. Whenever coherence, redundancy, and predictability become too
high, the primitive detects excessive saturation and injects a controlled
perturbation that preserves an irreducible degree of openness.

The primitive can be used in cognitive, symbolic, ecological, and distributed
constraint-based systems.

Theoretical references
----------------------
- Colin Gunther, Architecture de la non-clôture.
- Colin Gunther, The Impossibility of Global Closure.
"""


from typing import Dict, Any


PRIMITIVE_NAME = "NON_CLOSURE"
MATURITY_LEVEL = "FOUNDATIONAL_COMPLETE"


def clamp(
    value: float,
    min_value: float = 0.0,
    max_value: float = 1.0,
) -> float:
    """
    Clamp a numeric value between two bounds.
    """
    if min_value > max_value:
        min_value, max_value = max_value, min_value
    return max(min_value, min(max_value, float(value)))


class NonClosurePrimitive:
    """
    Ontological primitive preserving irreducible openness.

    This primitive encodes the impossibility of complete closure.
    Any highly saturated system is forced to maintain a residual
    openness, and can be perturbed if closure pressure becomes excessive.
    """

    primitive_name = PRIMITIVE_NAME
    maturity_level = MATURITY_LEVEL

    def __init__(
        self,
        weight: float = 1.0,
        drift: float = 0.05,
        stability: float = 0.95,
        minimum_openness: float = 0.05,
        closure_threshold: float = 0.90,
        perturbation_scale: float = 0.10,
    ) -> None:
        self.weight = max(0.0, float(weight))
        self.drift = float(drift)
        self.stability = clamp(float(stability))
        self.minimum_openness = clamp(
            float(minimum_openness),
            1e-12,
            1.0,
        )
        self.closure_threshold = clamp(
            float(closure_threshold),
            0.0,
            0.999999,
        )
        self.perturbation_scale = max(
            0.0,
            float(perturbation_scale),
        )

    # ---------------------------------------------------------------------
    # Core computations
    # ---------------------------------------------------------------------

    def compute_saturation(
        self,
        coherence: float,
        redundancy: float,
        predictability: float,
    ) -> float:
        """
        Compute system saturation in [0, 1].
        """
        c = clamp(coherence)
        r = clamp(redundancy)
        p = clamp(predictability)

        base = (c + r + p) / 3.0
        adjusted = base * self.weight + self.drift

        return clamp(adjusted)

    def openness(
        self,
        coherence: float,
        redundancy: float,
        predictability: float,
    ) -> float:
        """
        Compute residual openness.
        """
        saturation = self.compute_saturation(
            coherence,
            redundancy,
            predictability,
        )
        return max(self.minimum_openness, 1.0 - saturation)

    def closure_risk(
        self,
        coherence: float,
        redundancy: float,
        predictability: float,
    ) -> float:
        """
        Compute normalized closure risk.
        """
        saturation = self.compute_saturation(
            coherence,
            redundancy,
            predictability,
        )

        if saturation <= self.closure_threshold:
            return 0.0

        denominator = max(
            1e-12,
            1.0 - self.closure_threshold,
        )

        risk = (
            saturation - self.closure_threshold
        ) / denominator

        return clamp(risk)

    def should_perturb(
        self,
        coherence: float,
        redundancy: float,
        predictability: float,
    ) -> bool:
        """
        Determine whether perturbation is required.
        """
        saturation = self.compute_saturation(
            coherence,
            redundancy,
            predictability,
        )
        return saturation > self.closure_threshold

    def perturbation(
        self,
        coherence: float,
        redundancy: float,
        predictability: float,
    ) -> float:
        """
        Compute perturbation intensity.
        """
        risk = self.closure_risk(
            coherence,
            redundancy,
            predictability,
        )

        attenuation = 1.0 - self.stability

        return max(
            0.0,
            risk * self.perturbation_scale * attenuation,
        )

    # ---------------------------------------------------------------------
    # Simulation API
    # ---------------------------------------------------------------------

    def step(
        self,
        coherence: float = 0.96,
        redundancy: float = 0.93,
        predictability: float = 0.98,
    ) -> Dict[str, float | bool]:
        """
        Evaluate the primitive for a given state.
        """
        saturation = self.compute_saturation(
            coherence,
            redundancy,
            predictability,
        )

        openness = self.openness(
            coherence,
            redundancy,
            predictability,
        )

        risk = self.closure_risk(
            coherence,
            redundancy,
            predictability,
        )

        should = self.should_perturb(
            coherence,
            redundancy,
            predictability,
        )

        perturbation = self.perturbation(
            coherence,
            redundancy,
            predictability,
        )

        return {
            "saturation": saturation,
            "openness": openness,
            "closure_risk": risk,
            "should_perturb": should,
            "perturbation": perturbation,
        }

    # ---------------------------------------------------------------------
    # Scientific validation API
    # ---------------------------------------------------------------------

    def validate(self) -> Dict[str, Any]:
        """
        Scientific validation entry point.

        Returns
        -------
        dict
            Standard validation structure.
        """
        result = self.step()

        saturation = result["saturation"]
        openness = result["openness"]
        closure_risk = result["closure_risk"]

        non_closure_preserved = (
            openness >= self.minimum_openness
        )

        perturbation_available = (
            self.perturbation_scale > 0.0
        )

        valid = (
            0.0 <= saturation <= 1.0
            and 0.0 <= closure_risk <= 1.0
            and non_closure_preserved
            and perturbation_available
        )

        diagnostics = {
            "primitive": PRIMITIVE_NAME,
            "maturity_level": MATURITY_LEVEL,
            "saturation": saturation,
            "openness": openness,
            "minimum_openness": self.minimum_openness,
            "closure_threshold": self.closure_threshold,
            "closure_risk": closure_risk,
            "should_perturb": result["should_perturb"],
            "perturbation": result["perturbation"],
            "non_closure_preserved": non_closure_preserved,
            "perturbation_available": perturbation_available,
            "status": (
                "irreducible openness preserved"
                if valid
                else "closure failure"
            ),
        }

        return {
            "valid": valid,
            "in_viability_domain": valid,
            "configuration_size": 1,
            "diagnostics": diagnostics,
        }


if __name__ == "__main__":
    primitive = NonClosurePrimitive()

    result = primitive.validate()

    print("NON_CLOSURE validation")
    print("-" * 60)
    print(f"Valid: {result['valid']}")
    print(f"Maturity: {MATURITY_LEVEL}")
    print()

    for key, value in result["diagnostics"].items():
        print(f"{key:24s}: {value}")
