'''
GLOBAL_SELF_BROADCAST.

Broadcast of the integrated self-state across the cognitive
architecture through the global workspace.
'''

PRIMITIVE = "global_self_broadcast"

DESCRIPTION = (
    "Global dissemination of the current integrated self-state."
)

DEPENDENCIES = [
    "subjective_state_synthesis",
    "global_workspace",
    "attention_allocation",
    "introspective_reporting",
]

OUTPUTS = [
    "broadcast_self_state",
    "globally_available_identity_context",
    "self_state_access_signal",
]


class GlobalSelfBroadcast:
    """Auto-generated activation class for global_self_broadcast."""

    PRIMITIVE = "global_self_broadcast"

    def diagnostics(self):
        return {
            "primitive": self.PRIMITIVE,
            "status": "active",
        }

