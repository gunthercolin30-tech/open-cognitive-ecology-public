'''
CONSCIOUS_DECISION_TRACE.

Explicit and reportable trace of conscious decisions, including
justification, alternatives, uncertainties, and anticipated
consequences.
'''

PRIMITIVE = "conscious_decision_trace"

DESCRIPTION = (
    "Structured trace of decisions accessible to introspection."
)

DEPENDENCIES = [
    "reflective_goal_revision",
    "subjective_state_synthesis",
    "global_self_broadcast",
    "global_temporal_binding",
    "decision_making",
    "introspective_reporting",
]

OUTPUTS = [
    "decision_trace",
    "decision_justification",
    "considered_alternatives",
    "anticipated_consequences",
]


class ConsciousDecisionTrace:
    def __init__(self):
        self._traces = []

    def record(
        self,
        decision,
        justification="",
        alternatives=None,
        uncertainties=None,
        conflicts=None,
        goals=None,
        anticipated_consequences=None,
        subjective_state=None,
    ):
        trace = {
            "decision": decision,
            "justification": justification,
            "alternatives": list(alternatives or []),
            "uncertainties": list(uncertainties or []),
            "conflicts": list(conflicts or []),
            "goals": list(goals or []),
            "anticipated_consequences": list(anticipated_consequences or []),
            "subjective_state": dict(subjective_state or {}),
        }
        self._traces.append(trace)
        return trace

    def latest(self):
        if not self._traces:
            return None
        return self._traces[-1]

    def all_traces(self):
        return list(self._traces)

    def summarize(self):
        trace = self.latest()
        if trace is None:
            return {
                "available": False,
                "trace_count": 0,
            }

        return {
            "available": True,
            "trace_count": len(self._traces),
            "decision": trace["decision"],
            "justification": trace["justification"],
            "alternatives_count": len(trace["alternatives"]),
            "uncertainties_count": len(trace["uncertainties"]),
            "conflicts_count": len(trace["conflicts"]),
        }
