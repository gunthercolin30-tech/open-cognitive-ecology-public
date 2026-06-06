'''
GLOBAL_EXPERIENCE_EVALUATION.

Global assessment of the coherence, stability, and quality of
the integrated experiential state.
'''

PRIMITIVE = "global_experience_evaluation"

DESCRIPTION = (
    "Integrated evaluation of the overall experiential state."
)

DEPENDENCIES = [
    "experiential_stream_integration",
    "subjective_state_synthesis",
    "internal_conflict_monitoring",
    "uncertainty_awareness",
    "global_temporal_binding",
    "self_model_revision",
]

OUTPUTS = [
    "global_experience_score",
    "coherence_index",
    "stability_index",
    "experience_evaluation_report",
]


class GlobalExperienceEvaluation:
    def evaluate(
        self,
        coherence=0.0,
        stability=0.0,
        uncertainty=1.0,
        conflict=1.0,
        continuity=0.0,
    ):
        score = (
            coherence
            + stability
            + continuity
            + (1.0 - uncertainty)
            + (1.0 - conflict)
        ) / 5.0

        return {
            "global_experience_score": score,
            "coherence_index": coherence,
            "stability_index": stability,
            "continuity_index": continuity,
            "uncertainty_index": uncertainty,
            "conflict_index": conflict,
        }
