"""Self Parameter Optimization"""

PRIMITIVE = "self_parameter_optimization"

DEPENDENCIES = [
    "persistent_multi_scale_memory",
    "evaluation",
    "monitoring",
    "trajectory_policy_optimization",
    "uncertainty_awareness",
]


class SelfParameterOptimization:
    def __init__(self):
        self.parameters = {}
        self.best_score = None
        self.history = []

    def evaluate(self, parameters, score):
        entry = {
            "parameters": dict(parameters),
            "score": float(score),
        }
        self.history.append(entry)

        if self.best_score is None or score > self.best_score:
            self.best_score = float(score)
            self.parameters = dict(parameters)
            return True
        return False

    def current_parameters(self):
        return dict(self.parameters)

    def diagnostics(self):
        return {
            "primitive": PRIMITIVE,
            "evaluations": len(self.history),
            "best_score": self.best_score,
            "parameter_count": len(self.parameters),
        }
