'''
INTROSPECTIVE_REPORTING.

Generation of explicit reports describing current internal
states, uncertainties, conflicts, and operational limits.
'''

PRIMITIVE = "introspective_reporting"

DESCRIPTION = (
    "Explicit introspective reports about current cognitive " \
    "states and limitations."
)

DEPENDENCIES = [
    "self_narrative_generation",
    "meta_cognition",
    "report_generation",
    "self_model",
    "consciousness_readiness_index",
]

OUTPUTS = [
    "introspective_report",
    "uncertainty_statement",
    "conflict_statement",
    "operational_limit_statement",
]


class IntrospectiveReporting:
    """Auto-generated activation class for introspective_reporting."""

    PRIMITIVE = "introspective_reporting"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

