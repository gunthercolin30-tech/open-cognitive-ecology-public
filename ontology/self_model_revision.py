'''
SELF_MODEL_REVISION.

Explicit revision of the self-model based on autobiographical
experience, conscious decision traces, and reflective policy
adjustments.
'''

PRIMITIVE = "self_model_revision"

DESCRIPTION = (
    "Reflective updating of the internal self-model."
)

DEPENDENCIES = [
    "self_model",
    "autobiographical_memory",
    "conscious_decision_trace",
    "reflective_policy_adjustment",
    "introspective_reporting",
]

OUTPUTS = [
    "revised_self_model",
    "revision_justification",
    "identity_update_record",
]


class SelfModelRevision:
    def __init__(self):
        self._revisions = []

    def revise(
        self,
        changes,
        justification="",
        confidence=None,
        source_evidence=None,
    ):
        record = {
            "changes": dict(changes),
            "justification": justification,
            "confidence": confidence,
            "source_evidence": list(source_evidence or []),
        }
        self._revisions.append(record)
        return record

    def latest(self):
        if not self._revisions:
            return None
        return self._revisions[-1]

    def all_revisions(self):
        return list(self._revisions)

    def summarize(self):
        latest = self.latest()
        if latest is None:
            return {
                "available": False,
                "revision_count": 0,
            }

        return {
            "available": True,
            "revision_count": len(self._revisions),
            "changed_fields": sorted(latest["changes"].keys()),
            "confidence": latest["confidence"],
        }
