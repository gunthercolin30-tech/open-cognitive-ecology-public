'''
CONSCIOUSNESS_EXPERIMENT_RUNNER.

Experimental orchestrator for running repeated conscious cycles,
collecting metrics, and generating structured reports.
'''

PRIMITIVE = "consciousness_experiment_runner"

DESCRIPTION = (
    "Experimental runner for evaluating conscious processing."
)

DEPENDENCIES = [
    "autonomous_conscious_cycle",
    "consciousness_readiness_index",
    "global_experience_evaluation",
    "introspective_reporting",
    "autobiographical_memory",
]

OUTPUTS = [
    "experiment_report",
    "cycle_metrics",
    "summary_statistics",
]


class ConsciousnessExperimentRunner:
    def run(self, scores=None):
        scores = list(scores or [1.0])

        cycle_metrics = []
        for index, score in enumerate(scores):
            cycle_metrics.append({
                "cycle_index": index,
                "global_experience_score": score,
                "needs_regulation": score < 0.8,
            })

        average_score = sum(scores) / len(scores)

        return {
            "cycles": len(scores),
            "average_global_experience_score": average_score,
            "cycle_metrics": cycle_metrics,
            "experiment_status": "completed",
        }
