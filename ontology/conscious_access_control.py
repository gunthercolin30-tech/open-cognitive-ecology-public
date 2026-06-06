'''
CONSCIOUS_ACCESS_CONTROL.

Selection and gating of contents allowed to enter the global
workspace and become globally available.
'''

PRIMITIVE = "conscious_access_control"

DESCRIPTION = (
    "Controlled access of salient contents to the global workspace."
)

DEPENDENCIES = [
    "global_workspace",
    "attention_allocation",
    "global_self_broadcast",
    "salience_engine",
    "uncertainty_awareness",
]

OUTPUTS = [
    "workspace_access_decision",
    "content_priority_ranking",
    "broadcast_gate_signal",
]


class ConsciousAccessControl:
    """Auto-generated activation class for conscious_access_control."""

    PRIMITIVE = "conscious_access_control"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

