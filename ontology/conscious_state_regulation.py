'''
CONSCIOUS_STATE_REGULATION.

Active regulation of the global cognitive state based on
integrated experience evaluation and reflective control.
'''

PRIMITIVE = "conscious_state_regulation"

DESCRIPTION = (
    "Reflective regulation of the global cognitive state."
)

DEPENDENCIES = [
    "global_experience_evaluation",
    "subjective_state_synthesis",
    "attention_allocation",
    "reflective_policy_adjustment",
    "homeostatic_regulation",
]

OUTPUTS = [
    "state_regulation_action",
    "regulation_targets",
    "updated_state_parameters",
]


class ConsciousStateRegulation:
    def regulate(
        self,
        global_experience_score,
        target_threshold=0.8,
    ):
        needs_regulation = (
            global_experience_score < target_threshold
        )

        return {
            "needs_regulation": needs_regulation,
            "global_experience_score": global_experience_score,
            "target_threshold": target_threshold,
            "regulation_intensity": max(
                0.0,
                target_threshold - global_experience_score,
            ),
        }
