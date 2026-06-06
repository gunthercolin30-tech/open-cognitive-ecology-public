'''
INTERNAL_CONFLICT_MONITORING.

Detection and prioritization of contradictions among goals,
constraints, beliefs, and control policies.
'''

PRIMITIVE = "internal_conflict_monitoring"

DESCRIPTION = (
    "Monitoring of internal contradictions and their cognitive " \
    "significance."
)

DEPENDENCIES = [
    "goal_conflict_detection",
    "constraint_conflict_detection",
    "belief_revision",
    "meta_cognition",
    "introspective_reporting",
]

OUTPUTS = [
    "conflict_map",
    "conflict_priority_ranking",
    "conflict_intensity_score",
]


class InternalConflictMonitoring:
    """Auto-generated activation class for internal_conflict_monitoring."""

    PRIMITIVE = "internal_conflict_monitoring"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

