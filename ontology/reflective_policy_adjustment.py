'''
REFLECTIVE_POLICY_ADJUSTMENT.

Explicit modification of internal control policies based on
conscious decision traces, uncertainty estimates, and
metacognitive evaluation.
'''

PRIMITIVE = "reflective_policy_adjustment"

DESCRIPTION = (
    "Reflective adjustment of internal control policies."
)

DEPENDENCIES = [
    "conscious_decision_trace",
    "self_confidence_calibration",
    "uncertainty_awareness",
    "meta_cognition",
    "trajectory_policy_update",
]

OUTPUTS = [
    "policy_adjustment",
    "adjustment_justification",
    "updated_control_parameters",
]


class ReflectivePolicyAdjustment:
    def __init__(self):
        self._adjustments = []

    def adjust(
        self,
        target_policy,
        adjustment,
        justification="",
        confidence=None,
        uncertainty=None,
    ):
        record = {
            "target_policy": target_policy,
            "adjustment": adjustment,
            "justification": justification,
            "confidence": confidence,
            "uncertainty": uncertainty,
        }
        self._adjustments.append(record)
        return record

    def latest(self):
        if not self._adjustments:
            return None
        return self._adjustments[-1]

    def all_adjustments(self):
        return list(self._adjustments)

    def summarize(self):
        latest = self.latest()
        if latest is None:
            return {
                "available": False,
                "adjustment_count": 0,
            }

        return {
            "available": True,
            "adjustment_count": len(self._adjustments),
            "target_policy": latest["target_policy"],
            "confidence": latest["confidence"],
            "uncertainty": latest["uncertainty"],
        }
