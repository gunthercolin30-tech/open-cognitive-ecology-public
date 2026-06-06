"""
OPEN_ENDED_CAPABILITY_EVOLUTION

Continuously accumulates proposed capabilities and selects the next
highest-priority capability to sustain open-ended architectural growth.
"""

from typing import Any, Dict, List, Optional


class OpenEndedCapabilityEvolution:
    primitive_name = "OPEN_ENDED_CAPABILITY_EVOLUTION"

    def __init__(self) -> None:
        self.capability_backlog = []

    def step(
        self,
        discovered_capabilities: Optional[List[str]] = None,
        governance_approved: bool = True,
    ) -> Dict[str, Any]:
        discovered_capabilities = discovered_capabilities or []

        if governance_approved:
            for capability in discovered_capabilities:
                if capability not in self.capability_backlog:
                    self.capability_backlog.append(capability)

        next_priority = (
            self.capability_backlog[0]
            if self.capability_backlog
            else None
        )

        return {
            "primitive": self.primitive_name,
            "governance_approved": governance_approved,
            "backlog_size": len(self.capability_backlog),
            "capability_backlog": list(self.capability_backlog),
            "next_priority_capability": next_priority,
            "open_ended_growth_active": next_priority is not None,
        }


__all__ = ["OpenEndedCapabilityEvolution"]
