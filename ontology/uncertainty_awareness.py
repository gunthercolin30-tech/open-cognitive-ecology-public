'''
UNCERTAINTY_AWARENESS.

Explicit representation of uncertainty, confidence, and
recognized limits of current knowledge and inference.
'''

PRIMITIVE = "uncertainty_awareness"

DESCRIPTION = (
    "Explicit awareness of uncertainty and confidence levels."
)

DEPENDENCIES = [
    "meta_cognition",
    "introspective_reporting",
    "belief_revision",
    "internal_conflict_monitoring",
]

OUTPUTS = [
    "uncertainty_profile",
    "confidence_estimate",
    "known_unknowns",
]


class UncertaintyAwareness:
    """Auto-generated activation class for uncertainty_awareness."""

    PRIMITIVE = "uncertainty_awareness"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

