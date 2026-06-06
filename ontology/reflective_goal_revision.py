'''
REFLECTIVE_GOAL_REVISION.

Explicit revision of goals based on identity, temporal coherence,
internal conflicts, and current subjective state.
'''

PRIMITIVE = "reflective_goal_revision"

DESCRIPTION = (
    "Reflective revision of goals in light of self-state and temporal context."
)

DEPENDENCIES = [
    "global_temporal_binding",
    "internal_conflict_monitoring",
    "uncertainty_awareness",
    "subjective_state_synthesis",
    "goal_management",
]

OUTPUTS = [
    "revised_goal_set",
    "goal_revision_justification",
    "goal_priority_update",
]


class ReflectiveGoalRevision:
    """Auto-generated activation class for reflective_goal_revision."""

    PRIMITIVE = "reflective_goal_revision"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

